"""Flag user-guide screenshots whose anchors no longer exist in the SPA source.

    MEMBASE_SUITES=~/membase-suites python3 scripts/shots/check.py

Reads manifest.json, extracts every data-testid the callouts rely on, and greps the product
source (apps/product-web/src in the membase-suites checkout MEMBASE_SUITES points at) for it.
Exit 1 lists the shots to re-capture (and probably the pages to re-read); exit 2 means the
product source was not found, so nothing was checked.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent  # scripts/shots: this script and manifest.json
IMAGES = HERE.parents[1] / "public" / "images" / "shots"  # the published images


def _product_root() -> Path:
    """The membase-suites checkout (MEMBASE_SUITES). Without its SPA source every grep would
    fail and every shot would look stale — or, worse, a grep error would look like a pass — so
    a missing checkout stops the check instead."""
    raw = os.environ.get("MEMBASE_SUITES", "")
    root = Path(raw).expanduser().resolve() if raw else None
    if not root or not (root / "apps" / "product-web" / "src").is_dir():
        print(
            "check.py needs a membase-suites checkout: set MEMBASE_SUITES to its root "
            f"(got {raw or 'nothing'}; expected apps/product-web/src under it)",
            file=sys.stderr,
        )
        sys.exit(2)
    return root


ROOT = _product_root()
SRC = ROOT / "apps" / "product-web" / "src"


def _grep(needle: str) -> bool:
    r = subprocess.run(["grep", "-rqF", needle, str(SRC)], check=False)
    if r.returncode > 1:  # 2 = grep itself failed, which is not "not found"
        print(f"grep failed on {SRC} (exit {r.returncode})", file=sys.stderr)
        sys.exit(2)
    return r.returncode == 0


def _anchored(tid: str, prefix: bool) -> bool:
    """A testid is anchored when the source spells it out, or — for one built from a template
    literal such as `home-entry-${slug}` — when its static prefix is."""
    if _grep(tid):
        return True
    parts = tid.split("-")
    while len(parts) > 1:
        parts.pop()
        if _grep("-".join(parts) + "-${"):
            return True
    return prefix and _grep(tid)


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    stale: dict[str, list[str]] = {}
    for shot_id, shot in manifest["shots"].items():
        selectors = list(shot["selectors"]) + [shot["wait"]]
        for sel in selectors:
            m = re.search(r"data-testid(\^?=)'([^']+)'", sel)
            if not m:
                continue
            op, tid = m.groups()
            if not _anchored(tid, prefix=(op == "^=")):
                stale.setdefault(shot_id, []).append(tid)
        if not (IMAGES / shot["file"]).exists():
            stale.setdefault(shot_id, []).append("(image missing)")
    head = (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT).decode().strip()
    )
    if manifest.get("sha") != head:
        print(f"note: shots were captured at {manifest.get('sha')}, HEAD is {head}")
    if not stale:
        print("all shots anchored")
        return 0
    print("re-capture:")
    for shot_id, ids in stale.items():
        print(f"  {shot_id}: {', '.join(ids)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
