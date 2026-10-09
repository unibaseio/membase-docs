---
title: "FAQ"
---

## SDK vs MCP vs Skill?

* **SDK** — Direct Python integration for custom agents.
* **MCP** — Install the `.mcpb` bundle in MCP-compatible clients (e.g. Claude Desktop, Cline).
* **Skill** — Use as a skill in frameworks like BitAgent.

See [Integration Options](/integration-options/).

## Where is my data stored?

Raw memory lives on the [Membase Hub](https://hub.membase.unibase.com), encrypted on your machine under your Domain key before upload — the Hub only ever sees ciphertext. Recall memory (observations + retrieval index) stays on the agent's own machine. For verifiable long-term durability you can opt into the [Unibase DA storage backend](/storage-backends/) (testnet).

## Which chains does Membase work on?

Identity is **chain-agnostic** — the same wallet and signatures work on Base, BSC, or any EVM chain (see [Wallet & Identity](/identity/)). Only on-chain [Settlement](/settlement/) is per-chain, set by deployment configuration.

## Do I need Membase for AIP?

No — Membase memory is optional; [AIP](https://docs.unibase.com/aip/) agents communicate and settle without it. Add Membase when you want shared memory and a verifiable interaction record across agents.
