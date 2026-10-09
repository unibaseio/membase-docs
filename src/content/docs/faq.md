---
title: "FAQ"
description: "Answers about memories, connected apps, models, exports and deleting data."
---

Answers about memories, connected apps, models, exports and deleting data.

## What is a Memory?

A Memory organizes information about a topic, such as project decisions, reading notes or
customers. Choose its sources, describe what it should retain, and update it manually or on a
schedule. You control which apps and keys can access it.
[Concepts](/concepts/).

## I added a folder. Why does my AI not know about it yet?

Adding a source makes its content available for processing. Select **Update now** on the
Memory page, or wait for its scheduled update, to learn from that content. Check the run's
**Report** if the update fails. [Bring your material in](/use/bring-your-material-in/bring-material-in/).

## Why can the first search take longer?

A search after a period of inactivity may take longer to start. Search also uses a model to
find relevant information. If the request fails, check the model configuration and the error
before assuming the Memory is empty. [Search behavior](/build/concepts/how-membase-works/#a-search-is-a-turn).

## Where can I manage and export my data?

Manage your material in **Files**, review learned content in **Memory**, and choose which apps
can access it in **Connect**. Download an export from **Settings › Data & export**. If the
export warning says agent memory files are missing, export again before relying on it as a
backup. [Export and deletion](/use/account-and-models/settings/).

## What can a connected app do?

An app authorized through the MCP consent screen can read the Memories you select. Profile
access is a separate choice. For an integration that needs to add or remove content, create
a developer key with the appropriate access level. [Access control](/connect/manage-access/access-control/).

## How do I stop an app accessing my memory?

Switch off a Memory under **Use in**, or use **Disconnect…** on the app's page in **Connect**
to revoke its approvals. These changes apply to subsequent requests. They do not remove
content the external app has already received. Removing a connector only inside that app
does not revoke its Membase authorization.

## Which model does it use? Do I need my own key?

Use **AI Setup** to connect a supported provider key or subscription. A free account includes
an initial allowance of chat turns. When that allowance is used, stored memories remain;
continuing to run the assistant requires an available model source or a suitable plan.
[AI Setup](/use/account-and-models/ai-setup/).

## What is the profile?

The profile contains information about you, such as preferences and recent context. You can
grant access to it separately from access to individual Memories.

## What cannot be undone?

Deleting a Memory removes its stored content. Deleting a conversation removes its transcript;
information already saved to memory is retained. **Delete everything** in Settings removes
account data while retaining your sign-in identity. Review each confirmation and download
any data you want to keep before proceeding. [Deletion and access controls](/concepts/#stopping-and-undoing).

## How is this different from searching my files?

A Memory processes source material and retains information for later retrieval. Updating a
source and updating its Memory are separate actions. See the [memory engine benchmarks](/evaluation/benchmarks/)
for evaluation results and their scope; those measurements are separate from hosted API performance.

Questions about API status codes, metadata filters or serving multiple users are covered in
[API troubleshooting](/build/reference/troubleshooting/).
