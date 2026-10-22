---
title: "Kimi Code"
description: "Membase in the Kimi Code CLI over Streamable HTTP, with OAuth consent or a developer key in the header, and the skill."
---

Membase in the Kimi Code CLI over Streamable HTTP, with OAuth consent or a developer key in the header, and the skill.

**Kimi Code CLI** connects to remote MCP servers over Streamable HTTP, and reads pages and
runs commands, so it can take the skill as well.

## Before you start

* Kimi Code CLI. It has no `kimi mcp` command: MCP servers are declared in `mcp.json`, or added with `/mcp-config` inside a session.
* For a write-capable connection, a developer key from **Connect › Developer keys › Create key**.

## Set up

Add the server to `~/.kimi-code/mcp.json` for every project, or to `.kimi-code/mcp.json` in
one project:

```json
{ "mcpServers": { "membase": { "url": "https://api.app.membase.com/mcp-http" } } }
```

`/mcp-config` in a session adds the same entry without editing the file. A server added while a
session is open joins only the sessions started after it. In a new session run:

```text
/mcp-config login membase
```

The browser opens Membase's consent screen. Tick the Memories Kimi Code may use and, if it may
read the profile, **Profile access**. `/mcp` shows the server's connection status. Kimi Code has
no tile of its own in Connect's client catalog: it appears under **Other apps** once the consent
completed.

## With a developer key

Name an environment variable that holds the key, instead of logging in:

```json
{ "mcpServers": { "membase": {
    "url": "https://api.app.membase.com/mcp-http",
    "bearerTokenEnvVar": "MEMBASE_API_KEY" } } }
```

and `export MEMBASE_API_KEY=mbk_…` in the shell that starts Kimi Code. A static
`"headers": { "Authorization": "Bearer mbk_…" }` works too; keep a file that holds a key out of
version control. The key's level applies, up to Full access. The skill sentence from Connect's
**Skills** tab works as well: Kimi Code installs the folder and keeps the key as
`MEMBASE_API_KEY`.

## What it can do

With consent: `list_containers`, `search_memories` and, when ticked, `get_profile`; nothing
that writes. With a key: the key's level.

## Which Memories it uses

An empty container list means no Memory is switched on for this connection. Switch one on
under **Uses** on Kimi Code's page in Connect (under **Other apps**), or under **Use in** on
the Memory.

## Remove it

Delete the `membase` entry from `mcp.json`, or remove it with `/mcp-config`; sessions already
open list it as `removed` until they end. Then **Disconnect…** on Kimi Code's page in Connect or
**Revoke…** the key. A consent token Kimi Code still holds stops working once you disconnect.

## If something looks wrong

| It says | What it means | Do |
|---|---|---|
| `/mcp` shows Membase not authorized | consent not completed | `/mcp-config login membase` |
| `/mcp` does not list Membase | the entry was added while this session was open | start a new session |
| an empty container list | connected, no Memory switched on | **Uses** on Kimi Code's page in Connect |
| a write is refused | the connection is consent-minted (read-only), or the key is Read | use a Read & write key through `bearerTokenEnvVar` or `headers` |
| Membase fails to connect with a key | `MEMBASE_API_KEY` is not set in Kimi Code's environment, or the key is unknown, expired or revoked: the server answers `401 invalid_token` to every request, so no tools load | set the variable; or mint a new key, update `MEMBASE_API_KEY` (or the header) and start a new session |
