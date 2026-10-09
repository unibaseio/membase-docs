---
title: "ChatGPT"
description: "Membase as a ChatGPT plugin, through the Plugins dialog, with OAuth consent in the browser."
---

Membase as a ChatGPT plugin, through the Plugins dialog, with OAuth consent in the browser.

ChatGPT connects to Membase as a custom MCP server and reads the Memories you switch on for it.

## Before you start

* **Developer mode** may be required. ChatGPT asks for it on the web app (Pro, Plus, Business, Enterprise and Education plans; a workspace admin can turn it off); follow its on-screen instructions.
* A Membase account with at least one Memory that has run once.

## Set up

1. Open **ChatGPT Plugins** (`https://chatgpt.com/plugins`) and press **+**. Fill the dialog:
   * a name (*Membase*) and a description;
   * **Connection**: choose the public MCP server connection;
   * the complete URL, path included: `https://api.app.membase.io/mcp-http`;
   * **Authentication**: *OAuth*. Leave Client ID and Secret empty: ChatGPT registers itself with the server.
   If ChatGPT asks you to enable **Developer mode**, follow the on-screen instructions.
2. Accept the trust prompt and press **Create**.
3. The browser opens Membase's consent screen. Tick the Memories ChatGPT may use, and **Profile access** if it may read the profile. Press **Approve access**. The last page you should see is ChatGPT's own; if you end up on Membase instead, ChatGPT did not receive the code: retry the connection from ChatGPT.
4. Back in ChatGPT, the plugin's details page lists the discovered tools; use **Refresh** there if the list looks stale.
5. Start a new conversation and add Membase from the tools menu.

Then ask *"List my Membase containers."*

## What it can do

Read. `list_containers`, `search_memories` and, when ticked, `get_profile`. It cannot add,
delete or forget anything, and cannot see a Memory that is not switched on for it. The
writing and destructive tools are not in its tool list at all: `tools/list` does not offer
them, and a call to one is refused with `403 unauthorized`. ChatGPT has no way to send a
developer key, so the consent path is the only one.

## Which Memories it uses

An empty container list means no Memory is switched on for this connection yet. Switch one on
under **Uses** on ChatGPT's page in Connect, or under **Use in** on the Memory; the two are
the same switch, and off takes effect on the next question.

Two things worth knowing:

* ChatGPT registers itself under the same client name as the Codex CLI. Membase tells them apart and shows them as two tiles on Connect; do not be surprised to see both after setting up both.
* Profile access is decided on the consent screen only; ChatGPT's page in Connect has no profile switch. To change it, **Disconnect…** and set the plugin up again.

## Remove it

Delete the plugin under **Settings → Plugins**, and **Disconnect…** on ChatGPT's page in
Membase's Connect. ChatGPT does not tell the server when a plugin is removed.

## If something looks wrong

| It says | What it means | Do |
|---|---|---|
| ChatGPT asks for **Developer mode** | the plugin dialog needs it on this plan, or a workspace admin turned it off | follow ChatGPT's on-screen instructions |
| the plugin is created but never appears in a chat | it is not added to this conversation | start a new conversation and add Membase from the tools menu |
| *No memory access* on ChatGPT's page in Connect | authorized, no Memory switched on | switch one on under **Uses** |
| the consent screen never opens | the URL has a typo, or misses the path (a bare domain, `/mcp`) | paste `https://api.app.membase.io/mcp-http` exactly |
| the model answers from nothing about you | **Profile access** was not ticked at consent | **Disconnect…** on ChatGPT's page in Connect, set the plugin up again and tick it |
