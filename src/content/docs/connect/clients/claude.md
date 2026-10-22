---
title: "Claude"
description: "Membase in Claude on the web and the desktop app, as a custom connector, with OAuth consent in the browser or a developer key in a request header."
---

Membase in Claude on the web and the desktop app, as a custom connector, with OAuth consent in the browser or a developer key in a request header.

Claude (claude.ai and the desktop app) takes Membase as a **custom connector** and reads the
Memories you switch on for it. For Claude Code, the command-line agent, see
[Claude Code](/connect/clients/claude-code/).

## Before you start

* A Claude plan with custom connectors: Free (one custom connector), Pro, Max, Team or Enterprise. On Team and Enterprise an Owner adds the connector first under **Organization settings → Connectors**; members then press **Connect** on it under **Customize → Connectors**.
* A Membase account with at least one Memory that has run once.

## Set up

1. **Customize → Connectors**, then the add option → **Custom** → **Web**.
2. Paste `https://api.app.membase.com/mcp-http` and confirm.
3. Finish the authorization in the browser. On Membase's consent screen tick the Memories Claude may use and, if it may read the profile, **Profile access**; press **Approve access**. The last page you should see is Claude's own; if you end up on Membase instead, Claude did not receive the code: retry the connection from Claude.
4. In a chat, open **+ → Connectors** and switch Membase on, then ask *"List my Membase containers."*

## With a developer key

Request-header authentication is a beta that Claude offers to a limited set of organizations;
if the custom connector form shows no **Request headers** section, use the consent path above.
Where it is offered, choose **No sign-in** for authentication (a header named `Authorization`
cannot be set on an OAuth connection), then add `Authorization` with the value `Bearer mbk_…`.
A valid key passes without the consent screen, and the key's level and reach apply, up to Full
access. The authentication settings cannot be edited after the connector is added: to change
the key, remove the connector and add it again.

## What it can do

With consent: `list_containers`, `search_memories` and, when ticked, `get_profile`. Nothing
that writes: the saving, deleting and forgetting tools are not in its tool list, and a call to
one comes back as a tool error (*token missing required scope*). With a key in **Request
headers**: the key's level. Profile access is decided on the consent screen only; to change
it, **Disconnect…** on Claude's page in Connect and add the connector again (with a key,
it is **Your profile** on the key's page).

## Which Memories it uses

An empty container list means no Memory is switched on for this connection. Switch one on
under **Uses** on Claude's page in Connect (with a key: on the key's page), or under **Use in**
on the Memory. Off takes effect on Claude's next question.

## Remove it

Remove the connector on the same Connectors page, and **Disconnect…** on Claude's page in
Membase's Connect too, or **Revoke…** the key: the client does not tell the server.

## If something looks wrong

| It says | What it means | Do |
|---|---|---|
| the connector never finishes authorizing | the URL has a typo or misses the path, or the consent tab was closed | paste the URL exactly; add the connector again |
| *List my containers* answers an empty list | connected, no Memory switched on | **Uses** on Claude's page in Connect |
| the last step lands on the Membase app | Claude did not receive the authorization code | retry the connection from Claude |
| the model says a Memory "could not answer yet" | the memory was asleep; the first search wakes it | ask again in a moment |
| the connector with a key in **Request headers** cannot connect | the key is unknown, expired or revoked: the server answers `401 invalid_token` to every request | mint a new key, remove the connector and add it again with the new key |
| the model answers from nothing about you | **Profile access** was not ticked at consent | **Disconnect…** on Claude's page in Connect, add the connector again and tick it |
