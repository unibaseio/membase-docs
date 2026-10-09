---
title: "OpenAI API"
description: "The user's memory behind the OpenAI API or any function-calling model: declare search_memories and add_memory as functions and call the SDK when the model asks."
---

The user's memory behind the OpenAI API or any function-calling model: declare search_memories and add_memory as functions and call the SDK when the model asks.

Everything below assumes `MEMBASE_API_KEY` in the environment, minted at **Read & write**
with **Your profile** ticked ([Authentication & Scopes](/build/reference/authentication/)), and your model
provider's key beside it. The loop is the same in every harness:

![Read the profile once, search per question, answer citing the container, then save what the person supplied so the next search finds it](/images/figures/core-loop.svg)

## The tool-calling loop

Declare the two verbs as functions and call the SDK when the model asks. The shape is the
Chat Completions tool-calling loop; any provider with the same loop takes the same two
definitions.

```ts
import OpenAI from "openai";
import { Membase } from "membase-sdk";

const memory = new Membase();
const openai = new OpenAI();

const tools: OpenAI.Chat.Completions.ChatCompletionTool[] = [
  { type: "function", function: {
      name: "search_memories",
      description: "Search the user's memory. Use it before answering anything about their past work, decisions or preferences.",
      parameters: { type: "object", properties: { q: { type: "string" } }, required: ["q"] } } },
  { type: "function", function: {
      name: "add_memory",
      description: "Save one fact the user asked to remember, in their own words.",
      parameters: { type: "object", properties: { content: { type: "string" } }, required: ["content"] } } },
];

async function runTool(name: string, args: Record<string, string>): Promise<string> {
  if (name === "search_memories") {
    const { results } = await memory.search({ q: args.q, limit: 5 });
    return JSON.stringify(results.map((h) => ({ memory: h.container_name, content: h.content })));
  }
  await memory.memories.add({ content: args.content });
  return "saved";
}

const profile = await memory.profile();
const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
  { role: "system", content: "Standing facts about the user: " + profile.static.join("; ") },
  { role: "user", content: "What did we decide about the ledger?" },
];

for (;;) {
  const turn = await openai.chat.completions.create({ model: process.env.OPENAI_MODEL!, messages, tools });
  const reply = turn.choices[0].message;
  messages.push(reply);
  if (!reply.tool_calls?.length) { console.log(reply.content); break; }
  for (const call of reply.tool_calls) {
    if (call.type !== "function") continue;          // tool_calls is a union; custom tool calls carry no `function`
    const content = await runTool(call.function.name, JSON.parse(call.function.arguments));
    messages.push({ role: "tool", tool_call_id: call.id, content });
  }
}
```

The same loop in Python is the SDK's `client.search(...)` and `client.memories.add(...)`
behind two function definitions; nothing else changes.


## Rules that hold in every shape

* **Profile once, search per question.** The profile is small and standing; search is a turn inside the user's container.
* **Cite the container.** Every hit names `container_name`; say where an answer came from.
* **Save what the user supplied,** in their words, and only when they asked or plainly meant to.
* **Never confirm on your own.** A delete or forget without `confirm=true` answers with a `how` sentence; relay it and stop.
* **Treat `403` as withdrawn access.** The owner narrowed or revoked the key; do not retry with it.
* **Expect the first search to be slow.** Up to a minute after a quiet spell; keep the SDK's timeout.

The same rules, with the reasons, are on [Memory operations](/build/guides/memory-operations/#rules-of-the-road).
