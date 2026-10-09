---
title: "Grok"
description: "Membase in Grok on the web, iOS and Android, as a custom connector with OAuth consent in the browser."
---

Membase in Grok on the web, iOS and Android, as a custom connector with OAuth consent in the browser.

Grok (web, iOS and Android) takes custom MCP servers as **connectors**. The menus are the
vendor's own and move with its releases; the Membase side, the URL, the consent screen and
the app's page on Connect, is the same as for every other client. Grok has no tile of its own
in Connect's client catalog: it appears under **Other apps**, with a monogram, once the
consent completed.

## Before you start

* A Grok plan that allows connectors. On a Business or Enterprise plan a team admin provisions them first.
* A Membase account with at least one Memory that has run once.

## Set up

1. Open `grok.com/connectors`.
2. **New Connector → Custom**.
3. Enter the server URL, `https://api.app.membase.io/mcp-http`, and complete the authentication: the browser opens Membase's consent screen. Tick the Memories Grok may use and, if it may read the profile, **Profile access**; press **Approve access**.
4. Grok discovers the tools the server exposes for that consent. Ask *"List my Membase containers."*

## With a developer key

Grok's connector dialog has no header field, so a person's Grok connects by consent only.
Grok's **API** also takes remote MCP servers as tools on a request; that is a developer
integration rather than a plugin, and it works with a developer key in the server's
`Authorization` header the way [MCP frameworks](/build/integrations/mcp-frameworks/) describes.

## What it can do

`list_containers`, `search_memories` and, when ticked, `get_profile`. Nothing that writes.

## Which Memories it uses

An empty container list means no Memory is switched on for this connection. Switch one on
under **Uses** on Grok's page in Connect, or under **Use in** on the Memory. Grok's page
exists under **Other apps** on Connect once the consent completed, whatever Grok's own screen
says; it has **Uses**, **Approvals** and **Disconnect…** like every other app.

## Remove it

Remove the connector on the same page, and **Disconnect…** on Grok's page in Membase's
Connect; the client does not tell the server.

## If something looks wrong

| It says | What it means | Do |
|---|---|---|
| the connector never authorizes | the URL has a typo or misses the path, or the consent tab was closed | paste the URL exactly; add it again |
| an empty container list | connected, no Memory switched on | **Uses** on Grok's page in Connect |
| no **New Connector** on a team plan | connectors are provisioned by the admin | ask the admin to add the URL |
