---
title: "API troubleshooting"
description: "Diagnose API authentication errors, unread documents, partial search failures, model availability and timeouts."
---

Diagnose API authentication errors, unread documents, partial search failures, model availability and timeouts.

Start with the HTTP status and response body. For searches, also inspect `containers[]`:
a `200` response can contain errors for individual Memories alongside successful results.

## A document was accepted but search cannot find it

`202` means accepted, not learned. Poll `GET /v1/documents/{id}` until `learned` is true.
If the initial `document_id` is null, the source sync may still be creating its row. Wait
and list documents in that container; identify the uploaded file using the returned `path`
and the source listing in the app. Do not pick an arbitrary first row. A delayed row may
not yet carry your `custom_id` or custom title. The list gives you the id; the detail
endpoint gives you `learned`.

Inspect `learning_run.status` and the Memory's **Report** in the app. A failed or canceled
run requires attention; a deferred run may need **Update now** after capacity becomes
available. Adding the same `custom_id` again is a no-op and does not force a new learning run.
The [quickstart](/build/getting-started/api-quickstart/) includes bounded polling and failure handling.

## Search returns no results

1. Inspect `containers[].error`. If present, that Memory could not run a turn (no model,
   dormant, no agent container); do not treat it as proof that no relevant memory exists. Fix
   the model or run error before retrying. Any other failure inside one Memory fails the whole
   request instead of landing here.
2. Use `list_containers` to check reach. Without a `container`, search considers only Memories
   the key reaches. An explicitly requested container outside that reach is refused with `403`.
3. Check that the document is learned, then inspect the Memory in the app and try a question
   that names something specific from the source.

Search runs an agent turn in the hosted service and needs a working model. Stored content
is retained when a model is unavailable, but that does not make hosted search model-free.

## Authentication and access errors

| Response | Meaning | Next step |
|---|---|---|
| `401` | On REST: no bearer credential was supplied. On `/mcp-http` a missing and an invalid or revoked bearer both answer `401`, with `WWW-Authenticate: Bearer error="invalid_token"` and an RFC 6750 `{"error": "invalid_token", …}` body. | Check the Authorization header or `MEMBASE_API_KEY`; over MCP, also that the token is still valid. |
| `403 · unauthorized` | The token is invalid, expired or revoked, or the requested access is outside its grant. | Read the error and inspect the key in Connect. |
| `403 · may not use that container` | The container is absent or outside the key's reach. | List containers and check Reach on the key. |
| `403 · not in this agent's capability profile` | The operation is not granted to this credential. | Have the owner adjust the access level if appropriate. |
| `status: confirmation_required` | A destructive call has not been confirmed. | Ask the owner before calling with `confirm=true`; the key still needs Full access. |

A `403` is the API's refusal convention; it does not prove that the supplied secret was
valid. Do not retry refused requests unchanged. [Authentication](/build/reference/authentication/)
explains the credential model.

## Model, capacity and timeout errors

| Symptom | Next step |
|---|---|
| `400 · validation` or `422 · validation` | `400` is the service's own check: an empty `q`, both or neither of `content` and `url`, `container` omitted when more than one is in reach. `422 · validation` is a missing or mistyped body field. Read `code`, not only the status. |
| `422 · capability_unavailable` or a model-related `containers[].error` | Check AI Setup and the Memory agent's model setting; inspect its Report. |
| An error with `reason: dormant` | The free account needs available turns, its own model, or a paid plan. Follow the account's recovery choices. |
| `429 · rate_limited` | The account already has two agent turns running (`add_memory` with `static`, `forget_memory`, `ask_agent`) or the token exceeded its per-minute limit (`details.limit_per_min`). No `Retry-After` is sent; back off exponentially, as the SDK does. Search does not raise it and `add_document` never does. Do not start a parallel retry loop. |
| Request timeout | The account may be waking or an agent turn may still be running. Inspect the run before resubmitting writes. |

The SDK defaults to 90 seconds per request and retries some transient failures. That is a
client setting, not a promise that every cold request finishes in 90 seconds. Configure
`timeout` in Python or `timeoutMs` in TypeScript for your workload. Use `custom_id` for
retryable document writes; an unkeyed write should not be replayed blindly.

## Can search filter on metadata?

Search accepts a question, an optional container and a limit. `metadata` and `custom_id`
are document bookkeeping fields, not search filters. Put information needed for recall in
the content. See [Memory operations](/build/guides/memory-operations/).

## Can one application key serve all my users?

There is no application-wide credential or sub-tenant tag. Each person's account owns its
memory and grants access through that person's credential. A container is a topic inside
an account, not an end user. See [Multi-user isolation](/build/guides/multi-user-isolation/).
