---
title: "Codex"
description: "Membase in the Codex CLI and IDE extension over MCP, with consent or a developer key, and the skill beside AGENTS.md."
---

Membase in the Codex CLI and IDE extension over MCP, with consent or a developer key, and the skill beside AGENTS.md.

Codex, the CLI and the IDE extension, reads Membase over MCP, and can take the skill as well.

## Before you start

* Codex CLI with `codex mcp`, or the IDE extension; they share one configuration.
* For a write-capable connection, a developer key from **Connect › Developer keys › Create key**.

## Set up

```bash
codex mcp add membase --url https://api.app.membase.io/mcp-http
codex mcp login membase
codex mcp list
```

`codex mcp login` opens the browser on Membase's consent screen; tick the Memories Codex may
use and, if it may read the profile, **Profile access**. `codex mcp list` shows the
server and whether it is authorized.

In the IDE extension: the gear menu → *MCP servers* → add the same server, then *Restart
extension* and *Authenticate*. A server added on one side appears on the other.

## With a developer key

The snippet Membase serves at `https://www.app.membase.io/plugin/clients/codex.toml` is the
server alone, for `~/.codex/config.toml`:

```toml
[mcp_servers.membase]
url = "https://api.app.membase.io/mcp-http"
```

Membase writes no Codex snippet with a key in it. If your Codex build takes a static header on
a Streamable HTTP server, add one under `[mcp_servers.membase]` with the key as
`Authorization: Bearer mbk_…`; the setting's name is Codex's own and is not checked here, so
the plain way to give Codex a key is the skill:

> Install Membase from https://www.app.membase.io/skill using key mbk_…

Codex installs the folder beside `AGENTS.md`, points to it from there, and keeps the key as
`MEMBASE_API_KEY` under `env` in its `config.toml`. With the MCP tools already present it
uses those and keeps the skill for its rules.

## What it can do

With consent: `list_containers`, `search_memories` and, when ticked, `get_profile`; nothing
that writes. With a key: the key's level, up to Full access.

## Which Memories it uses

An empty container list means no Memory is switched on for this connection. Switch one on
under **Uses** on Codex's page in Connect, or under **Use in** on the Memory.

Codex and the ChatGPT connector register with Membase under the same client name. Membase
tells them apart and shows two tiles on Connect; each has its own **Uses** switches and its
own **Disconnect…**.

## Remove it

`codex mcp remove membase`, then **Disconnect…** on Codex's page in Connect or **Revoke…**
the key.

## If something looks wrong

| It says | What it means | Do |
|---|---|---|
| `codex mcp list` shows the server without authorization | consent not completed | `codex mcp login membase` |
| an empty container list | connected, no Memory switched on | **Uses** on Codex's page in Connect |
| a write is refused | the connection is consent-minted (read-only) | give Codex a Read & write key through the skill |
| the extension does not see the server | it was added before the extension restarted | *Restart extension*, then *Authenticate* |
