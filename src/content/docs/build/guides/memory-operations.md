---
title: "Memory operations"
description: "Every verb of the agent protocol end to end: Memories, search, facts, profile facts, documents, media, ask, forget and delete, what a run does to them, and what code sees when the app does something."
---

Every verb of the agent protocol end to end: Memories, search, facts, profile facts, documents, media, ask, forget and delete, what a run does to them, and what code sees when the app does something.

The API has a handful of nouns and verbs. This page walks them in the order a program
meets them, says what each does inside the user's account, and what code sees when the
person, a schedule or the app does something on its side. Every snippet is the Python SDK;
the TypeScript and REST shapes are on the [SDKs](/build/reference/sdk-quickstart/) and the
[API reference](/build/reference/api-reference/).

| Noun | In the app | What it is | Id |
|---|---|---|---|
| **Memory** | a *Memory* | one named space of memory, with the agent that keeps it and the material it reads; `text` or `media`. Named in answers (`memory_name`), never addressed in a request | — |
| **memory** | an item on a Memory's page | one fact a Memory learned | `mem_…` |
| **profile fact** | a line under Settings › Your profile | one standing statement about the person (name, role, a lasting preference); the account's, not a Memory's | `pf_…` |
| **document** | a row under a Memory's sources | one piece of raw material a Memory read: a file or page (`kind: file`), or a fact as it was said (`kind: note`) | `doc_…` |
| **media** | a photo or video in a media Memory | one photo or video, with its moments | `med_…` |

Ids are typed and opaque. An id outside the key's reach, an id of the wrong type and a string
that is not one of ours all answer `404`. Every list is `{items, has_more, partial}`: the newest
`limit` (1–1000, default 100), whether more were left out, and the Memories that could not
answer; there is no paging.

![One account holds Memories; each Memory holds documents that a run turns into memories; the profile sits beside them](/images/figures/three-nouns.svg)

## Memories

```python
caps = client.capabilities()
caps["memories"]          # [{"name": "Project decisions", "kind": "text"}, …]: what the key reaches
caps["actions"]           # ["search", "memories.list", "memories.add", …]: what it may do
```

No request names a Memory. Reads (search, lists, ids) cover every Memory the key reaches;
writes land in the key's **write target**, the one text Memory it reaches. A key that reaches
several text Memories is refused on a write with `422 write_target_required`
(`WriteTargetRequiredError`) and nothing is written somewhere by guess. Sending a `container`
is a `422` too: the API refuses fields it does not know. `capabilities()` names the Memories in
reach by name and kind, never by id; it is not permission, and every call is still checked when
made. A Memory outside the reach cannot be told apart from one that does not exist. The
assistant's own memory is not a Memory here: code meets what it knows about the person as
profile facts.

What a Memory's tile says in the app, and what it means to code:

| Tile word | Meaning | In the API |
|---|---|---|
| *Add a source* | reads nothing yet | in reach, `list_documents` lists nothing from it |
| *On sale* | listed on the Marketplace | buyers hold credentials that `ask_memory` it, and nothing else |
| *Subscribed* | bought from someone else | `ask_memory` only; no passages, no documents, no writes |
| no word | yours, reading at least one source | in reach; searches answer from what its runs learned |

Renaming a Memory changes the `memory_name` answers carry; ids never change. Deleting a
Memory is the owner's, in the app, and has no agent-protocol verb.

## Search

```python
hits = client.search("what did we decide about the ledger", limit=5)
for h in hits["items"]:
    print(h["memory_name"], "·", h["content"])
```

A search covers every Memory in reach at once, and each passage names its Memory
(`memory_name`). Passages come most relevant first: `type: "memory"` is a learned fact and
carries its `mem_` id (read it again with `memories.get(id)`), `type: "document"` is a passage
from a document. `limit` is how many in all (1–50), not per Memory. `partial` names each Memory
that could not answer (`reason: "error"`) or whose passages all lost to `limit`
(`reason: "truncated"`); the others still answered. `mode="fast"` is one round of retrieval
with no model call, for recall before every turn of an agent whose own model judges what it is
handed; the default `full` is the engine's whole retrieval.

A search is a **turn** inside the account's container, not a query on an index. The first one
after a quiet spell includes runtime startup; the SDKs default to 90
seconds per request, which is configurable and is not a latency guarantee. There are no metadata filters, because there is no server-side index to apply
them to: put what matters in the content. Search is retrieval; `ask` is an answer.

A Memory with no learned content may return no results. Check `partial` before interpreting
an empty result: an unavailable model is a failed search, not evidence that no matching memory
exists. Search is not held to the two-turns-at-once limit, but like every call it can answer
`429` when the token exceeds its per-minute request limit.

## Facts

```python
facts = client.memories.list(limit=20)            # the newest facts, newest by when they happened
for f in facts["items"]:
    print(f["id"], f["memory_name"], f["content"], f["source_time"])
client.memories.get("mem_…")                      # one fact, at any age
```

`memories.list` shows the facts the Memories in reach learned, newest by when they happened,
each with its `mem_` id, `memory_name`, `source_time` (when it happened) and `recorded_at`.
`memories.get` reads one, however old: a search can name one older than any list shows.
Listing facts stands on the search grant, so any key that may search may list.

## Profile facts

```python
facts = client.profile_facts.list(limit=50)
for f in facts["items"]:
    print(f["id"], f["source_kind"], f["content"])   # "pf_…", "user_stated", "Prefers dark mode."

kept = client.profile_facts.add("Works in Lisbon, UTC+0.")
kept["id"], kept["created"]                           # "pf_…", True; the same statement again: False

client.profile_facts.forget("pf_…", confirm=True)     # {"id": "pf_…", "status": "forgotten"}
```

The profile sits beside the Memories: a list of standing statements about the person, newest
first. Each has its `pf_` id, `content`, `recorded_at` and `source_kind`, which says where it
came from: `user_stated` (the owner or one of their keys said it), `imported`, or
`model_generated` (the assistant recorded it in a conversation). The service sets
`source_kind`; a request cannot.

`profile_facts.list` needs the profile tick on the key. With the tick, what else the key may do
follows its level: a Read & write key may `add` a statement, a Full access key may also
`forget` one, with the same confirmation rule as forgetting a memory (`428` without
`confirm=true`). Without the tick no profile operation is offered at all. Adding a statement
that is already there keeps the one there (`created: false`). There is no editing: a correction
is a new statement and the old one forgotten. List the profile once, near the start of a
conversation.

## Add a memory

```python
receipt = client.memories.add("We settled on Postgres for the ledger.")
receipt   # {"id": "doc_…", "kind": "note", "status": "processing", "learning": [{"memory_name": "Project decisions", "status": "processing"}]}
```

One fact, into the key's write target. It is written as a note the Memory reads, and this call
starts its learning run asynchronously: it answers `202` with the note's receipt, a document of
kind `note`. Poll `documents.get(receipt["id"])` as for a document write; acceptance is not
completion. To remove the note, pass its `doc_` id to `delete_document`; `forget_memory` takes
the `mem_` id of a fact the Memory learned. Needs a Read & write key.

## Add a document

```python
doc = client.add("…the text…", title="Call with Acme", custom_id="call-2026-09-24")
doc["status"]          # "pending" or "processing"
doc["id"]              # "doc_…": poll documents.get(id)["learning"]
```

The text (or a public `url` to fetch, one or the other) lands in the write target's upload folder
in the account's Files, is connected as a source on the spot, and a learning run starts on its
own; the call answers `202` with the receipt `{id, kind: "file", status, learning}`. The same
`custom_id` again names the document already there and starts nothing, so retries are safe.
`id` can be `null` on the `202` when the folder sync had not written the row yet; list the
documents a moment later. Uploads are capped at 32 MiB per file, on every plan.

### What the `202` becomes

When a learning run starts, it appears on the account’s Activity page. `learning` on the
receipt and on `documents.get(id)` names each Memory with its status: `pending` (waiting for
the next run; the one in flight starts it when it ends), `processing` (a run is reading it now),
`succeeded` or `failed`. After a successful run over that material, search can retrieve what it
learned. A `202` alone does not guarantee that a run started: it can be deferred while the
agent is paused or capacity is unavailable. If it ends `failed`, the document is still listed
and still unread, and the Memory's Report says why; usually the account has no working model
under AI Setup, or a source needs reauthorization.

### Documents

```python
docs = client.documents.list(kind="file")["items"]                # newest first; kind is "file" or "note"
for d in docs:
    detail = client.documents.get(d["id"])
    print(d["id"], d["memory_name"], d["title"], [e["status"] for e in detail.get("learning") or []])

client.documents.delete("doc_…", confirm=True)                    # Full access
```

A document is one piece of raw material a Memory has read or will read: a file in a folder
source, an uploaded file, a Notion page, a conversation the browser extension captured, or
what `add_document` handed in, or the note `add_memory` wrote. Its `learning` reads
`succeeded` once a run has committed it; it is the field to poll after a write. It is computed
per source, not per document: succeeded when the Memory's last successful run is at or after
the source's current version, under the Memory's current instruction. So when a new file
lands in the same upload folder, every document in that folder reads `pending` again until
the next run, and changing the Memory's instruction makes every document in it read `pending`
until it has run again.

### Sync and run are two different things

![Material arrives with a 202 and is not learned yet; a run learns it; then its learning succeeds and search finds it](/images/figures/sync-then-learn-api.svg)

A **sync** fetches raw material and stops. It runs no model, reads nothing into memory and
never changes what a search answers. A **run** (the learning turn) is what reads the unread
material. In the app the Memory's button says **Update now** while a source holds material
it has not read; a schedule does the same on a cadence; `add_document` starts a run itself.
"Unread" is decided by versions, not clocks: a sync that changed nothing, or a run on another
Memory, cannot make this one look up to date.

`add_document` normally starts learning without a schedule; if it is deferred, use the
Memory’s next run after fixing the cause. A schedule
matters for material that arrives without a call: a folder the person keeps adding to, a
Notion selection that changes. When a schedule fires, nothing changes in the API except the
memory itself: `learning` turns `succeeded` and the next search answers from what the run
learned.
There is no agent-protocol verb to create or pause a schedule; it is the owner's, in the app.

## Media

```python
client.media.list(limit=20)                          # photos and videos, newest first, each with a one-sentence summary
hits = client.media.search("someone skiing", kind="video")
for m in hits["items"]:
    print(m["memory_name"], m["filename"], [(x["t"], x["text"]) for x in m["moments"]])
client.media.get("med_…")                            # one item with all its moments
client.media.delete("med_…", confirm=True)           # Full access
```

A media Memory holds photos and videos, apart from documents and facts: `search` and the fact
and document lists do not read them. Each item has a `summary`, a `file_url` and a `thumb_url`
(routes on the API, read with the same bearer; a `Range` header answers `206` with that part).
`media.get` and `media.search` add its `moments`: a video's shots and spoken lines, each with
`t`/`end` in seconds, `speaker` and `thumb_url`. Adding media over the API is not offered yet;
it arrives through the Memory's sources in the app.

## Ask

```python
out = client.ask("Summarise what the seller learned about Postgres RLS.")
out["answer"]       # one answer, written from the Memories in reach
out["citations"]    # [{"memory_name": "Postgres notes"}]: the Memory, never the passages
out["partial"]      # the Memories that could not answer
```

`ask` is the other kind of read next to search: the memory engine reads the Memories in reach
and writes one answer, with no agent, no tools and no session. `citations` name the Memory the
answer came from, never a passage. A `model` field is refused (`422`), like any field the API
does not know.

`ask_memory` is held only when a credential's tool list names it, and today only a marketplace
buyer's credential does: it reaches the one Memory bought, holds nothing else, and every call
takes one call of the period's allowance. A developer key does not hold it at any level, and
the call is refused with `403 · unauthorized`. A product that wants to put a model over the
person's memory uses search and its own model ([Claude API](/build/integrations/claude-api/),
[OpenAI API](/build/integrations/openai-api/)).

## Forget and delete

```python
from membase import ConfirmationRequiredError

try:
    client.memories.forget("mem_…")
except ConfirmationRequiredError as e:
    print(e.details)        # {"id": "mem_…", "verb": "forget_memory", "content": "…", "how": "…"}

client.memories.forget("mem_…", confirm=True)     # {"id": "mem_…", "status": "forgotten"}
client.documents.delete("doc_…", confirm=True)    # {"id": "doc_…", "status": "deleted"}
```

`forget_memory` takes the `mem_` id of a learned fact, from `memories.list`, `memories.get` or
a search hit of `type: "memory"`. A note added with `add_memory` is a document; remove it with
`delete_document`.

Both need a Full access key (as do `media.delete` and `profile_facts.forget`, the latter with
the profile tick), and even then they do not run on a bare call: without
`confirm=true` nothing changes and the answer is `428 confirmation_required`
(`ConfirmationRequiredError`), naming the target by its public id and carrying a `how`
sentence to relay to the person. Pass `confirm=true` only after they agreed; from a developer
key that counts as the owner's confirmation. Forgetting a fact leaves the material it was
learned from; deleting a document withdraws it and what every Memory learned from it (the file
goes to the Files trash). A consent-minted client is never offered these verbs at
all: its token is read-only, so from an AI app the call is refused with `403 · unauthorized ·
token missing required scope`, not answered with the sentence. What is
forgotten or deleted is gone from the next search; nothing on the platform caches it.

Deleting a Memory, a source's imported material or the account has no agent-protocol verb;
those are the owner's, in the app.

## Rules

```python
client.capabilities()["rules"]
```

`GET /v1/capabilities` carries the standing rules for this credential under `rules`
(`citation_required`, `retention_notice`, `version`): what the skill tells an AI about behaving
beneath the ceiling the server enforces. Over MCP the same answer is `get_capabilities`; there
is no separate rules call.

## What code sees when the app does something

| The person | Code sees |
|---|---|
| selects **Update now**, or a schedule fires | documents' `learning` turns `succeeded`; the next search answers from the run |
| switches a Memory off for the key under **Use in** | on the very next call, same token, searches and lists leave it out and its ids answer `404`; if the key is left with one text Memory, that one becomes its write target |
| lowers the key's access | `403 · not in this agent's capability profile` on the verbs above it |
| revokes the key, or it expires | `403 · unauthorized` on every call; mint another |
| removes a source | its documents stop being listed; what was learned stays until the Memory is deleted |
| deletes the Memory | its `memory_name` no longer appears; searches no longer answer from it |
| has no working model for its agent | a failed turn, surfaced as `422 · capability_unavailable` or a search entry in `partial` (`reason: "error"`); stored memory remains, documents may wait unread. Read `code` on a `422`: `validation` there is a request the API cannot take, and `write_target_required` a write with nowhere to land, not a model problem |
| is on the free plan with its free turns spent | `422 · capability_unavailable` with `details.reason: "dormant"` until they bring a model or move to a paid plan |
| already has two agent turns running, or a token exceeds its per-minute request limit | `429 · rate_limited`. The turn limit hits agent turns (search is not held to it; `add_document` never is, its learning waits as `pending`); the per-minute limit hits any call, search and `add_document` included. No `Retry-After` is sent; the SDK backs off and retries twice |

## Rules of the road

* **Profile once, search per question.** The profile facts are few and standing; search is a turn inside the user's memory.
* **Cite the Memory.** Every hit names its Memory (`memory_name`); say where an answer came from.
* **Save what the user supplied,** in their words, and only when they asked or plainly meant to.
* **Never confirm on your own.** A delete or forget without `confirm=true` changes nothing and answers `428` with a `how` sentence; relay it and stop.
* **Treat `403` as withdrawn access.** The owner narrowed or revoked the key; do not retry with it.
* **Allow for cold starts.** Configure a suitable timeout and inspect `partial`; see [API troubleshooting](/build/reference/troubleshooting/).
* **Do not store to filter later.** There are no server-side metadata filters; use `custom_id` for your own bookkeeping.
* **The token stays out of logs.** Log the key's hint (`mbk_7f3a92d1…`), never the token.
