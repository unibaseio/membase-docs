---
title: "Notion"
description: "Connect a Notion workspace, choose pages for a Memory, learn from them, and manage updates or disconnect the workspace."
---

Connect a Notion workspace, choose pages for a Memory, learn from them, and manage updates or disconnect the workspace.

Use Notion pages and databases as a Memory's sources. Connecting a workspace gives Membase
permission to find pages; choosing pages imports them; running the Memory learns from them.

You need a Memory and permission to share the Notion pages you want it to read.

## Connect and choose pages

1. Open the Memory. Under **Add to this memory**, press **Connect** on **Notion**. If a
   workspace is already connected, the button says **Add pages**.
2. Press **Connect Notion** and finish the authorization screen. Back in Membase, the picker
   shows the workspace and the pages available to it.
3. Tick the pages or databases to read. Use **Search pages, or paste a Notion link** to find
   a specific page. Choose whether **Include subpages** should be on.
4. Press **Add to** followed by the Memory's name. The picker closes and the source appears
   under the Memory's Add card.
5. Open the source and wait for its files to arrive. Return to the Memory and press **Update now**. When the run finishes, inspect **Your memory** or ask about the material.

If your deployment does not offer the Notion card, use [Files](/use/bring-your-material-in/files/)
to import an export instead. Some deployments offer **Use a token instead** in the picker;
that token must have access to the pages you select.

## Update the selection

Open the source from the Memory. The **Pages** row shows the selected pages and whether it
includes subpages. Press **Change…**, adjust the selection, then **Save pages**.

If a page is missing, open the workspace's **⋯** menu and choose **Update page access** for
an OAuth connection, then **Refresh list**. A newly shared page may take a moment to appear.
Pasting a link does not grant access to a page that the connection cannot read.

## Keep it up to date

**Sync now** fetches the current Notion content. It does not update what the Memory knows;
press **Update now** on the Memory afterwards, or let its [schedule](/use/automate-and-troubleshoot/schedules/) run.
**Pause** on the source stops its syncing; **Resume** starts it again. Pausing a source and
pausing a Memory's schedule are separate controls.

## Disconnect a workspace

In the page picker, open **⋯** and choose **Disconnect** followed by the workspace name.
Read the confirmation: it names the affected Memories. Confirm only if those sources should
stop syncing. Imported material and what the Memories already learned remain.

To remove learned content, use the [Memory's editing and deletion controls](/use/manage-your-memory/memory/).
Disconnecting Notion is not a request to forget what it previously supplied.

## If something looks wrong

| What you see | What to do |
|---|---|
| No pages shared with Membase yet | Use **Update page access**, share the required pages, then refresh the list. |
| A page is absent | Check the selected workspace and that the connection has permission to read it. |
| Files arrived but answers have not changed | Run the Memory; syncing alone does not teach it. |
| Needs reauthorization | Use **Reauthorize** on the source and finish authorization again. |
| Sync failed | Open the source's error, check page access, and retry **Sync now**. |
