---
title: "Kimi Code"
description: "Membase in the Kimi Code CLI over Streamable HTTP, with OAuth consent or a developer key in the header, and the skill."
---

Membase in the Kimi Code CLI over Streamable HTTP, with OAuth consent or a developer key in the header, and the skill.

**Kimi Code CLI** connects to remote MCP servers over Streamable HTTP, and reads pages and
runs commands, so it can take the skill as well.

## Before you start

* Kimi Code CLI with `kimi mcp`.
* For a write-capable connection, a developer key from **Connect › Developer keys › Create key**.

## Set up

```bash
kimi mcp add --transport http --auth oauth membase https://api.app.membase.io/mcp-http
kimi mcp auth membase
kimi mcp list
```

`kimi mcp auth` opens the browser on Membase's consent screen and caches the token under
`~/.kimi/mcp-oauth/`. Tick the Memories Kimi Code may use and, if it may read the profile,
**Profile access**. `kimi mcp list` shows the server and its authorization state. Kimi Code has
no tile of its own in Connect's client catalog: it appears under **Other apps** once the consent
completed.

## With a developer key

```bash
kimi mcp add --transport http membase https://api.app.membase.io/mcp-http \
  --header "Authorization: Bearer mbk_…"
```

The key's level applies, up to Full access. The skill sentence from Connect's **Skills** tab
works as well: Kimi Code installs the folder and keeps the key as `MEMBASE_API_KEY`.

## What it can do

With consent: `list_containers`, `search_memories` and, when ticked, `get_profile`; nothing
that writes. With a key: the key's level.

## Which Memories it uses

An empty container list means no Memory is switched on for this connection. Switch one on
under **Uses** on Kimi Code's page in Connect (under **Other apps**), or under **Use in** on
the Memory.

## Remove it

`kimi mcp remove membase`, then **Disconnect…** on Kimi Code's page in Connect or
**Revoke…** the key.

## If something looks wrong

| It says | What it means | Do |
|---|---|---|
| `kimi mcp list` shows the server unauthorized | consent not completed | `kimi mcp auth membase` |
| an empty container list | connected, no Memory switched on | **Uses** on Kimi Code's page in Connect |
| a write is refused | the connection is consent-minted (read-only), or the key is Read | use a Read & write key in the header |
| the tools appear but every call is refused | the key in the header is expired or revoked | rotate it and run `kimi mcp add` again |
