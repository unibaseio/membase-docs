---
title: "Any MCP client"
description: "The MCP server itself: how a client discovers it, the two ways to authenticate, what a connected client sees, the ready-made config files, and the clients without a page of their own."
---

The MCP server itself: how a client discovers it, the two ways to authenticate, what a connected client sees, the ready-made config files, and the clients without a page of their own.

```
https://api.app.membase.io/mcp-http
```

One URL for every client. Streamable HTTP, JSON responses, with or without a trailing slash
(both answer the same; what fails is a wrong path such as `/mcp`). The server
speaks the current MCP specification and advertises its authorization the standard way, so
a client that can add "a remote MCP server with OAuth" can add Membase without a special
step.

## Two ways to authenticate

**OAuth consent**, for the person's own AI apps. An unauthenticated request answers `401`
with `WWW-Authenticate` pointing at
`https://api.app.membase.io/.well-known/oauth-protected-resource/mcp-http` (RFC 9728). The
metadata names the authorization server and its registration endpoint; the client registers
itself (RFC 7591) and runs the authorization code flow with PKCE. The browser opens Membase's
consent screen; the person ticks the Memories the app may use and whether it may read their
profile; the client receives a token good for that and nothing else.

**A developer key in the header**, for a client that can send a static header and a person
who prefers a key they minted:

```
Authorization: Bearer mbk_…
```

No consent round-trip; the key's access level and reach apply, up to Full access. The
ready-made config files carry no header, so a key never ends up in a public file.

## What a connected client sees

`tools/list` is filtered per caller.

| Credential | Tools offered |
|---|---|
| consent token | `list_containers`, `search_memories`; `get_profile` when the person ticked it |
| developer key, Read | those, plus `list_documents`, `memory_rules` |
| developer key, Read & write | plus `add_memory`, `add_document` |
| developer key, Full access | plus `delete_document`, `forget_memory` |
| an agent or workflow exposure | `ask_agent` or `workflow_invoke` |

A tool outside the caller's list is refused with `403 unauthorized` ("tool '…' is not in this
agent's capability profile"): a consent-minted client cannot write, delete or forget at all.
A Full access key that calls `delete_document` or `forget_memory` without `confirm=true`
answers `status: confirmation_required` with a `how` sentence for the model to relay. Retired
tool names (`memory_view_query`, `memory_list`, `memory_recall`, `memory_remember`,
`memory_ingest`, `memory_list_sources`, `memory_forget`, `agent_invoke`) still answer for
clients that carry them and are hidden from `tools/list`.

A search is a turn inside the person's container. The first one after a quiet spell can
take up to a minute; the answer marks in `containers[]` any Memory that could not answer
yet, and the model should say so rather than answer from nothing.

## Ready-made config files

Use these published configuration files and references for your client:

| File | For |
|---|---|
| `https://www.app.membase.io/plugin/mcp.json` | the server in the `mcpServers` shape most clients read |
| `https://www.app.membase.io/plugin/clients/vscode.mcp.json` | VS Code's `servers` shape |
| `https://www.app.membase.io/plugin/clients/codex.toml` | Codex's `config.toml` snippet |
| `https://www.app.membase.io/plugin/membase-skill.zip` | the skill folder |
| `https://www.app.membase.io/plugin/openapi/agent-protocol.json` | the OpenAPI document |
| `https://www.app.membase.io/skill` | the skill's `SKILL.md` with its install preamble |

## Other clients

The clients with a page of their own are [ChatGPT](/connect/clients/chatgpt/), [Claude](/connect/clients/claude/),
[Claude Code](/connect/clients/claude-code/), [Cursor](/connect/clients/cursor/), [Codex](/connect/clients/codex/), [Grok](/connect/clients/grok/) and
[Kimi Code](/connect/clients/kimi-code/). Everything else takes the same URL.

### VS Code (Copilot agent mode)

Command palette → *MCP: Add Server* → *HTTP* → the URL → complete the OAuth prompt, or in
`.vscode/mcp.json`:

```json
{ "servers": { "membase": { "type": "http", "url": "https://api.app.membase.io/mcp-http" } } }
```

### Windsurf

`~/.codeium/windsurf/mcp_config.json`, in the `mcpServers` shape:

```json
{ "mcpServers": { "membase": { "serverUrl": "https://api.app.membase.io/mcp-http" } } }
```

Then refresh the MCP list in Windsurf's settings and complete the OAuth prompt.

### Devin

```bash
devin mcp add --scope user membase https://api.app.membase.io/mcp-http
devin mcp login membase
```

### Claude Desktop, and any `mcpServers`-shaped client

Merge `https://www.app.membase.io/plugin/mcp.json` into the client's configuration:

```json
{ "mcpServers": { "membase": { "type": "http", "url": "https://api.app.membase.io/mcp-http" } } }
```

### Any other client, or your own

Use the same URL. The server advertises OAuth discovery on a `401`, accepts a bearer
developer key in `Authorization`, and speaks Streamable HTTP. An agent framework without an
MCP client can take `SKILL.md` as instructions and the REST API directly;
[MCP frameworks](/build/integrations/mcp-frameworks/) and [AI coding tools](/build/integrations/ai-coding-tools/) have the shapes.

## Verifying and revoking

The **Connect** page shows every authorized client with its last activity. A client's page
has the per-Memory switch (*Uses*), the credential list (*Approvals*, shown when there is
more than one) and **Disconnect…** for all of them. A client without a tile of its own is
listed under **Other apps** once authorized. Removing a connector inside the client does not
notify Membase: revoke on
Connect to be sure access has stopped. Revocation takes effect on the credential's next call.
