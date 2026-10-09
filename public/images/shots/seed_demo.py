"""Populate the docs demo account with realistic material, then learn it for real.

The demo account is a disposable wallet account on staging. Its session lives OUTSIDE the repo
in a JSON file ({base, cookie, csrf, account_id, key}); `login_demo.py` creates or refreshes it.
Everything here goes through the public API as that account: Files (folders and files), two
memories, two folder sources, a real learning run per memory and two real assistant turns —
so the screenshots show what a person would actually see.

    MEMBASE_DOCS_DEMO=~/.membase-docs-demo.json python3 docs/user-guide/shots/seed_demo.py [--no-run]

`--no-run` seeds files, memories and sources only (no model turns).
"""

from __future__ import annotations

import io
import json
import os
import sys
import time

import requests

SESSION_FILE = os.path.expanduser(os.environ.get("MEMBASE_DOCS_DEMO", "~/.membase-docs-demo.json"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from login_demo import refresh_if_expired  # noqa: E402

D = refresh_if_expired(SESSION_FILE, json.load(open(SESSION_FILE)))
base = D["base"]
host = base.split("//", 1)[1].split("/", 1)[0]
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0", "X-CSRF-Token": D["csrf"]})
s.cookies.set("mb_session", D["cookie"], domain=host)


def call(m, p, **kw):
    r = s.request(m, base + p, timeout=kw.pop("timeout", 90), **kw)
    if r.status_code >= 400:
        print("!!", m, p, r.status_code, r.text[:300])
        r.raise_for_status()
    return r.json() if r.text else None


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# A solo developer's project vault — the guide's primary reader (PRODUCT.md §1).
# File paths are case-folded by the server (a folder made as "/Lumen" lives at "/lumen"), so
# every path here is lowercase; the folder's display name keeps its case.
FILES = {
    "/lumen/README.md": """# Lumen

Lumen is a small personal-finance app I build on weekends: import bank CSV exports, categorise
transactions with rules, and show a monthly picture. Solo project, started March 2026.

Stack: Python 3.12 + FastAPI, Postgres, a React front end. Deployed on a single Hetzner box
with Caddy in front.
""",
    "/lumen/ARCHITECTURE.md": """# Architecture

- One Postgres database. Every table carries `household_id`; row-level security is on and the
  app connects as a role that cannot bypass it.
- Imports are idempotent. A transaction's identity is (account, posted date, amount, hash of
  the description), so re-importing the same CSV never doubles anything.
- Categorisation is rules first, model second. A rule that matches wins; the model only
  proposes for the leftovers and never writes a category without confirmation.
- The front end never sees raw bank descriptions in logs. Logging strips them at the API edge.
""",
    "/lumen/decisions/0001-postgres-not-sqlite.md": """# ADR 0001: Postgres, not SQLite

Date: 2026-03-14. Status: accepted.

SQLite would have been simpler for a solo app, but I want two households (mine and my parents')
on one deployment with hard isolation. Postgres row-level security gives that without writing
tenant checks in every query.

Consequence: local dev needs a Postgres too. `make db` starts one in Docker.
""",
    "/lumen/decisions/0002-rules-before-model.md": """# ADR 0002: Rules before the model

Date: 2026-04-02. Status: accepted.

Categorising with the model alone was 91% right and wrong in embarrassing ways (rent as
"entertainment"). Deterministic rules now run first; the model proposes only for what no rule
matched, and proposals sit in a review list until I confirm them.

Consequence: rules are data, kept in the `category_rules` table, editable from the UI.
""",
    "/lumen/decisions/0003-no-bank-api.md": """# ADR 0003: CSV import only, no bank API

Date: 2026-05-20. Status: accepted.

Open-banking aggregators want a company registration and charge monthly. For two households the
export-a-CSV-once-a-month routine is fine. Revisit if a third household joins.
""",
    "/lumen/CONVENTIONS.md": """# Conventions

- Money is stored as integer cents, never floats. Currency is a separate column.
- Dates are the bank's posted date, stored as `date`, never as a timestamp.
- Migrations are plain SQL files under `db/migrations/`, numbered, applied by `make migrate`.
- Tests that touch the database use a fresh schema per test module.
- Commit messages: imperative, under 72 characters, body explains why.
""",
    "/lumen/notes/2026-08-30 monthly review.md": """# Monthly review, August 2026

- Import of the DBS CSV failed on a row with a quoted comma in the description. Fixed the
  parser; added that row as a fixture.
- 14 transactions had no rule. Wrote rules for 9, confirmed model proposals for 5.
- Open question: should recurring transfers between my own accounts be hidden from the
  monthly picture? Leaning yes, as a "transfer" category excluded from totals.
- Next: a budget line per category, with the month's spend against it.
""",
    "/reading/Designing Data-Intensive Applications, ch. 7.md": """# DDIA chapter 7, Transactions

Notes from re-reading. Weak isolation levels are the norm in practice; "serializable" is rare
because of the cost. Snapshot isolation is what most databases call "repeatable read", and it
is what Postgres gives by default under that name.

Takeaway for Lumen: the import job should run in one transaction per file, not per row, so a
half-imported file never shows up in a monthly total.
""",
    "/reading/Postgres RLS in practice.md": """# Row-level security in Postgres, in practice

Article notes. Two traps: the table owner bypasses RLS unless `FORCE ROW LEVEL SECURITY` is
set, and a `SECURITY DEFINER` function runs as its owner and therefore also bypasses it.

Applied both to Lumen in April: the app role is not the owner, and there are no security
definer functions.
""",
    "/reading/Why I stopped using floats for money.md": """# Why I stopped using floats for money

Short blog post. 0.1 + 0.2 in binary floating point is not 0.3; summing a month of transactions
drifts by a cent or two. Integer minor units plus a currency code is the boring, correct answer.
Lumen has done this from the first migration.
""",
}


def main() -> int:
    log("account", D["account_id"], "at", base)

    # 1. Files: folders and files.
    for folder in ["/lumen", "/lumen/decisions", "/lumen/notes", "/reading"]:
        try:
            call("POST", "/v1/space/folders", json={"path": folder})
        except requests.HTTPError:
            pass  # already there
    for path, text in FILES.items():
        folder, name = path.rsplit("/", 1)
        r = s.post(
            base + "/v1/space/uploads",
            files={"file": (name, io.BytesIO(text.encode()), "text/markdown")},
            data={"path": folder},
            timeout=120,
        )
        log("upload", path, r.status_code, r.text[:80] if r.status_code >= 400 else "")

    # 2. Two memories.
    views = call("GET", "/v1/memory-views")["views"]

    def ensure_view(name: str, query: str) -> dict:
        for v in views:
            if v["name"] == name:
                return v
        v = call("POST", "/v1/memory-views", json={"name": name, "query": query})
        views.append(v)
        return v

    lumen = ensure_view(
        "Lumen project",
        "Decisions, conventions and open questions in the Lumen app, with the reason behind each",
    )
    reading = ensure_view(
        "Reading notes", "What I took away from each book chapter or article, and what I applied"
    )
    log("views", lumen["id"], reading["id"])

    # 3. Each folder becomes a source, attached to its memory (a union, as the UI does it).
    #    A source left over from an earlier attempt that points at a folder that does not exist
    #    is disconnected first — its learning run can only fail.
    present = {o["path"] for o in call("GET", "/v1/space/list", params={"path": "/"})["objects"]}
    for c in call("GET", "/v1/connections"):
        label = (c.get("label") or "").replace("/docs", "", 1) or "/"
        # Exact match on purpose: a source made as "/Lumen" points the agent at a folder that is
        # not there, since the folder itself lives at "/lumen".
        if (
            c.get("connector") == "space-folder"
            and c.get("status") != "disconnected"
            and label not in present
        ):
            log("disconnecting stale source", c["connection_id"], label)
            call("POST", f"/v1/connections/{c['connection_id']}/disconnect", json={})
            for v in views:
                fresh = call("GET", f"/v1/memory-views/{v['id']}")
                if c["connection_id"] in (fresh.get("source_ids") or []):
                    call(
                        "PATCH",
                        f"/v1/memory-views/{v['id']}",
                        json={
                            "source_ids": [
                                i for i in fresh["source_ids"] if i != c["connection_id"]
                            ]
                        },
                    )

    def ensure_source(path: str) -> str:
        for c in call("GET", "/v1/connections"):
            label = (c.get("label") or "").replace("/docs", "", 1) or "/"
            if (
                c.get("connector") == "space-folder"
                and label == path
                and c.get("status") != "disconnected"
            ):
                return c["connection_id"]
        r = call(
            "POST",
            "/v1/imports",
            json={"connector": "space-folder", "config": {"path": path}, "mode": "keep_synced"},
        )
        return r["connection_id"]

    src_lumen, src_reading = ensure_source("/lumen"), ensure_source("/reading")
    log("sources", src_lumen, src_reading)
    for v, sid in [(lumen, src_lumen), (reading, src_reading)]:
        fresh = call("GET", f"/v1/memory-views/{v['id']}")
        ids = list({*(fresh.get("source_ids") or []), sid})
        call("PATCH", f"/v1/memory-views/{v['id']}", json={"source_ids": ids})
    for _ in range(60):
        conns = {c["connection_id"]: c for c in call("GET", "/v1/connections")}
        st = [conns[i].get("status") for i in (src_lumen, src_reading)]
        log("sync status", st)
        if all(x not in ("pending", "syncing", "queued") for x in st):
            break
        time.sleep(5)

    # 3b. Two developer keys, so Connect › Developer keys has rows to photograph: one that has
    #     done some work (a few real calls, one of them refused, so the key page's usage and
    #     activity are populated) and one that expires. Keys the capture run itself made
    #     ("docs shot") are revoked here so they do not pile up.
    keys = [
        e for e in call("GET", "/v1/exposures")["exposures"] if e.get("subject_kind") == "apikey"
    ]
    live = {e["name"]: e for e in keys if e.get("status") not in ("revoked", "disconnected")}
    for e in keys:
        if e["name"] == "docs shot" and e.get("status") not in ("revoked",):
            call("DELETE", f"/v1/exposures/{e['id']}")
    if "nightly-notes script" not in live:
        k = call(
            "POST",
            "/v1/api-keys",
            json={
                "name": "nightly-notes script",
                "profile": "suggest",
                "view_ids": [lumen["id"]],
                "profile_access": True,
            },
        )
        bearer = {"Authorization": f"Bearer {k['token']}"}
        for _ in range(3):
            s.get(base + "/v1/containers", headers=bearer, timeout=60)
        s.post(
            base + "/v1/search",
            headers=bearer,
            json={"q": "how are money amounts stored"},
            timeout=180,
        )
        s.post(
            base + "/v1/search",
            headers=bearer,
            json={"q": "x", "container": reading["id"]},
            timeout=60,
        )  # refused: out of reach
        s.delete(
            base + "/v1/documents/doc-nope", headers=bearer, params={"confirm": "true"}, timeout=60
        )  # refused: above the level
        log("key", k["binding_id"], k["token_hint"])
    if "ci — docs indexer" not in live:
        k = call(
            "POST",
            "/v1/api-keys",
            json={
                "name": "ci — docs indexer",
                "profile": "read",
                "view_ids": [reading["id"]],
                "profile_access": False,
                "expires_in_days": 90,
            },
        )
        log("key", k["binding_id"], k["token_hint"], "expires", k["expires_at"])

    if "--no-run" in sys.argv:
        log("done (no runs)")
        return 0

    # 4. Learn for real: one run per memory, the same call the Run button makes.
    def run(
        agent_id: str, instruction: str = "", conversation_id: str | None = None, timeout: int = 900
    ) -> dict:
        body: dict = {"instruction": instruction, "wait": False}
        if conversation_id:
            body["conversation_id"] = conversation_id
        r = call("POST", f"/v1/agent-definitions/{agent_id}/run", json=body, timeout=120)
        t0 = time.time()
        while r["status"] in ("running", "pending", "queued") and time.time() - t0 < timeout:
            time.sleep(5)
            r = call("GET", f"/v1/agent-runs/{r['id']}")
        log(
            "run",
            agent_id,
            r["status"],
            (r.get("reason") or "")[:120],
            str((r.get("output") or {}).get("answer", ""))[:160],
        )
        return r

    #    A memory whose last run already read the current sources is left alone; one whose run
    #    failed (a cold box can drop the first attempt) is tried up to three times.
    for v in (lumen, reading):
        fresh = call("GET", f"/v1/memory-views/{v['id']}")
        for attempt in range(3):
            state = call("GET", f"/v1/memory-views/{v['id']}/learning")
            if state.get("last_success_at") and not state.get("pending_source_ids"):
                log("learned already", v["name"], state.get("last_success_at"))
                break
            r = run(fresh["agent_id"])
            if r["status"] == "succeeded":
                break
            log("retrying", v["name"], attempt + 1)
        log("learning", str(call("GET", f"/v1/memory-views/{v['id']}/learning"))[:300])

    # 5. The assistant consults both memories (the same field the memories chip on Home's
    #    composer sets), then two real conversations so Home has a transcript to show. Ones
    #    from an earlier attempt (asked before the memory had learned anything) are forgotten.
    assistant = call("GET", "/v1/assistant")
    wanted = [lumen["id"], reading["id"]]
    if sorted(assistant.get("memory_view_ids") or []) != sorted(wanted):
        call("PATCH", f"/v1/agent-definitions/{assistant['id']}", json={"memory_view_ids": wanted})
        log("assistant now consults", wanted)
    titles = {
        "Lumen app: how do I categorise transactions?": "In my Lumen app (the personal-finance side project), what did I decide about how transactions get categorised, and why? Keep it short.",
        "Lumen app: money storage convention": "In my Lumen app, how are money amounts stored? One sentence, from my own conventions.",
    }
    for c in call("GET", "/v1/conversations"):
        if c.get("title") in titles or c.get("title") in (
            "Lumen: what did I decide about categorisation?",
            "Money storage convention",
        ):
            log("forgetting stale conversation", c["id"])
            call(
                "DELETE", f"/v1/conversations/{c['id']}", params={"confirm": "forget"}, timeout=180
            )
    for title, question in titles.items():
        conv = call("POST", "/v1/conversations", json={"title": title})
        r = run(assistant["id"], question, conv["id"])
        # The web surface files both lines of a turn on the conversation itself (the agent keeps
        # its own session; the transcript the page shows is these rows), so do the same here.
        out = r.get("output") or {}
        answer = str(out.get("answer") or out.get("text") or "").strip()
        call(
            "POST",
            f"/v1/conversations/{conv['id']}/messages",
            json={"role": "user", "text": question},
        )
        if answer:
            call(
                "POST",
                f"/v1/conversations/{conv['id']}/messages",
                json={
                    "role": "assistant",
                    "text": answer,
                    "run_id": r.get("id"),
                    "usage": r.get("usage"),
                    "activity": out.get("activity") or out.get("steps"),
                },
            )
    log("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
