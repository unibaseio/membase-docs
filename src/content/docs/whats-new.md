---
title: "What's new"
description: "New features and significant updates for Membase users and developers."
---

New features and significant product changes, newest first.

## October 2026

**SDK packages renamed (11 Oct).** The Python SDK is now `unibaseio-membase` on PyPI and the
TypeScript SDK `@unibaseio/membase` on npm, both from 0.3.0. The Python package includes the
`membase` command line; `@unibaseio/membase-cli` provides the same command for the hosted API
without Python. `pip install 'unibaseio-membase[local]'` adds an MCP server (`membase mcp`)
and, on Python 3.12 or 3.13, runs the memory engine on your machine: `Membase(local=True)` in
Python, or `membase --local serve` for the same API over local HTTP.
[SDKs](/build/reference/sdk-quickstart/).

**membase.com (20 Oct).** The docs are at docs.membase.com, the web app at
[app.membase.com](https://app.membase.com) and the API at `https://api.app.membase.com`. The
`.ai` and `.io` web addresses redirect there; `https://api.app.membase.ai` and
`https://api.app.membase.io` keep serving the same API.

**Documentation moved (9 Oct).** These docs moved to their own site.

## September 2026

**Python and TypeScript SDKs (28 Sep).** Integrate Membase into your application with the
Python or TypeScript SDK, now on PyPI and npm. Add documents, search memories and retrieve a
profile with a developer key, or ask an agent with a subscription credential.
[Get started with the SDKs](/build/reference/sdk-quickstart/).

**Notion sources (22 Sep).** Connect Notion and select the pages to use in a Memory. After
syncing your sources, select **Update now** to process their content.
[Connect Notion](/use/bring-your-material-in/notion/).

**AI options after the free allowance (22 Sep).** Your memories remain available when your
free chat turns are used. To continue running your assistant, connect your own model in
**AI Setup** or choose a paid plan.

**Developer keys and AI connections (17 Sep).** Create keys with specific permissions,
memory access and expiry dates. Manage or revoke access at any time. In **Connect**, use the
**MCP** tab for supported AI apps or the **Skills** tab for agents that can run commands.
[Connect your AI](/connect/).

**Memory access through MCP and REST (17 Sep).** Apps connected through MCP can list and
search the Memories you approved, and read your profile when you tick **Profile access**.
Developer keys add document reading at **Read**, adding content at **Read & write**, and
removing documents or memory entries at **Full access**, where each removal needs explicit
confirmation. [API reference](/build/reference/api-reference/).

**Invitations (16 Sep).** Share your invitation link to invite others to Membase.

**Separate Home and Telegram conversations (8 Sep).** Use the same assistant memory in
Home and Telegram while keeping their conversation histories separate. Ending or deleting
one conversation does not remove the other.
