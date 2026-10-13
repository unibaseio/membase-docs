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
codex mcp add membase --url https://api.app.membase.com/mcp-http
codex mcp login membase
codex mcp list
```

`codex mcp login` opens the browser on Membase's consent screen; tick the Memories Codex may
use and, if it may read the profile, **Profile access**. `codex mcp list` shows the
server and whether it is authorized.

In the IDE extension: the gear menu → *MCP servers* → add the same server, then *Restart
extension* and *Authenticate*. A server added on one side appears on the other.

## With a developer key

Have Codex send the key from an environment variable instead of logging in:

```bash
codex mcp add membase --url https://api.app.membase.com/mcp-http --bearer-token-env-var MEMBASE_API_KEY
```

which writes this to `~/.codex/config.toml`:

```toml
[mcp_servers.membase]
url = "https://api.app.membase.com/mcp-http"
bearer_token_env_var = "MEMBASE_API_KEY"
```

Codex reads the variable from the environment it starts in, so `export MEMBASE_API_KEY=mbk_…`
in your shell profile; `codex mcp list` then shows *Bearer token* under Auth. The key's level
applies, up to Full access. `http_headers` (static values) and `env_http_headers` (values taken
from environment variables) under the same table set other headers. The snippet Membase serves
at `https://app.membase.com/plugin/clients/codex.toml` is the server alone, without the key line.

Or the skill:

> Install Membase from https://app.membase.com/skill using key mbk_…

Codex installs the folder beside `AGENTS.md` and points to it from there. The key has to reach
the commands Codex runs in later sessions: keep `MEMBASE_API_KEY` in the environment Codex
starts from, or under `set` in `[shell_environment_policy]` in `config.toml` (its `config.toml`
has no top-level `env` table). With the MCP tools already present it uses those and keeps the
skill for its rules.

## What it can do

With consent: `list_containers`, `search_memories` and, when ticked, `get_profile`; nothing
that writes. With a key: the key's level, up to Full access.

## Which Memories it uses

An empty container list means no Memory is switched on for this connection. Switch one on
under **Uses** on Codex's page in Connect (with a key: on the key's page), or under **Use in**
on the Memory.

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
| a write is refused | the connection is consent-minted (read-only), or the key is Read | give Codex a Read & write key through `bearer_token_env_var` or the skill |
| Membase fails to connect with `bearer_token_env_var` | `MEMBASE_API_KEY` is not set where Codex starts, or the key is unknown, expired or revoked: the server answers `401 invalid_token` to every request | export the variable; or mint a new key and update it |
| the extension does not see the server | it was added before the extension restarted | *Restart extension*, then *Authenticate* |
