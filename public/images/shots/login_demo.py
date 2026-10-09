"""Create or refresh the docs demo account's session on a deployment.

The demo account is a disposable wallet account. Its private key and current session are kept
in one JSON file OUTSIDE the repo (default ~/.membase-docs-demo.json, override with
MEMBASE_DOCS_DEMO). Run this when the session has expired (two weeks) or to mint a fresh
account; then `seed_demo.py` to populate it and `capture.py --base-url … --session …` to shoot.

    python3 docs/user-guide/shots/login_demo.py [--base-url https://www.app.membase.io] [--new]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import requests
from eth_account import Account
from eth_account.messages import encode_defunct


def sign_in(base: str, key: str | None = None) -> dict:
    """Sign the demo wallet in (a fresh wallet when `key` is None) and return the session
    record the other scripts read: {base, address, key, account_id, cookie, csrf, expires_at}."""
    wallet = Account.from_key(key) if key else Account.create()
    base = base.rstrip("/")
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0"
    challenge = s.post(
        base + "/v1/auth/wallet/challenge", json={"address": wallet.address}, timeout=30
    ).json()["message"]
    signature = wallet.sign_message(encode_defunct(text=challenge)).signature.hex()
    r = s.post(
        base + "/v1/auth/wallet/session",
        json={"message": challenge, "signature": signature},
        timeout=60,
    )
    r.raise_for_status()
    j = r.json()
    return {
        "base": base,
        "address": wallet.address,
        "key": wallet.key.hex(),
        "account_id": j["account_id"],
        "cookie": s.cookies.get("mb_session"),
        "csrf": j["csrf_token"],
        "expires_at": j.get("expires_at"),
    }


def save_session(path: str, out: dict) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(out, f, indent=2)


def refresh_if_expired(path: str, session: dict) -> dict:
    """The saved session, or a fresh one signed with the saved wallet when the cookie no longer
    opens the account — so a two-week-old session file never stops a capture or a seed."""
    base = session["base"].rstrip("/")
    host = base.split("//", 1)[1].split("/", 1)[0]
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0"
    s.cookies.set("mb_session", session.get("cookie") or "", domain=host)
    if s.get(base + "/v1/account", timeout=30).status_code != 401:
        return session
    if not session.get("key"):
        raise SystemExit(
            f"the demo session in {path} has expired and holds no wallet key; run login_demo.py --new"
        )
    fresh = sign_in(base, session["key"])
    save_session(path, fresh)
    print(
        f"demo session refreshed: {fresh['account_id']} until {fresh.get('expires_at')}", flush=True
    )
    return fresh


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--base-url", default="https://www.app.membase.io", help="the SPA origin (it proxies /v1)"
    )
    ap.add_argument(
        "--new",
        action="store_true",
        help="mint a fresh wallet (a new account) instead of reusing the saved one",
    )
    a = ap.parse_args()
    path = os.path.expanduser(os.environ.get("MEMBASE_DOCS_DEMO", "~/.membase-docs-demo.json"))
    saved = {} if a.new or not os.path.exists(path) else json.load(open(path))
    out = sign_in(a.base_url, saved.get("key"))
    save_session(path, out)
    print(
        f"signed in as {out['account_id']} on {out['base']}; session until {out.get('expires_at')}; saved to {path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
