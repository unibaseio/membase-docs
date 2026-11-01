---
title: "API troubleshooting"
description: "Diagnose API authentication errors, unread documents, partial search failures, model availability and timeouts."
---

Diagnose API authentication errors, unread documents, partial search failures, model availability and timeouts.

Start with the HTTP status and response body. For searches and lists, also inspect
`partial`: a `200` response can name Memories that could not answer alongside the results.

## A document was accepted but search cannot find it

`202` means accepted, not learned. Poll `GET /v1/documents/{id}` until its `learning` status
is `succeeded`. If the receipt's `id` is null, the source sync may still be creating its row:
wait and list the documents. A delayed row may not yet carry your `custom_id` or custom title.

The status says where learning stands: `processing` (a run is reading it now), `pending`
(waiting for the next run, which the one in flight starts when it ends) or `failed`: inspect
the Memory's **Report** in the app. Adding the same `custom_id` again is a no-op and does not
force a new learning run.
The [quickstart](/build/getting-started/api-quickstart/) includes bounded polling and failure handling.

## Search returns no results

1. Inspect `partial`. A Memory named there could not answer (no model, dormant, unreachable)
   or lost every passage to `limit`; do not treat it as proof that no relevant memory exists.
   Fix the model or run error before retrying.
2. Check reach: `GET /v1/capabilities` names the Memories the key reaches (`memories`). Search
   considers only those.
3. Check that the document is learned, then inspect the Memory in the app and try a question
   that names something specific from the source.

Search runs an agent turn in the hosted service and needs a working model. Stored content
is retained when a model is unavailable, but that does not make hosted search model-free.

## Authentication and access errors

| Response | Meaning | Next step |
|---|---|---|
| `401` | On REST: no bearer credential was supplied. On `/mcp-http`, a missing bearer answers `401` with `WWW-Authenticate: Bearer resource_metadata="…"` and `{"error": "unauthorized", …}`; an invalid, expired or revoked one answers `401` with `WWW-Authenticate: Bearer error="invalid_token", resource_metadata="…"` and `{"error": "invalid_token", …}`. | Check the Authorization header or `MEMBASE_API_KEY`; over MCP, `invalid_token` means the token is no longer valid: authorize again. |
| `403 · unauthorized` | The token is invalid, expired or revoked, or the requested access is outside its grant. | Read the error and inspect the key in Connect. |
| `404 · not_found` on an id | The id is outside the key's reach, deleted, or not one of ours. | Check `memories` in `GET /v1/capabilities` and **Memory access** on the key. |
| `403 · token missing required scope` | A write operation from a read-scoped credential: a **Read** key or an app's consent token. | Create a new key at **Read & write** or above; raising an existing **Read** key does not let it write. Consent tokens never write. |
| `403 · not in this agent's capability profile` | The operation is not granted to this credential, for example a delete or forget from a **Read & write** key. | Have the owner adjust the access level if appropriate. |
| `428 · confirmation_required` | A destructive call has not been confirmed; nothing changed. | Ask the owner before calling with `confirm=true`; the key still needs Full access. |
| `422 · write_target_required` | A write from a key that reaches several Memories. | Use a key that reaches the one Memory writes should go to. |

A `403` is the API's refusal convention; it does not prove that the supplied secret was
valid. Do not retry refused requests unchanged. [Authentication](/build/reference/authentication/)
explains the credential model.

## Model, capacity and timeout errors

| Symptom | Next step |
|---|---|
| `400 · validation` or `422 · validation` | `400` is the service's own check: an empty `q`, both or neither of `content` and `url`, a `limit` out of range. `422 · validation` is a missing, mistyped or unknown body field (a `container` included). Read `code`, not only the status. |
| `422 · capability_unavailable`, or a Memory in `partial` with reason `error` | Check AI Setup and the Memory agent's model setting; inspect its Report. |
| `422 · capability_unavailable` with `details.reason: dormant` (in a search, the Memory is named in `partial` with reason `error`) | The free account needs available turns, its own model, or a paid plan. Follow the account's recovery choices. |
| `429 · rate_limited` | The account already has two agent turns running (`forget_memory`, `ask_agent`), the service is running as many agent turns as it can at once (`details.scope: "process"`), or the token exceeded its per-minute limit (`details.limit_per_min`). The per-minute limit applies to every `/v1` call, search and `add_document` included; only the two-turn limit spares them (`add_document` defers its learning instead). No `Retry-After` is sent; back off exponentially, as the SDK does. Do not start a parallel retry loop. |
| `429 · quota_exceeded` | `add_document` or `add_memory` when the account's storage is full (`details.meter: "storage"`) or its plan is not active (`details.meter: "plan"`). Retrying does not help; free space in Files, get more storage or renew the plan. |
| Request timeout | The account may be waking or an agent turn may still be running. Inspect the run before resubmitting writes. |

The SDK defaults to 90 seconds per request and retries some transient failures. That is a
client setting, not a promise that every cold request finishes in 90 seconds. Configure
`timeout` in Python or `timeoutMs` in TypeScript for your workload. Use `custom_id` for
retryable document writes; an unkeyed write should not be replayed blindly. Both SDKs retry
every request, POSTs included, on a timeout, a connection error, `409`, `429` and `5xx`. For
a write without `custom_id` (`memories.add`, `ask`), turn that off with `max_retries=0` in
Python or `maxRetries: 0` in TypeScript and decide yourself whether to resend.

## Can search filter on metadata?

Search accepts a question, a limit and a mode. `custom_id` is a document bookkeeping field,
not a search filter, and a `metadata` field is refused. Put information needed for recall in
the content. See [Memory operations](/build/guides/memory-operations/).

## Can one application key serve all my users?

There is no application-wide credential or sub-tenant tag. Each person's account owns its
memory and grants access through that person's credential. A Memory is a topic inside an
account, not an end user. See [Multi-user isolation](/build/guides/multi-user-isolation/).
