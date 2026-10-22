---
title: "Benchmarks"
description: "LoCoMo, LongMemEval_S and DMR results for the local Membase engine (unibaseio-membase-core), with the method behind each number."
---

LoCoMo, LongMemEval_S and DMR results for the local Membase engine (unibaseio-membase-core), with the method behind each number.

This report covers `unibaseio-membase-core`, the engine that `pip install 'unibaseio-membase[local]'`
runs on your machine. The hosted Membase service does not run this engine today, so these
scores and latency figures are not measurements of the hosted Membase API, account startup,
or an end-to-end app task.
For hosted search behavior and timeouts, see [How Membase works](/build/concepts/how-membase-works/)
and [API troubleshooting](/build/reference/troubleshooting/).

The engine is measured on three public long-term-memory benchmarks:
**LoCoMo**, **LongMemEval_S** and **DMR**. Each accuracy number below is one pass over the full
question set, graded by a gpt-4o-mini judge with one prompt per benchmark; the latency and context-token rows come from
the timing samples noted under the latency table. Powered by episodic extraction and multi-round
retrieval that sends the reader a few thousand tokens instead of the whole history.

| | LoCoMo | LongMemEval_S | DMR |
|---|---|---|---|
| **Accuracy** | **93.1%** | **92.6%** | **92.2%** |
| Questions | 1,540 | 500 | 500 |
| Context tokens per question (mean over the timing sample) | 6,562 | 8,970 | 1,602 |
| Full history per question | ~20k | ~103k | — |
| Token reduction | 3× | 11× | — |
| Reader model | gpt-4.1-mini | gpt-5.5 | gpt-4o-mini |

## LoCoMo

1,540 questions in four categories: single-hop, multi-hop, open-domain and temporal recall
across multi-session conversations spanning months.

| Category | Questions | Accuracy |
|---|---|---|
| single-hop | 841 | 94.6% |
| multi-hop | 282 | 93.6% |
| temporal | 321 | 91.6% |
| open-domain | 96 | 83.3% |
| **overall** | **1,540** | **93.1%** |

Mean context over the 40-question timing sample: 6,562 tokens, three times below the full history. 98.1% of the evidence sessions
reach the reader. Swapping the reader model moves the score by less than
0.1 points.

## LongMemEval_S

500 questions in six types. Each question comes with its own 103k-token, roughly 50-session
history; the reader sees only what memory retrieves.

| Question type | Questions | Accuracy |
|---|---|---|
| single-session preference | 30 | 100% |
| single-session user | 70 | 98.6% |
| knowledge update | 78 | 97.4% |
| temporal reasoning | 133 | 92.5% |
| multi-session | 133 | 88.0% |
| single-session assistant | 56 | 85.7% |
| **overall** | **500** | **92.6%** |

Mean context over the 30-question timing sample: 8,970 tokens, eleven times below the full history. 99.95% of the evidence
sessions are retrieved, and 99.8% of questions get every one of theirs. 29 of the 30 unanswerable questions were correctly
abstained.

## DMR

MemGPT's Deep Memory Retrieval set: 500 questions, five sessions each, run in Zep's harness
with MemGPT's judge prompt and gpt-4o-mini as reader and judge.

| Outcome | Questions | Share |
|---|---|---|
| correct | 461 | 92.2% |
| abstained | 4 | 0.8% |
| lost a detail in extraction | 35 | 7.0% |

Mean context over the 30-question timing sample: 1,602 tokens.

## Latency and tokens

| | LoCoMo | LongMemEval_S | DMR |
|---|---|---|---|
| search latency, p50 / p95 | 1.67 s / 7.02 s | 2.53 s / 6.11 s | 1.13 s / 1.71 s |
| end-to-end, p50 / p95 | 8.30 s / 18.0 s | 14.7 s / 30.2 s | 3.21 s / 6.34 s |
| context tokens per question (mean) | 6,562 | 8,970 | 1,602 |

The latency and context-token rows were measured on samples, not the full sets: 40 LoCoMo questions, 30
LongMemEval_S and 30 DMR, timed serially on 2026-09-21. In these runs, search takes 1.1 to
2.5 s at the median, including one to three decider rounds. End to end is 3 to 15 s at the
median depending on the reader model. These figures exclude hosted runtime wake-up and are
not a service latency guarantee.

## Why the numbers look this way

Each score traces back to a specific part of the architecture.

* **Recall correctness.** Every session is narrated into timestamped episodes that keep who, what and when together, so a fact is retrieved with its context. The retrieval decider reads the first hits and asks follow-up questions before settling, which is why 99.95% of LongMemEval_S evidence sessions are in context.
* **Context footprint.** Keyword and vector search are fused by reciprocal rank and only the top twenty episodes enter the prompt. That keeps a LongMemEval_S call at about 9,000 tokens against a 103k-token history, and a LoCoMo call at about 6,500 against 20k.
* **Response time.** One to three decider rounds per search, each a short call; the reader model dominates end-to-end time.

## What is inside

Four pieces working together.

| | |
|---|---|
| **Boundary detection** | An LLM pass splits each session into topical cells before extraction, so one episode never straddles two subjects. |
| **Episodic extraction** | Each cell becomes a titled, timestamped narrative from the user's point of view. Optional profile, fact and foresight layers sit beside it. |
| **Multi-round retrieval** | Hybrid search per sub-query, fused by reciprocal rank; a decider marks core evidence and issues new queries for up to three rounds. |
| **Local-first store** | SQLite and FAISS on disk, scoped per user, with any OpenAI-compatible model for extraction, retrieval and answering. |

## Method

* **Grading.** gpt-4o-mini judges every benchmark, with one prompt each: Memori's CORRECT/WRONG prompt for LoCoMo, the same prompt plus LongMemEval's official per-type rules for LongMemEval_S, and MemGPT's prompt in Zep's harness for DMR. Every question in the set is counted once; a failed call is graded wrong.
* **No re-runs.** Each accuracy number is one pass over the full question set. No best-of-N, no merging of re-runs. Each benchmark has one answer prompt; none carries rules for individual questions.
* **Models.** OpenAI only: gpt-4.1-mini for extraction and retrieval decisions, text-embedding-3-small for vectors, and the reader listed per benchmark. The same stores answer with any OpenAI-compatible model.
* **Reproducing.** The harness, dataset loaders, judge configuration and run commands live in [membase-bench](https://github.com/unibaseio/membase-bench), pinned to `unibaseio-membase-core==0.3.0`. The published numbers come from runs on 18–21 September 2026, before any engine release; 0.3.0 was released on 11 October.

## Which benchmark matters

LoCoMo tests recall across a long two-person history. LongMemEval_S tests finding one fact in a
103k-token haystack and updating or abstaining correctly. DMR tests the fidelity of what was
extracted. A memory system needs all three, which is why each is reported separately.

## How this differs from RAG over the transcript

Raw chunks lose who said what and when. Episodes are written with speaker, time and context
attached, and retrieval can ask follow-up questions instead of taking the first top-k.

*Benchmark report, September 2026.*
