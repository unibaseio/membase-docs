---
title: "Platform overview"
description: "The hosted Membase at app.membase.com as your code meets it: the nouns, what each screen of the app is to the API, credentials, one account per person, limits, the Marketplace, and what can be undone."
---

The hosted Membase at app.membase.com as your code meets it: the nouns, what each screen of the app is to the API, credentials, one account per person, limits, the Marketplace, and what can be undone.

The Memory Platform is the hosted Membase at `https://app.membase.com`. A person hands it
material once; it keeps a living memory of that material; every AI they connect, and every
key they mint, reads the same memory. The mechanism is on
[How Membase works](/build/concepts/how-membase-works/); this page is the product around it, written for
someone whose code will meet what the person sees. The screens themselves, one page each,
are in the **Use Membase** tab.

## The nouns

| API | In the app | What it is |
|---|---|---|
| **Memory** (`memory_name` in answers) | a *Memory* | one named space of memory, with the agent that keeps it and the material it reads. Named in answers, never addressed in a request |
| **memory** (`mem_…`) | an item on a Memory's page | one fact a Memory learned |
| **document** (`doc_…`) | a row under a Memory's sources | one piece of material handed in: a file or a page (`kind: file`), or a fact as it was said (`kind: note`) |
| **media** (`med_…`) | a photo or video in a media Memory | what was seen or said in it, with its moments |

![One account holds Memories; each Memory holds documents that a run turns into memories; the profile sits beside them](/images/figures/three-nouns.svg)

Plain verbs: `list`, `search`, `get`, `add`, `delete`, `forget`, `ask`.
[Memory operations](/build/guides/memory-operations/) walks them; the [API reference](/build/reference/api-reference/)
has every operation.

A **profile** sits beside the Memories: the standing facts the assistant keeps about the
user (`static`) and the most recently changed ones (`dynamic`). `get_profile` reads it.

A credential reads every Memory it reaches; a write lands in the one text Memory it reaches,
and a credential that reaches several is refused with `422 write_target_required`.

## The screens

| Screen | The person uses it to | Your code meets it as |
|---|---|---|
| [Home](/use/use-your-assistant/home/) | talk to the assistant, the one agent that is theirs by default; reach it on Telegram | the profile it keeps; the assistant's own memory is not a Memory here |
| [Memory](/use/manage-your-memory/memory/) | make, run and inspect Memories | `search_memories`, `list_memories`, `get_memory`, the facts `forget_memory` removes; a document's `learning` turning `succeeded` after a run |
| [Files](/use/bring-your-material-in/files/) | keep files, and hand folders, uploads, Notion pages and captured conversations to a Memory | `add_document`, `list_documents`, `get_document`, `delete_document` |
| [Studio](/use/advanced/studio/) | edit a Memory's pipeline canvas | nothing; a canvas run as an endpoint is `workflow_invoke` over MCP |
| [Agents](/use/advanced/agents/) | build agents beyond the assistant | `ask_agent` on an agent-endpoint credential |
| [Schedules](/use/automate-and-troubleshoot/schedules/) | run Memories on a cadence | a document's `learning` turning `succeeded` without a call of yours |
| [Activity](/use/automate-and-troubleshoot/activity/) | see what ran | the run a `202` from `add_document` started; a key's own calls are on the key's page |
| [AI Setup](/use/account-and-models/ai-setup/) | choose the account's model | `422 · capability_unavailable` when there is none |
| [Connect](/use/manage-your-memory/connect/) | let an AI app read Memories, mint keys | consent tokens and developer keys: [Authentication & Scopes](/build/reference/authentication/) |
| [Marketplace](/use/share-and-trade/marketplace/) | sell and buy access to a Memory | subscriptions, `ask_agent` |
| [Settings](/use/account-and-models/settings/) | plan, export, delete | `422 · capability_unavailable` with `details.reason: "dormant"` on a free plan whose turns are spent |

## Credentials

Every call carries a bearer: a **developer key** the owner minted, or a **consent token** an
app received on the OAuth consent screen. A key has a level (Read, Read & write, Full
access), a reach (the Memories it may use) and an expiry; a consent token is read-only and
reaches what the user ticked. Both are managed by the account owner in **Connect**. [Authentication & Scopes](/build/reference/authentication/) has the whole model; the keys
screen is under [Connect](/use/manage-your-memory/connect/#developer-keys) in the user guide.

A key's calls are on the key's page, not on Activity: **Usage** (calls in the last 30 or 7
days, how many were *refused*, the tool it calls most) and **Recent activity** (each call:
tool, Memory, what came back, when; a refused call in red with the reason). The same numbers
are on `GET /v1/api-keys/{id}/usage` with the owner's session.

## One account per person

The account is the tenant. A Memory is a topic, not an end user. A product that serves
many people gives each of them their own Membase account, and reads their memory with their
own key or their own consent; there are no application-wide keys and no sub-tenant tags.
[Multi-user isolation](/build/guides/multi-user-isolation/) has the patterns.

## Models

Every learning turn, every search and every assistant answer needs a model. The account
chooses it under AI Setup: a key of its own for a provider, or a Claude or ChatGPT
subscription. Follow the connection and verification steps shown in **AI Setup**. An account with no working model keeps
its stored memory, but learning and hosted search need working agent turns. A search may
name the Memories that could not answer in `partial`; documents can remain unread.
[How Membase works](/build/concepts/how-membase-works/#models).

## Limits and errors

Search and every list name the Memories that could not answer in `partial` on an HTTP
`200`. Check that field before treating an empty result as “nothing found.” [API troubleshooting](/build/reference/troubleshooting/)
covers partial failures, deferred learning and timeouts.

| Status | Code | When |
|---|---|---|
| 400 | `validation` | an empty `q`, both or neither of `content` and `url`, a `limit` out of range |
| 401 | `unauthenticated` | no bearer token on the request |
| 403 | `unauthorized` | an invalid, expired or revoked key, or a verb above its level |
| 404 | `not_found` | an id that is not this credential's to read: outside its reach, deleted, or not one of ours |
| 422 | `validation` | a missing, mistyped or unknown body field (`container` included); read `code` to tell it from the rows below |
| 422 | `write_target_required` | a write from a credential that reaches several Memories |
| 428 | `confirmation_required` | a delete or forget without `confirm=true`; nothing changed |
| 422 | `capability_unavailable` | the account's memory cannot run a turn here (no agent container, no model) |
| 422 | `capability_unavailable` | with `details.reason: "dormant"`: a free-plan account whose free turns are spent |
| 429 | `rate_limited` | the account's concurrent-turn budget, or the token's per-minute request limit; retry later |

Uploads through `add_document` are capped at 32 MiB per file, on every plan. An account on
the free plan whose free turns are spent keeps its memory but cannot run turns until it
brings a model of its own under AI Setup or moves to a paid plan.

## Marketplace

A listing is an agent endpoint (or a workflow endpoint): the buyer's credential calls
`ask_agent` (or `workflow_invoke`) and gets answers, never files. The earlier snapshot and
live-memory listing kinds were retired and can no longer be created; a few pre-existing ones
may still render for their buyers. Check the listing's **Included access** section.
[Marketplace](/use/share-and-trade/marketplace/).

## Stopping and undoing

Revoking a key or disconnecting an app changes subsequent access. It does not erase content
already received by the client. Pausing a schedule stops future scheduled runs; subscription
changes follow the terms and dates shown for that purchase or plan.

Deleting a Memory removes its stored content. Deleting a conversation removes the transcript
but retains information already saved to memory. Deleting account data retains the sign-in
identity. Review the confirmation and export data you want to keep before deleting.
[Concepts](/concepts/#stopping-and-undoing).
