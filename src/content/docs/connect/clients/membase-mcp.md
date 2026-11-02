---
title: "Any MCP client"
description: "The MCP server itself: how a client discovers it, the two ways to authenticate, what a connected client sees, the ready-made config files, and the clients without a page of their own."
---

The MCP server itself: how a client discovers it, the two ways to authenticate, what a connected client sees, the ready-made config files, and the clients without a page of their own.

```
https://api.app.membase.com/mcp-http
```

One URL for every client. Streamable HTTP, JSON responses, with or without a trailing slash
(both answer the same; what fails is a wrong path such as `/mcp`). The server
speaks the current MCP specification and advertises its authorization the standard way, so
a client that can add "a remote MCP server with OAuth" can add Membase without a special
step. The SDK also ships a local stdio server, `membase --local mcp` (from
`unibaseio-membase[local]`); see the [SDK quickstart](/build/reference/sdk-quickstart/).

## Two ways to authenticate

**OAuth consent**, for the person's own AI apps. An unauthenticated request answers `401`
with `WWW-Authenticate` pointing at
`https://api.app.membase.com/.well-known/oauth-protected-resource/mcp-http` (RFC 9728). The
metadata names the authorization server and its registration endpoint; the client registers
itself (RFC 7591) and runs the authorization code flow with PKCE. The browser opens Membase's
consent screen; the person ticks the Memories the app may use and whether it may read their
profile; the client receives a token good for that and nothing else.

**A developer key in the header**, for a client that can send a static header and a person
who prefers a key they minted:

```
Authorization: Bearer mbk_…
```

No consent round-trip; the key's access level and reach apply, up to Full access. An
unknown, expired or revoked key gets `401` with `WWW-Authenticate: Bearer error="invalid_token"`
on every request, `initialize` and `tools/list` included, so the client reports that it cannot
connect or needs authentication rather than showing tools. The ready-made config files carry
no header, so a key never ends up in a public file.

## What a connected client sees

The tools are the memory API's operations under their tool names, with the same arguments and
the same answers as REST ([API reference](/build/reference/api-reference/)). No tool takes a
Memory: reads cover every Memory the credential reaches, and a write lands in the one text
Memory it reaches. `tools/list` is filtered per caller and shows only what the credential holds.

| Credential | Tools offered |
|---|---|
| consent token | `get_capabilities`, `search_memories`, `list_memories`, `get_memory`, `list_media`, `get_media`, `search_media`; `list_profile_facts` when the person ticked **Profile access**. Read-only: it never writes and never confirms |
| developer key, Read | `get_capabilities`, `search_memories`, `list_memories`, `get_memory`, `list_documents`, `get_document`, `list_media`, `get_media`, `search_media`; `list_profile_facts` with **Your profile** ticked |
| developer key, Read & write | plus `add_memory`, `add_document`; `add_profile_fact` with the profile tick |
| developer key, Full access | plus `forget_memory`, `delete_document`, `delete_media`; `forget_profile_fact` with the profile tick; each only with `confirm=true` |
| a marketplace buyer's credential | `get_capabilities` and `ask_memory`, on the one Memory bought: answers, never passages |

A call to a tool outside the caller's list is refused as a tool error (HTTP `200`,
`isError: true`), not an HTTP status: *token missing required scope* when a read-only
credential (a consent token or a Read key) calls a writing tool, *tool '…' is not in this
agent's capability profile* when the tool is above a key's level otherwise. A consent-minted
client cannot write, delete or forget at all. The REST API answers the same refusals with
`403 unauthorized`. A Full access key that calls a destructive tool without `confirm=true` gets
a tool error with `confirmation_required` and a `how` sentence for the model to relay; nothing
changed. `get_capabilities` names what the connection holds, the Memories it reaches and the
person's standing rules (`rules`); there is no separate rules tool.

The protocol before this one had `list_containers`, `memory_rules`, `get_profile`,
`ask_agent`, `workflow_invoke`, a `container` argument and the `memory_*` names. None of them
is offered any more, and a `container` argument is refused like any unknown field.

A search is a turn inside the person's memory. The first one after a quiet spell can take up
to a minute; the answer names in `partial` any Memory that could not answer yet, and the model
should say so rather than answer from nothing.

## Ready-made config files

Use these published configuration files and references for your client:

| File | For |
|---|---|
| `https://app.membase.com/plugin/mcp.json` | the server in the `mcpServers` shape most clients read |
| `https://app.membase.com/plugin/clients/vscode.mcp.json` | VS Code's `servers` shape |
| `https://app.membase.com/plugin/clients/codex.toml` | Codex's `config.toml` snippet |
| `https://app.membase.com/plugin/membase-skill.zip` | the skill folder |
| `https://app.membase.com/plugin/openapi/agent-protocol.json` | the OpenAPI document |
| `https://app.membase.com/skill` | the skill's `SKILL.md` with its install preamble |

## Other clients

The clients with a page of their own are [ChatGPT](/connect/clients/chatgpt/), [Claude](/connect/clients/claude/),
[Claude Code](/connect/clients/claude-code/), [Cursor](/connect/clients/cursor/), [Codex](/connect/clients/codex/), [Grok](/connect/clients/grok/) and
[Kimi Code](/connect/clients/kimi-code/). Everything else takes the same URL.

### VS Code (Copilot agent mode)

Command palette → *MCP: Add Server* → *HTTP* → the URL → complete the OAuth prompt, or in
`.vscode/mcp.json`:

```json
{ "servers": { "membase": { "type": "http", "url": "https://api.app.membase.com/mcp-http" } } }
```

### Windsurf

`~/.codeium/windsurf/mcp_config.json`, in the `mcpServers` shape:

```json
{ "mcpServers": { "membase": { "serverUrl": "https://api.app.membase.com/mcp-http" } } }
```

Then refresh the MCP list in Windsurf's settings and complete the OAuth prompt.

### Devin

```bash
devin mcp add --scope user membase https://api.app.membase.com/mcp-http
devin mcp login membase
```

### Any `mcpServers`-shaped client

Merge `https://app.membase.com/plugin/mcp.json` into the client's configuration:

```json
{ "mcpServers": { "membase": { "type": "http", "url": "https://api.app.membase.com/mcp-http" } } }
```

Claude Desktop's `claude_desktop_config.json` is for local servers it launches itself; add
Membase in Claude as a custom connector instead, as [Claude](/connect/clients/claude/) describes.

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
