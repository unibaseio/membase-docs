---
title: "Build with Membase"
description: "Start with one working API call sequence, then learn memory operations, integrate your model, and look up SDK and API details."
---

Start with one working API call sequence, then learn memory operations, integrate your model, and look up SDK and API details.

Use Membase from code to add material to a person's memory and retrieve it for your app.
Calls use that person's developer key and the Memories they grant it. Python, TypeScript
and REST all reach the same service at `https://api.app.membase.io`.

**Start with the [quickstart](/build/getting-started/api-quickstart/).** It creates one document, waits for learning
to finish, and searches the result. The example includes the checks needed to distinguish an
empty Memory from a failed search.

## Choose your next task

| Task | Guide |
|---|---|
| Add facts or documents, search, read the profile, forget or delete | [Memory operations](/build/guides/memory-operations/) |
| Serve multiple people | [Multi-user isolation](/build/guides/multi-user-isolation/) |
| Configure timeouts, retries or SDK methods | [SDKs](/build/reference/sdk-quickstart/) |
| Set access and reach, rotate or revoke a credential | [Authentication](/build/reference/authentication/) |
| Look up an endpoint or response shape | [API reference](/build/reference/api-reference/) |
| Fix a failed request or unread document | [API troubleshooting](/build/reference/troubleshooting/) |

## Integrations

| Your application | Guide |
|---|---|
| Claude API | [Claude API](/build/integrations/claude-api/) |
| OpenAI API or a function-calling model | [OpenAI API](/build/integrations/openai-api/) |
| An agent framework that speaks MCP | [MCP frameworks](/build/integrations/mcp-frameworks/) |
| A coding assistant building the integration for you | [AI coding assistants](/build/integrations/ai-coding-tools/) |

If you want to give an existing AI app your memory without building an integration, use
[Connect your AI](/connect/).

## Understand the model

In the API, a **container** is one *Memory* in the app, a **document** is raw material it
reads, and a **memory** is a learned fact or a profile fact. A container is not an end user.

[Platform overview](/build/concepts/platform-overview/) maps these objects to the app.
[How Membase works](/build/concepts/how-membase-works/) explains learning, retrieval and model requirements.
The [engine benchmark report](/evaluation/benchmarks/) is separate from API setup and performance guidance.
