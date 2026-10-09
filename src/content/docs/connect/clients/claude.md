---
title: "Claude"
description: "Membase in Claude on the web and the desktop app, as a custom connector with OAuth consent in the browser."
---

Membase in Claude on the web and the desktop app, as a custom connector with OAuth consent in the browser.

Claude (claude.ai and the desktop app) takes Membase as a **custom connector** and reads the
Memories you switch on for it. For Claude Code, the command-line agent, see
[Claude Code](/connect/clients/claude-code/).

## Before you start

* A Claude plan that allows custom connectors (organisation admins can restrict them).
* A Membase account with at least one Memory that has run once.

## Set up

1. **Customize → Connectors → + → Add custom connector**.
2. Paste `https://api.app.membase.io/mcp-http` and confirm.
3. Finish the authorization in the browser. On Membase's consent screen tick the Memories Claude may use and, if it may read the profile, **Profile access**; press **Approve access**. The last page you should see is Claude's own; if you end up on Membase instead, Claude did not receive the code: retry the connection from Claude.
4. In a chat, open **+ → Connectors** and switch Membase on, then ask *"List my Membase containers."*

## What it can do

`list_containers`, `search_memories` and, when ticked, `get_profile`. Nothing that writes:
the saving, deleting and forgetting tools are not in its tool list, and a call to one is
refused with `403 unauthorized`. Claude's connector settings have no field for a header, so
the consent path is the only one here; a developer key belongs to
[Claude Code](/connect/clients/claude-code/). Profile access is decided on the consent screen only; to
change it, **Disconnect…** on Claude's page in Connect and add the connector again.

## Which Memories it uses

An empty container list means no Memory is switched on for this connection. Switch one on
under **Uses** on Claude's page in Connect, or under **Use in** on the Memory. Off takes
effect on Claude's next question.

## Remove it

Remove the connector on the same Connectors page, and **Disconnect…** on Claude's page in
Membase's Connect too: the client does not tell the server.

## If something looks wrong

| It says | What it means | Do |
|---|---|---|
| the connector never finishes authorizing | the URL has a typo or misses the path, or the consent tab was closed | paste the URL exactly; add the connector again |
| *List my containers* answers an empty list | connected, no Memory switched on | **Uses** on Claude's page in Connect |
| the last step lands on the Membase app | Claude did not receive the authorization code | retry the connection from Claude |
| the model says a Memory "could not answer yet" | the memory was asleep; the first search wakes it | ask again in a moment |
| the model answers from nothing about you | **Profile access** was not ticked at consent | **Disconnect…** on Claude's page in Connect, add the connector again and tick it |
