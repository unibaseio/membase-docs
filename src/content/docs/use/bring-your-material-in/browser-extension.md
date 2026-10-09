---
title: "Browser extension"
description: "Unibase Memory, the browser extension that captures the person's conversations with other assistants and hands them to a Memory as a source."
---

Unibase Memory, the browser extension that captures the person's conversations with other assistants and hands them to a Memory as a source.

**Unibase Memory** is a browser extension. It captures the person's conversations with other
AI assistants as they happen and hands them to Membase, where a Memory reads them as a
source. Use this to bring conversations into memory. To let an AI app read existing memory, follow
[Connect your AI](/connect/).

* Chrome Web Store: [Unibase Memory](https://chromewebstore.google.com/detail/edmncknbiihfoakimejbepnaeemaaamf)

## What it captures

Conversations the person has with assistants in the browser. The capture is encrypted with
the person's wallet key before it leaves the browser, and it is the person's wallet that
Membase uses to read it back, so the platform sees nothing it was not handed. Which
assistants are captured is the extension's own setting.

## Connecting it to a Memory

In the app, on a Memory's page, the Add card has a door for it:

1. Press **Install** on *Unibase memory*. Once the extension is connected to the same wallet, the same door says **Use here**.
2. Press **Use here**. The door says *Added* and the source appears in the Add card.
3. Press **Update now**.

From then on the captured conversations reach the Memory as documents. The source's own page
shows a status word (*Syncing…*, *Sync failed*, *Needs reauthorization*) and **Sync now** (**Retry**
after a failed sync), **Reauthorize** or **Reconnect** when they apply, plus **Manage…** and
**Delete…**; see [Bring your material in](/use/bring-your-material-in/bring-material-in/).

## Writing the instruction

A Memory over conversations keeps memory about *the person*: what they asked, decided,
adopted. It does not restate what an assistant explained. Its instruction is a **filter on
the chats, not a subject**: *unibase* keeps what the chats say that bears on Unibase, not a
description of Unibase. An instruction written as a topic produces a log; written as a
filter it produces the standing facts the person would want any other assistant to know.

## If something looks wrong

| It says | What it means | Do |
|---|---|---|
| **Install** never turns into **Use here** | the page has no channel to the extension; it can only tell by what reached the wallet | install from the store, sign the extension in with the same wallet as the app, have a conversation, reload |
| *Added* but the Memory learns nothing | no conversation has been uploaded yet, or the Memory has not run | check the extension's own log; press **Update now** |
| the Memory reads like a log of what assistants said | the instruction is a topic | rewrite it as a filter on the chats |
| *Needs reauthorization* | the extension's credential expired | **Reauthorize** on the source page |
