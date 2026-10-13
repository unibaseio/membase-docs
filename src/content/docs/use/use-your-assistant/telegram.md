---
title: "Telegram"
description: "Connect Telegram to your assistant, receive scheduled results, and manage or remove a connected chat."
---

Connect Telegram to your assistant, receive scheduled results, and manage or remove a connected chat.

The assistant that answers on Home can live in a Telegram chat as well. The same memory
answers in both places, and when the assistant finishes a scheduled run its result is
delivered to that chat. Telegram is not an MCP client: it is a second door to the one
assistant, not a reader of your Memories from outside.

## Before you start

* Telegram on your phone.
* An account whose assistant has a working model under AI Setup; the chat answers with the same model as Home.

## Set up

Membase connects Telegram through a bot you own.

1. In Telegram, open @BotFather, send it `/newbot` and copy the bot token it gives you.
2. On Home, at the foot of the conversation rail under **Remote**, press **Connect Telegram**.
3. Paste the bot token and press **Save**. Membase checks the token with Telegram before it
   keeps it. The optional **Webhook secret token** is the `secret_token` you pass to Telegram's
   `setWebhook` in the next step; set it and Membase accepts only updates that carry it.
4. Register the webhook. Membase does not poll Telegram and does not call `setWebhook` for your
   bot, so the bot hears nothing until you do. After **Save** the dialog shows the address
   once, as **Webhook URL**; copy it, then open
   `https://api.telegram.org/bot<token>/setWebhook?url=<Webhook URL>` with your bot token and
   that address (add `&secret_token=<value>` if you set one).
5. Press **Generate QR code**. Scan the QR with your phone's camera, or press **Copy link** and
   open the link in Telegram. Either way Telegram opens your bot with a one-time code already
   filled in; send it.
6. Back in the dialog press **Check connection**. The chat appears under **Connected chats**, and
   the **Remote** row on Home now opens that chat.

The code is single-use, valid for 15 minutes and tied to your account. Nothing is connected
until the bot actually receives it from your phone.

On a deployment that also runs a shared Membase bot, the dialog opens on **Scan a QR code**
instead: press **Generate QR code** and send the code to that bot, with no token or webhook of
your own. **Use a custom bot** switches to the steps above.

## What it can do

* **Talk to the assistant.** Ask anything you would ask on Home. It reads the same Memories and keeps the same instructions.
* **Receive scheduled results.** When the assistant finishes a scheduled run, its result is sent to this chat. A Memory's scheduled update runs its own agent, not the assistant, so it is not sent here.
* **Read it on Home.** The **Remote** row opens a read-only view of the Telegram chat, so what you said on your phone is there when you are back at your desk.

The Telegram chat is its own conversation. It does not appear in the day-grouped list on
Home, and Home's conversations do not appear in Telegram; the memory is what they share.

## Which Memories it uses

The assistant's: the Memories listed in the assistant's own settings on Home (the ⚙
**Assistant settings** button beside **Remote**, at the foot of the conversation rail). There is no switch on Connect for Telegram, because Telegram is the
assistant, not an app reading it.

## Remove it

Open **Assistant settings** (the ⚙ beside **Remote**) and press **Disconnect** in its Telegram
section. The connection dialog (Home's **Connect Telegram** quick action) also lists
**Connected chats** with a **Delete** per chat. The bot stops answering that chat at once, and scheduled
results stop going there.

## If something looks wrong

| It says | What it means | Do |
|---|---|---|
| the bot never answers anything | its webhook is not registered with Telegram | register the **Webhook URL** with `setWebhook` (step 4) |
| *That bind code is invalid or expired* | the code expired (15 minutes) or was already used | generate a new QR |
| the chat answers on the phone but nothing shows under **Remote** | the dialog has not re-read the connection yet | press **Check connection** |
| a scheduled result never reached Telegram | only the assistant's own scheduled runs are delivered, and only to a chat bound to it | Home › Remote › **Connect Telegram**; a Memory's schedule is not delivered to Telegram |
| the chat answers *The assistant run failed: …* instead of an answer | the assistant has no working model (in the app: *AI is unavailable*) | AI Setup › **Connect** a model source |
