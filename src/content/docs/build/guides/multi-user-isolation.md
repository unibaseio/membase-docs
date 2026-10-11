---
title: "Multi-user isolation"
description: "The account is the tenant. What that means for a product that serves many people, and the three ways to reach each person's memory with their own credential."
---

The account is the tenant. What that means for a product that serves many people, and the three ways to reach each person's memory with their own credential.

In Membase **the person owns the memory**, not the application. There is no application-wide
key, no master credential and no per-user tag inside a shared store. Every credential belongs
to one account, reaches only that account's Memories, and was minted by that account's owner.

If you have used a memory API where you tag content with a *user id* or *container tag* and
one key reaches them all: that is not this. Here a container is one of the person's own
Memories (a topic such as *Project decisions*), not a tenant.

## The boundary

| Layer | How it is separated |
|---|---|
| **Memory** | every account has its own agent container, a small VM with its own volume. Its files, documents and learned memory live there and nowhere else. A search is a turn inside that container. |
| **Control plane** | accounts, credentials, bindings, billing and raw source bytes are rows keyed by the account, under forced row-level security in Postgres. A query cannot see another account's rows even with the platform's own connection. |
| **Credentials** | a developer key or a consent token carries its account. It cannot be widened from the calling side, only on the Connect page by the owner. |
| **Model calls** | a turn goes through the platform's inference service under the account's own model policy; a model credential never enters an agent container. |
| **Deletion** | revoking, narrowing or deleting takes effect on the next call, ahead of any cache, projection or issued credential. |

A container outside a credential's reach is refused the same way as one that does not exist,
so a caller cannot even enumerate what it may not read.

## A product that serves many people

Give each person their own Membase account, and reach their memory with a credential that
person minted or approved. Three shapes fit most products.

![One shared account with a container per user and one key is not isolation; one account per person, each with their own credential, is](/images/figures/one-account-per-person.svg)

### Your product is an MCP client

If your product can act as an MCP client (an agent framework, a desktop app, anything that
speaks Streamable HTTP and OAuth), point it at `https://api.app.membase.io/mcp-http`. Each
user completes the consent screen once; your product holds one consent token per user and
gets `list_containers`, `search_memories` and, when the user ticked it, `get_profile`. It
cannot write and cannot see a Memory the user did not tick. The flow is in
[Authentication & Scopes](/build/reference/authentication/#oauth-for-an-app-that-connects-over-mcp) and the
client side in [Any MCP client](/connect/clients/membase-mcp/).

This is the shape to prefer: the user never handles a token, and can turn your product off
on the Connect page.

### Your product holds a key per user

If your product needs to write (save what a conversation produced) or is not an MCP client,
each user mints a developer key under **Connect › Developer keys**, chooses its level and
reach, and pastes it into your product. Store it per user, encrypted at rest, and send it as
that user's bearer and nobody else's.

```python
from membase import Membase

def memory_for(user) -> Membase:
    return Membase(api_key=secrets.get(user.id))       # that user's key, never another's

memory_for(alice).search("what did we decide about the ledger")
```

Two rules follow. A key is refused with `403` the moment its owner narrows or revokes it, so
treat `PermissionDeniedError` as *this user withdrew access*, not as a bug. And never route
one user's request through another user's key: the platform cannot tell, but the memory it
answers from is the wrong person's.

### Your agent answers from a memory you own

The reverse case: you hold the memory (a support corpus, a product's knowledge) and many
people ask it. List that Memory on the Marketplace as an **agent endpoint**. Each subscriber
receives a credential of their own and calls `ask_agent`; your agent answers from what it
learned, and the files never leave your container. Lapsing a subscription stops access at
once. See [Platform overview](/build/concepts/platform-overview/#marketplace).

![The seller's Memory and its agent stay in the seller's container; the listing is an agent endpoint; each subscriber calls ask_agent with their own credential and gets answers, never files](/images/figures/agent-endpoint.svg)

## What is not isolation

* **Containers are not users.** Making one container per end user inside one account puts every user's material behind one owner's credentials and one agent. Nothing stops it, and nothing protects it either.
* **Metadata is not a filter.** `add_document` accepts `metadata` for your own bookkeeping; search does not filter on it, so it cannot separate people.
* **Reach is not a secret.** A key with *All memories* reaches Memories the user makes later. Say so when you ask for one.

## Checking it

The negative cases are the ones to test:

| Try | Expect |
|---|---|
| a container id from another account, with your key | `403 · unauthorized · may not use that container` |
| a container the owner switched off for the key | the same `403`, on the very next call |
| a revoked key | `403 · unauthorized` on every call, at once |
| `delete_document` on a Read & write key | `403 · unauthorized · not in this agent's capability profile` |
| `delete_document` on a Full access key without `confirm` | `200 · status: confirmation_required` |
