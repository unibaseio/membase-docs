---
title: "Cursor"
description: "Membase in Cursor through mcp.json, in one project or globally, with consent or a developer key."
---

Membase in Cursor through mcp.json, in one project or globally, with consent or a developer key.

Cursor reads Membase over MCP from a JSON file, in one project or for every project, and its
agent can take the skill as well.

## Before you start

* Cursor with MCP enabled under **Customize** in the sidebar.
* For a write-capable connection, a developer key from **Connect › Developer keys › Create key**.

## Set up

`.cursor/mcp.json` in the project, or `~/.cursor/mcp.json` for every project:

```json
{ "mcpServers": { "membase": { "url": "https://api.app.membase.io/mcp-http" } } }
```

Open **Customize** in the sidebar, enable Membase and complete the OAuth prompt: the browser
opens Membase's consent screen, where you tick the Memories Cursor may use and, if it may read
the profile, **Profile access**. Check that its tools appear under **Available Tools** in chat,
then ask *"List my Membase containers"*.

## With a developer key

Add the header; the key's level applies, up to Full access:

```json
{ "mcpServers": { "membase": {
    "url": "https://api.app.membase.io/mcp-http",
    "headers": { "Authorization": "Bearer mbk_…" } } } }
```

The token screen right after **Connect › Developer keys › Create key** writes this block with
the key filled in, on its **Cursor / VS Code** tab; the key's page later shows no snippets. Keep a
file that holds a key out of version control; the consent form of the file is safe to
commit.

Or the skill: paste the sentence from Connect's **Skills** tab and Cursor's agent installs
the skill folder in the project, points to it from the rules file and keeps the key. With the
MCP tools already present it uses those and keeps the skill for its rules.

## What it can do

With consent: `list_containers`, `search_memories` and, when ticked, `get_profile`, and
nothing that writes. With a key: the key's level.

## Which Memories it uses

An empty container list means no Memory is switched on for this connection. Switch one on
under **Uses** on Cursor's page in Connect, or on the key's page, or under **Use in** on the
Memory.

## Remove it

Delete the entry from `mcp.json`, then **Disconnect…** on Cursor's page in Connect or
**Revoke…** the key.

## If something looks wrong

| It says | What it means | Do |
|---|---|---|
| the server shows red under MCP | the URL is wrong, or consent was not completed | check the URL is the exact address, path included; retry the prompt; the Output panel's MCP Logs has the error |
| the tools appear but every call is refused | the key in `headers` is expired or revoked | rotate it on the key's page and update the file |
| an empty container list | connected, no Memory switched on | **Uses** on Cursor's page in Connect |
| a project file with a key was committed | the token is public | **Revoke…** it now and mint another |
