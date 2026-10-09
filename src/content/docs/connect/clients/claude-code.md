---
title: "Claude Code"
description: "Membase in Claude Code: over MCP with consent, over MCP with a developer key, or as the skill alone."
---

Membase in Claude Code: over MCP with consent, over MCP with a developer key, or as the skill alone.

Claude Code reads pages and runs commands, so it can take Membase three ways: over MCP with
consent, over MCP with a developer key, or as the skill alone. Pick by what you want it to be
able to do.

## Before you start

* Claude Code 2.1.186 or later for `claude mcp login`; older versions authorize with `/mcp` inside a session.
* For anything that writes, a developer key from **Connect › Developer keys › Create key** at Read & write or Full access.

## Set up

### Over MCP, with consent

```bash
claude mcp add --transport http --scope user membase https://api.app.membase.io/mcp-http
claude mcp login membase
```

`--scope user` makes the server available in every project. The browser opens Membase's
consent screen; tick the Memories Claude Code may use and, if it may read the profile,
**Profile access**. Then ask *"List my Membase containers."* This connection is
read-only.

## With a developer key

No OAuth round-trip, and the key's level applies, up to Full access:

```bash
claude mcp add --transport http --scope user membase https://api.app.membase.io/mcp-http \
  --header "Authorization: Bearer ${MEMBASE_API_KEY}"
```

The token screen right after **Connect › Developer keys › Create key** writes this command
with the key filled in, on its **Claude Code** tab. The key's page later shows no snippets, and
a key created from the **Skills** tab shows only the sentence below.

Or the skill alone, with no MCP server at all. Paste the sentence from Connect's **Skills**
tab:

> Install Membase from https://www.app.membase.io/skill using key mbk_…

Claude Code fetches the skill folder into `~/.claude/skills/membase/`, stores the key as
`MEMBASE_API_KEY` in the `env` block of `~/.claude/settings.json`, checks it with one call
and reports which Memories it can use. If it already has the MCP tools it uses those and
keeps the skill for its rules.

## What it can do

| Way in | Tools |
|---|---|
| consent | `list_containers`, `search_memories`, `get_profile` when ticked; read-only |
| a Read key | those, plus `list_documents`, `memory_rules` |
| a Read & write key | plus `add_memory`, `add_document` |
| a Full access key | plus `delete_document`, `forget_memory`, each only with `confirm=true` after you agreed |

## Which Memories it uses

With consent: the Memories ticked on the consent screen, switchable later under **Uses** on
Claude Code's page in Connect. With a key: the key's reach, switchable on the key's page or
under **Use in** on the Memory. An empty container list means nothing is switched on yet.

## Remove it

`claude mcp remove membase`. Then **Disconnect…**
on Claude Code's page in Connect, or **Revoke…** the key: the client does not tell the
server.

## If something looks wrong

| It says | What it means | Do |
|---|---|---|
| `claude mcp list` shows membase as *needs authentication* | consent not completed | `claude mcp login membase`, or `/mcp` in a session |
| *List my containers* answers an empty list | connected, no Memory switched on | **Uses** on Claude Code's page in Connect, or **Use in** on the Memory |
| the skill says it has no access | no key, or the key reaches nothing | Skills tab › **Create key**; or switch a Memory on for the key |
| a write is refused with `403` | the connection is consent-minted (read-only), or the key is Read | use a Read & write key |
| the first search takes a minute | the memory was asleep | nothing; the next one is quick |
| the model asks me to confirm a delete | a Full access key called delete or forget without `confirm=true` and got its `how` sentence | decide; only a Full access key can pass `confirm=true` |
