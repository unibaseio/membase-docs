---
title: "Bring your material in"
description: "Choose how to bring in files, Notion pages or captured conversations, and learn when a Memory reads them."
---

Choose how to bring in files, Notion pages or captured conversations, and learn when a Memory reads them.

Choose the source that fits your material. Files, uploads, Notion and captured conversations
feed a Memory through its Add card; the Memory learns from them when you run it. Talking to
your assistant follows a different path: it can save what matters during the conversation.

![Material arrives when a source is added or synced; the Memory learns it on a run; then it is in memory](/images/figures/sync-then-learn.svg)

| Way in | Good for | Where |
|---|---|---|
| A folder in your Files | a project, a vault, anything already on disk | memory page › Add card › **Your Files › Choose** |
| Upload | a handful of files | memory page › Add card › **Upload files › Upload** |
| [Notion](/use/bring-your-material-in/notion/) | pages and databases | memory page › Add card › **Notion** (where available) |
| [Browser extension](/use/bring-your-material-in/browser-extension/) | your chats with other assistants | memory page › Add card › **Unibase memory** |
| Talking to your assistant | what you tell it, decide with it, ask it | Home, or Telegram |

## A folder in your Files

Press **Choose** on *Your Files*. The Files browser opens inside the dialog: browse, tick one or
more folders, and confirm in the footer. The folder is read in place, so anything you later add
to it is picked up on the memory's next run. A folder the memory already reads says *reading*.

If the files are not in your Files yet, put them there first from the Files page, or upload.

## Upload

Press **Upload** on *Upload files* and drop the files. They land in a folder named
“<memory name> uploads” (“… uploads (2)” if that name is taken) at the top of your Files, which
is connected as a source on the spot. Accepted: text formats (`.md`, `.markdown`, `.mdown`,
`.txt`, `.csv`, `.json`, `.jsonl`, `.yaml`, `.yml`); PDFs and images once a model is set up in
[AI Setup](/use/account-and-models/ai-setup/); and `.zip` archives, which are unpacked into a
folder. Office files (`.docx`, `.xlsx`, `.pptx` …) are refused: convert them to PDF or Markdown
first. Each file can be up to 32 MiB. The dialog tells you before sending if a file is not accepted.

## Notion

Connect a workspace, select the pages or databases the Memory should read, and add them.
A sync fetches those pages; the Memory still needs a run to learn from them. Follow the
[Notion guide](/use/bring-your-material-in/notion/) for authorization, page selection, updates and disconnection.

## Unibase memory

The Unibase Memory browser extension captures your conversations with other assistants and
hands them to a memory as a source.

1. Press **Install** on *Unibase memory*. A **Connect Unibase Memory** dialog opens; if the
   extension is not installed yet, use its **Install browser extension** link and sign the
   extension in with the same wallet.
2. Press **Connect wallet** and approve the two signatures. The door says *Added* and the source
   appears in the Add card; syncing continues in the background.
3. When the sync finishes, select **Update now**.

If your account already has this connection (another memory uses it, say), the door says
**Use here**; press it to add the same source to this memory.

A memory over your conversations keeps memory about *you*: what you asked, decided, adopted. It
does not restate what an assistant explained. Its instruction is a filter on the chats, not a
subject: *unibase* keeps what the chats say that bears on Unibase, not a description of Unibase.

## Talking to your assistant

Your assistant can retain relevant information from conversations on Home or Telegram.
A *Saved to memory* indication shows when information has been saved. Review the assistant's
memory on the Memory page; do not assume every message has been stored as a memory entry.

The [browser extension guide](/use/bring-your-material-in/browser-extension/) covers setup and missing conversations.

## Then run

After adding a source, select **Update now** on the Memory page or configure a schedule
in **Settings**. See [Memory](/use/manage-your-memory/memory/).
