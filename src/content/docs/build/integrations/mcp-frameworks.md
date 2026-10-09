---
title: "MCP frameworks"
description: "An agent framework with an MCP client needs no Membase-specific code: the server URL and the key as a header, and it discovers the tools. Without a framework, the OpenAPI document generates a typed client."
---

An agent framework with an MCP client needs no Membase-specific code: the server URL and the key as a header, and it discovers the tools. Without a framework, the OpenAPI document generates a typed client.

## Give the framework the server

A framework with an MCP client (LangChain's MCP adapters, the OpenAI Agents SDK, Pydantic AI,
Mastra, and most others) needs no Membase-specific code. Give it the server as a Streamable
HTTP endpoint with the key in the header:

```json
{ "url": "https://api.app.membase.io/mcp-http",
  "headers": { "Authorization": "Bearer mbk_…" } }
```

It discovers the key's tools with `tools/list` and calls them by the names in the
[API Reference](/build/reference/api-reference/). Where the framework's own MCP client speaks OAuth, leave
the header out and the user consents in the browser instead; the connection is then
read-only, which is what a user-facing agent usually wants.


A user-facing agent whose end users each hold their own Membase account connects by consent
instead, one account at a time; [Multi-user isolation](/build/guides/multi-user-isolation/) has the
patterns.

## Without an SDK

Any HTTP client works, and the OpenAPI document generates a typed client for any language:

```bash
curl -s https://www.app.membase.io/plugin/openapi/agent-protocol.json -o agent-protocol.json
npx openapi-typescript agent-protocol.json -o membase.d.ts
```

Three requests cover most integrations: `GET /v1/profile`, `POST /v1/search` with `{"q": …}`
and `POST /v1/memories` with `{"content": …}`, each with the bearer header.

## Rules that hold in every shape

* **Profile once, search per question.** The profile is small and standing; search is a turn inside the user's container.
* **Cite the container.** Every hit names `container_name`; say where an answer came from.
* **Save what the user supplied,** in their words, and only when they asked or plainly meant to.
* **Never confirm on your own.** On a Full access key, a delete or forget without `confirm=true` answers with a `how` sentence; relay it and stop.
* **Treat `403` as withdrawn access.** The owner narrowed or revoked the key; do not retry with it.
* **Expect the first search to be slow.** Up to a minute after a quiet spell; keep the SDK's timeout.

The same rules, with the reasons, are on [Memory operations](/build/guides/memory-operations/#rules-of-the-road).
