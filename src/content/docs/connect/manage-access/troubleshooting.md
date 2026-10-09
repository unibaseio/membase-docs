---
title: "Troubleshooting"
description: "Every word and status a connected client, the Connect page or the API can show, and what to do about it."
---

Every word and status a connected client, the Connect page or the API can show, and what to do about it.

Look up the word on screen, or the status in the answer.

## On the Connect page

| It says | What it means | Do |
|---|---|---|
| *Set up* on a tile | this app is not connected | pick the tile and follow the steps |
| *No memory access* (amber) on an app's page | connected, but no Memory switched on | turn a switch on under **Uses** |
| the app cannot see a Memory | its switch is off | Memory page › **Use in** |
| I removed the app in Claude or ChatGPT but it still shows *Authorized* | the app did not tell Membase | **Disconnect…** on the app's page |
| *The MCP address is unavailable* | the page could not ask the server for it | reload; the sentence for your AI still works |
| my AI installed the skill but says it has no access | the skill needs a developer key | Skills tab › **Create key**, and paste the sentence |
| a key's row says *Expired* | its token has lapsed | **⋯ › Create a similar key** |
| two tiles for ChatGPT and Codex | they register under one client name; Membase tells them apart | nothing |

## In the client

| It says | What it means | Do |
|---|---|---|
| the server never authorizes | the URL has a typo or a wrong path (`/mcp`, a bare domain), or the consent tab was closed | paste `https://api.app.membase.io/mcp-http` exactly; run the login again |
| *List my containers* answers an empty list | connected, no Memory switched on | **Uses** on the client's page, or **Use in** on the Memory |
| the tools appear, every call is refused | the key in the header is expired or revoked | rotate it and update the file |
| a write is refused | the connection is consent-minted (read-only), or the key is Read | mint a Read & write key and use it instead |
| the model says a Memory "could not answer yet" | the memory was asleep; the first search after a quiet spell wakes it | ask again in a moment |
| the model answers from nothing about the person | the profile tick is off | an app: **Disconnect…** and authorize again with **Profile access** ticked; a key: **Your profile** on the key's page |
| the model asks me to confirm a delete | a Full access key called delete or forget without `confirm=true` and got its `how` sentence | decide; only a Full access key can pass `confirm=true` |
| a retired tool name in the model's call (`memory_recall`…) | the client cached an old list | it still answers; restart the client to refresh `tools/list` |

## In the API answer

| Answer | Meaning | Do |
|---|---|---|
| `401` | no bearer at all | send `Authorization: Bearer …` |
| `403 · unauthorized` | an unknown, expired or revoked token | mint a new key; do not retry with this one |
| `403 · unauthorized · may not use that container` | the container is outside the reach, or does not exist | switch it on under **Memory access**; or list containers first |
| `403 · unauthorized · not in this agent's capability profile` | the tool is not in this credential's list: above the key's level, or a write from a consent-minted app | raise the level, or mint a higher key |
| `200 · status: confirmation_required` | a Full access key's destructive verb without `confirm=true` | pass `confirm=true` after the person agreed |
| `400 · validation` | a missing `q`, both `content` and `url`, an ambiguous `container` | fix the request; with several Memories in reach, `container` is required |
| `404 · not_found` | an unknown document or memory id | list first |
| `422 · capability_unavailable · no model` | the account has no working model | [AI Setup](/use/account-and-models/ai-setup/) |
| `422 · capability_unavailable · no agent containers` | the memory service is unavailable | contact support with the error and trace ID |
| `422 · reason: dormant` | a free-plan account whose free turns are spent | bring a model, or a paid plan |
| `429 · rate_limited` | the account's concurrent-turn budget | retry later; the SDK retries twice with backoff |
| `202` with `document_id: null` | the folder sync had not written the row yet | list the container's documents in a moment |
| a search takes a minute | the container was asleep | allow time for startup; check for errors if the request times out |
| `405` on the MCP URL | a wrong path that missed the mount, e.g. `/mcp` or `/mcp-http/v1` | use `https://api.app.membase.io/mcp-http` exactly; a trailing slash is fine |

## On the extension

| It says | What it means | Do |
|---|---|---|
| **Install** never becomes **Use here** | the page cannot see the extension; it can only tell by what reached the wallet | sign the extension in with the same wallet, have a conversation, reload |
| *Reading* but the Memory learns nothing | nothing uploaded yet, or the Memory has not run | check the extension's log, then select **Update now** on the Memory |
| the Memory reads like a log | the instruction is a topic | rewrite it as a filter on the chats |

## Reporting a problem

Every error envelope carries a `trace_id`. Quote it, with the key's hint (never the token),
the tool, and the time.
