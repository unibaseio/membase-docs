---
title: "Troubleshooting"
---

## Common Issues

### "Permission denied" / Auth errors

* Check the agent's key env is set — `MEMBASE_PRIVATE_KEY`.
* Read access is by **domain** membership — confirm the wallet was invited to the domain (see [Domains & Encryption](/authorization/)).

### Connection / Timeout errors

* Check your network can reach the Hub endpoint (and the Server URL, if you use one).
* For firewall/proxy environments, ensure outbound HTTPS is allowed.

### Import errors (Python)

* Create a fresh virtual environment: `python -m venv venv && source venv/bin/activate`
* Reinstall the SDK: `pip install --upgrade "unibase-membase-sdk @ git+https://github.com/unibaseio/unibase-membase.git"`

## Memory & Recall

### `memory.ingest` / `memory.answer` raises ImportError

* These need the LLM extras: `pip install "unibase-membase-sdk[recovery,runtime]"`.
* `memory.ingest` also needs an LLM key (e.g. `OPENAI_API_KEY`); raw `set`/`get` do not.

### Recall returns nothing / stale results

* Pass the right `query_date` — observations are filtered to those valid at that date, so a current fact won't show for a past date (and vice versa).
* Confirm the session was ingested (`memory.ingest(...)`) before querying; recall reads the local store, not raw turns.

### "value not encrypted under this domain" on read

* You're decrypting with the wrong domain key. Read with the correct domain handle, and name the `author` whose value you want (`get(key, author=...)`).
* For shared domains, ensure the wallet **accepted the invite** (`accept_invite`) so it holds the domain key.

### Hub write/read appears to do nothing

* Writes are wallet-signed; verify the agent's wallet/key is set and the Hub URL is reachable.
* The Hub returns the latest value per `(owner, id)` — re-writing the same key overwrites; use distinct keys for history.

## Settlement & metering (Membase Server)

* Metering/settlement require a **Server URL** — agent-direct memory works without one.
* On-chain flush needs the wallet funded with gas on the settlement chain and the configured token (e.g. `UB`); a stuck flush is usually insufficient allowance/balance.

## Getting Help

* [Telegram Community](https://t.me/unibase_ai)
* [Support Email](mailto:support@unibase.com)
* [GitHub Issues](https://github.com/unibaseio) — report bugs per repository
