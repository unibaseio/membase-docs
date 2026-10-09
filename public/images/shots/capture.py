"""Regenerate every user-guide screenshot from the built SPA against a fresh local instance.

Run from the repo root (build the SPA first: `cd apps/product-web && npm run build`):

    PYTHONPATH=src:packages:. python3 docs/user-guide/shots/capture.py [shot-id ...]

Against a real deployment (the demo account, populated by the seed script — see CONTRIBUTING.md):

    PYTHONPATH=src:packages:. python3 docs/user-guide/shots/capture.py \
        --base-url https://www.app.membase.io --session ~/.membase-docs-demo.json --view "Lumen project"

Each shot is declared once in SHOTS: a route, what to wait for, optional clicks, and the
controls to call out. Callouts are anchored on the product's own `data-testid`s (or a text
locator when a control has none), so a re-run after a UI change moves the markers with the
control instead of leaving a stale box on a pixel position. The overlay is drawn inside the
page (a numbered badge + a brand-blue frame per target, an optional dim outside the targets)
and removed again before the next shot. `manifest.json` records, per image, the route, the
selectors and the git sha the SPA was built from — `check.py` reads it to flag shots whose
selectors no longer exist in the source tree.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from playwright.sync_api import sync_playwright  # noqa: E402
from test_ui_browser import _LOCAL, _Server, _wait_shell  # noqa: E402

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT))  # login_demo, for refreshing the demo session
VIEWPORT = {"width": 1440, "height": 900}
BRAND = "#3e61ff"


@dataclass
class Mark:
    """One callout: the control's selector and the number the text refers to."""

    selector: str
    n: int
    # note: a short label drawn beside the badge — only for the anatomy shots; steps keep the
    # words in the prose so one image serves every language.
    note: str = ""


@dataclass
class Shot:
    id: str
    route: str
    wait: str
    marks: list[Mark] = field(default_factory=list)
    # clip: a selector whose box (plus padding) becomes the image — dialogs and cards; the
    # whole viewport when empty.
    clip: str = ""
    dim: bool = False
    before: list = field(default_factory=list)  # callables (page, ctx) run after `wait`
    caption: str = ""
    remote_only: bool = False  # needs a real account (learned content, a conversation)
    local_only: bool = False  # an empty state the populated demo account no longer has


OVERLAY_JS = """
([marks, dim, brand]) => {
  document.querySelectorAll('.ug-overlay').forEach(e => e.remove());
  const root = document.createElement('div');
  root.className = 'ug-overlay';
  root.style.cssText = 'position:fixed;inset:0;z-index:2147483000;pointer-events:none;font-family:ui-sans-serif,system-ui,sans-serif';
  document.body.appendChild(root);
  const boxes = [];
  for (const m of marks) {
    let el = null;
    try { el = document.querySelector(m.selector); } catch (e) {}
    if (!el && m.selector.startsWith('text=')) {
      const t = m.selector.slice(5);
      el = [...document.querySelectorAll('button,a,[role=button],h1,h2,h3,label')].find(x => x.innerText && x.innerText.trim().startsWith(t)) || null;
    }
    if (!el) { boxes.push(null); continue; }
    const r = el.getBoundingClientRect();
    const pad = 6;
    const b = { x: r.left - pad, y: r.top - pad, w: r.width + pad * 2, h: r.height + pad * 2 };
    boxes.push(b);
    const frame = document.createElement('div');
    frame.style.cssText = `position:absolute;left:${b.x}px;top:${b.y}px;width:${b.w}px;height:${b.h}px;border:3px solid ${brand};border-radius:10px;box-shadow:0 0 0 3px rgba(255,255,255,.9), 0 6px 20px rgba(62,97,255,.25)`;
    root.appendChild(frame);
    const badge = document.createElement('div');
    badge.textContent = String(m.n);
    const by = Math.max(4, b.y - 14), bx = Math.max(4, b.x - 14);
    badge.style.cssText = `position:absolute;left:${bx}px;top:${by}px;width:28px;height:28px;border-radius:50%;background:${brand};color:#fff;font:700 15px/28px ui-sans-serif,system-ui,sans-serif;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,.25)`;
    root.appendChild(badge);
    if (m.note) {
      const note = document.createElement('div');
      note.textContent = m.note;
      const ny = b.y - 30 < 4 ? b.y + b.h + 8 : b.y - 30;
      note.style.cssText = `position:absolute;left:${Math.max(4, b.x + 18)}px;top:${ny}px;background:${brand};color:#fff;font:600 12px/20px ui-sans-serif,system-ui,sans-serif;padding:0 8px;border-radius:6px;white-space:nowrap`;
      root.appendChild(note);
      note.style.left = `${Math.max(4, Math.min(b.x + 18, innerWidth - note.offsetWidth - 4))}px`;
    }
  }
  if (dim) {
    const W = innerWidth, H = innerHeight;
    const live = boxes.filter(Boolean);
    const shade = (x, y, w, h) => {
      if (w <= 0 || h <= 0) return;
      const d = document.createElement('div');
      d.style.cssText = `position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${h}px;background:rgba(15,18,40,.42)`;
      root.appendChild(d);
    };
    if (live.length) {
      const u = { x: Math.min(...live.map(b => b.x)), y: Math.min(...live.map(b => b.y)) };
      u.r = Math.max(...live.map(b => b.x + b.w)); u.b = Math.max(...live.map(b => b.y + b.h));
      shade(0, 0, W, u.y); shade(0, u.b, W, H - u.b); shade(0, u.y, u.x, u.b - u.y); shade(u.r, u.y, W - u.r, u.b - u.y);
    }
  }
  return boxes;
}
"""


_HEADERS: dict = {}


def _json(url: str, body: dict | None = None, method: str = "GET"):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"content-type": "application/json", "user-agent": "Mozilla/5.0", **_HEADERS},
        method=method if body is None else (method if method != "GET" else "POST"),
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode() or "null")


def _sha() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT)
            .decode()
            .strip()
        )
    except Exception:  # noqa: BLE001
        return "unknown"


# ---- interactions used by shots -------------------------------------------------------------


def click(testid: str, wait_for: str | None = None, settle: int = 400):
    def run(page, ctx):
        page.get_by_test_id(testid).first.click()
        if wait_for:
            page.wait_for_selector(wait_for, timeout=15000)
        page.wait_for_timeout(settle)

    return run


def click_text(text: str, settle: int = 400):
    def run(page, ctx):
        page.get_by_role("button", name=text).first.click()
        page.wait_for_timeout(settle)

    return run


def tick(label: str):
    """Tick the checkbox whose row reads `label` (a memory in the create dialog's Reach)."""

    def run(page, ctx):
        page.locator("label", has_text=label).first.locator("input").check()
        page.wait_for_timeout(200)

    return run


def mint_screenshot_key(page, ctx):
    """Track only the temporary key created for this screenshot, for exact cleanup."""
    with page.expect_response(
        lambda r: r.request.method == "POST" and r.url.endswith("/v1/api-keys")
    ) as response:
        page.get_by_test_id("developer-key-create").click()
    minted = response.value.json()
    ctx["screenshot_key_id"] = minted["binding_id"]
    page.get_by_test_id("developer-key-done").wait_for(state="visible")


def revoke_screenshot_key(page, ctx):
    """A published example must never contain a usable developer key."""
    key_id = ctx.get("screenshot_key_id")
    if key_id:
        _json(ctx["base"] + "/v1/exposures/" + urllib.parse.quote(key_id, safe=""), method="DELETE")
        ctx.pop("screenshot_key_id")


def open_key(name: str):
    """Open the developer key whose row carries `name` (the list is newest first, so "the
    first row" would be whatever the last capture minted)."""

    def run(page, ctx):
        page.locator("[data-testid='developer-key-row']", has_text=name).first.get_by_test_id(
            "developer-key-open"
        ).click()
        page.wait_for_selector("[data-testid='key-activity-row']", timeout=15000)
        page.wait_for_timeout(1200)

    return run


def fill(testid: str, value: str):
    def run(page, ctx):
        page.get_by_test_id(testid).first.fill(value)
        page.wait_for_timeout(200)

    return run


def open_tour(page, ctx):
    if page.locator("[data-testid='setup-tour']").count():
        return
    page.get_by_test_id("home-setup-guide").click()
    page.wait_for_selector("[data-testid='setup-tour']", timeout=15000)
    page.wait_for_timeout(500)


def open_conversation(page, ctx):
    """The latest conversation, read the way its owner left it."""
    rows = page.locator("[data-testid='conversation-row']")
    if not rows.count():
        raise RuntimeError("no conversation on this account")
    # The seed's first question gets the answer worth showing (a decision recalled with its
    # reason); the rail lists newest first, so pick it by title when it is there.
    preferred = rows.filter(has_text="categorise")
    (preferred.first if preferred.count() else rows.first).click()
    page.wait_for_selector("[data-testid='mothership-assistant-message']", timeout=30000)
    page.wait_for_timeout(800)


def open_memory_entry(page, ctx):
    """Select the first learned page so the right column shows it."""
    # A page (wiki) or a fact, depending on the memory provider the account runs on.
    entries = page.locator("[data-testid='memory-entry'], [data-testid='memory-fact']")
    entries.first.wait_for(state="visible", timeout=60000)
    entries.first.click()
    page.wait_for_selector(
        "[data-testid='memory-entry-column'], [data-testid='memory-fact-column']", timeout=15000
    )
    page.wait_for_timeout(500)


def close_tour(page, ctx):
    """Dismiss the first-run guide if it is up. Its close control is the X on the card
    (`setup-skip`); the spotlight overlay can sit over it, so the click is forced."""
    # Two builds of the guide exist: the spotlight tour (`setup-tour`) and the three-step
    # dialog it replaced, still what a deployment built from main shows. Both carry the same
    # close control (aria-label "Close onboarding").
    guide = "[data-testid='setup-tour'], [role='dialog']:has-text('Create a memory')"
    for _ in range(3):
        if not page.locator(guide).count():
            break
        for sel in ("[data-testid='setup-skip']", "button[aria-label='Close onboarding']"):
            btn = page.locator(sel)
            if btn.count():
                btn.first.click(force=True, timeout=5000)
                break
        else:
            page.keyboard.press("Escape")
        try:
            page.wait_for_selector(guide, state="detached", timeout=8000)
        except Exception:  # noqa: BLE001 - try again
            pass
    page.wait_for_timeout(300)


def seed(page, ctx):
    """Two memories and a folder source, so the drive and its pages have something to show."""
    if ctx.get("seeded"):
        return
    base = ctx["base"]
    if ctx.get("remote"):
        # A real account: nothing is created here. The demo account is populated by the seed
        # script (see CONTRIBUTING.md); this only looks up what to point the shots at.
        views = _json(base + "/v1/memory-views")["views"]
        by_name = {v["name"]: v for v in views}
        pick = by_name.get(ctx.get("view_name") or "") or (views[0] if views else None)
        if not pick:
            raise RuntimeError(
                "the remote account has no memory to photograph — run the seed script first"
            )
        ctx["view_id"] = pick["id"]
        ctx["view2_id"] = next((v["id"] for v in views if v["id"] != pick["id"]), None)
        srcs = [
            c
            for c in _json(base + "/v1/connections")
            if c.get("connector") == "space-folder"
            and c.get("connection_id") in (pick.get("source_ids") or [])
        ]
        ctx["source_id"] = srcs[0]["connection_id"] if srcs else None
        subs = _json(base + "/v1/memory-listing-subscriptions")
        ctx["listing_id"] = (subs or [{}])[0].get("listing_id") if subs else None
        convs = _json(base + "/v1/conversations")
        rows = convs.get("conversations") if isinstance(convs, dict) else convs
        ctx["conversation_id"] = (rows or [{}])[0].get("id") if rows else None
        ctx["seeded"] = True
        return
    v1 = _json(
        base + "/v1/memory-views",
        {
            "name": "Project decisions",
            "query": "Decisions, conventions and open questions in this project",
        },
    )
    v2 = _json(
        base + "/v1/memory-views",
        {"name": "Reading notes", "query": "What I learned from papers and articles"},
    )
    ctx["view_id"] = v1.get("id") or v1.get("view", {}).get("id")
    ctx["view2_id"] = v2.get("id") or v2.get("view", {}).get("id")
    vault = Path(ctx["home"]) / "demo-vault"
    vault.mkdir(exist_ok=True)
    (vault / "ARCHITECTURE.md").write_text(
        "# Architecture\n\nWe chose Postgres with row-level security.\n"
    )
    (vault / "decisions.md").write_text("# Decisions\n\n- 2026-03-02: one account is one tenant.\n")
    try:
        conn = _json(
            base + "/v1/connections", {"connector": "local-folder", "config": {"path": str(vault)}}
        )
        ctx["source_id"] = conn.get("connection_id") or conn.get("id")
    except Exception as e:  # noqa: BLE001
        print("  (folder source not seeded:", str(e)[:80], ")")
    ctx["seeded"] = True


def route_view(page, ctx):
    page.goto(ctx["base"] + f"/memories?mv={ctx['view_id']}", wait_until="domcontentloaded")
    _wait_shell(page)
    page.wait_for_selector("[data-testid='view-page']", timeout=20000)
    page.wait_for_timeout(600)


def route_subscription(page, ctx):
    if not ctx.get("listing_id"):
        raise RuntimeError("the remote account has no marketplace subscription")
    page.goto(ctx["base"] + f"/memories?sub={ctx['listing_id']}", wait_until="domcontentloaded")
    _wait_shell(page)
    page.wait_for_selector("[data-testid='memory-drive']", timeout=20000)
    page.wait_for_timeout(1500)


def open_telegram_dialog(page, ctx):
    page.get_by_role("button", name="Connect Telegram").first.click()
    page.wait_for_selector(
        "[data-testid='telegram-platform-qr'], [data-testid='telegram-bind-code']", timeout=20000
    )
    page.wait_for_timeout(600)
    qr = page.locator("[data-testid='telegram-platform-qr']")
    if qr.count():
        qr.first.click()
        page.wait_for_timeout(2500)


def route_source(page, ctx):
    if not ctx.get("source_id"):
        raise RuntimeError("no folder source seeded")
    page.goto(ctx["base"] + f"/memories?source={ctx['source_id']}", wait_until="domcontentloaded")
    _wait_shell(page)
    page.wait_for_selector("[data-testid='source-page']", timeout=20000)
    page.wait_for_timeout(600)


# ---- the shots ------------------------------------------------------------------------------

SHOTS: list[Shot] = [
    Shot(
        id="tour-name-card",
        route="/app",
        wait="[data-testid='home-entries'], [data-testid='setup-tour']",
        before=[open_tour],
        caption="First run: the guide opens on a name card.",
        local_only=True,  # the spotlight tour is not on the deployed build yet
    ),
    Shot(
        id="tour-step-1",
        route="/app",
        wait="[data-testid='home-entries'], [data-testid='setup-tour']",
        before=[
            open_tour,
            click("setup-continue", "[data-testid='setup-tour'][data-lit='true']", 600),
        ],
        caption="Step 1 of the guide lights the real Add Memory card.",
        local_only=True,
    ),
    Shot(
        id="home-empty",
        route="/app",
        wait="[data-testid='home-entries']",
        before=[close_tour],
        marks=[
            Mark("[data-testid='home-entry-add-memory']", 1),
            Mark("[data-testid='home-entry-connect-your-ai']", 2),
            Mark("[data-testid='home-setup-guide']", 3),
        ],
        caption="Home: a new conversation.",
    ),
    Shot(
        id="home-anatomy",
        route="/app",
        wait="[data-testid='home-entries']",
        before=[close_tour],
        marks=[
            Mark("[data-testid='shell-nav']", 1, "Navigation"),
            Mark("[data-testid='conversation-new']", 2, "New conversation"),
            Mark("[data-testid='home-entries']", 3, "Entry cards"),
            Mark("[data-testid='mothership-composer']", 4, "Ask your assistant"),
            Mark("[data-testid='home-setup-guide']", 5, "Setup guide"),
        ],
        caption="The Home page.",
    ),
    Shot(
        id="memory-home-empty",
        route="/memories",
        wait="[data-testid='memory-home']",
        before=[close_tour],
        marks=[Mark("[data-testid='home-new-view']", 1)],
        caption="Memory before any memory exists: only the Assistant's built-in memory.",
        local_only=True,
    ),
    Shot(
        id="new-memory-dialog",
        route="/memories",
        wait="[data-testid='memory-home']",
        before=[
            close_tour,
            click("home-new-view", "[data-testid='new-group-dialog']"),
            fill("new-group-name", "Project decisions"),
        ],
        clip="[role='dialog']",
        marks=[
            Mark("[data-testid='new-group-name']", 1),
            Mark("[data-testid='new-group-create']", 2),
        ],
        caption="New memory: a name and what it keeps.",
    ),
    Shot(
        id="memory-home",
        route="/memories",
        wait="[data-testid='memory-home']",
        before=[
            seed,
            lambda p, c: (
                p.reload(wait_until="domcontentloaded"),
                _wait_shell(p),
                p.wait_for_selector("[data-testid^='view-tile-']"),
                p.wait_for_timeout(500),
            ),
        ],
        marks=[
            Mark("[data-testid^='view-tile-']", 1),
            Mark("[data-testid='home-new-view']", 2),
        ],
        caption="Memory home: one tile per memory.",
    ),
    Shot(
        id="memory-page",
        route="/memories",
        wait="[data-testid='memory-home']",
        before=[seed, route_view],
        marks=[
            Mark("[data-testid='view-run']", 1),
            Mark("[data-testid='view-settings']", 2),
            Mark("[data-testid='group-add']", 3),
        ],
        caption="A memory's page: Update now, Settings, and the Add card.",
    ),
    Shot(
        id="memory-page-anatomy",
        route="/memories",
        wait="[data-testid='memory-home']",
        before=[seed, route_view],
        marks=[
            Mark("[data-testid='view-title']", 1, "Name (click to rename)"),
            Mark("[data-testid='view-run']", 2, "Update now"),
            Mark("[data-testid='view-settings']", 3, "Settings"),
            Mark("[data-testid='view-delete']", 4, "Delete"),
            Mark("[data-testid='group-add']", 5, "Add to this memory"),
        ],
        caption="Anatomy of a memory's page.",
    ),
    Shot(
        id="memory-settings",
        route="/memories",
        wait="[data-testid='memory-home']",
        before=[
            seed,
            route_view,
            click("view-settings", "[data-testid='view-settings-dialog']", 700),
        ],
        clip="[role='dialog']",
        marks=[
            Mark("[data-testid='view-query']", 1),
            Mark("[data-testid='view-cadence-edit']", 2),
        ],
        caption="Settings: what the memory extracts, and how often.",
    ),
    Shot(
        id="source-page",
        route="/memories",
        wait="[data-testid='memory-home']",
        before=[seed, route_source],
        marks=[
            Mark("[data-testid='source-hero']", 1),
            Mark("[data-testid='source-read-by']", 2),
        ],
        caption="A folder source's page: Sync now, and which memories read it.",
    ),
    Shot(
        id="connect-page",
        route="/connect",
        wait="[data-testid='connect-page']",
        before=[seed, close_tour],
        marks=[
            Mark("[data-testid='connect-tab-mcp']", 1),
            Mark("[data-testid='connect-mcp-url']", 2),
            Mark("[data-testid='mcp-connector']", 3),
        ],
        caption="Connect, the MCP tab: the address, then the apps by purpose.",
    ),
    Shot(
        id="connect-start",
        route="/connect?tab=skills",
        wait="[data-testid='connect-skills']",
        before=[seed, close_tour],
        marks=[
            Mark("[data-testid='connect-with-key']", 1),
            Mark("[data-testid='connect-existing-key']", 2),
            Mark("[data-testid='connect-skill-zip']", 3),
            Mark("[data-testid='connect-manage-keys']", 4),
        ],
        caption="The Skills tab: Create key, an existing key, downloads and the setup guide, and Manage keys.",
    ),
    Shot(
        id="connect-claude-steps",
        route="/connect",
        wait="[data-testid='connect-page']",
        before=[
            seed,
            close_tour,
            click("client-tile-claude", "[data-testid='mcp-connector']", 600),
        ],
        marks=[Mark("[data-testid='connect-steps']", 1)],
        caption="Picking Claude unfolds the connector URL and its steps.",
    ),
    Shot(
        id="connect-developer-keys",
        route="/connect/keys",
        wait="[data-testid='developer-key-row']",
        before=[seed, close_tour],
        marks=[
            Mark("[data-testid='developer-key-new']", 1),
            Mark("[data-testid='developer-key-row'] [data-testid='developer-key-open']", 2),
            Mark("[data-testid='developer-key-row'] [data-testid='developer-key-menu']", 3),
        ],
        caption="Developer keys: one row per key — name and hint, access, reach, expiry, last use.",
        remote_only=True,  # rows, a real token and usage need a populated account
    ),
    Shot(
        id="developer-key-create",
        route="/connect/keys",
        wait="[data-testid='developer-key-new']",
        before=[
            seed,
            close_tour,
            click("developer-key-new", "[data-testid='developer-key-dialog']"),
            fill("developer-key-name", "nightly-notes script"),
            click("developer-key-profile-suggest"),
        ],
        clip="[data-testid='developer-key-dialog'] > div",
        marks=[
            Mark("[data-testid='developer-key-name']", 1),
            Mark("[data-testid='developer-key-access-suggest']", 2),
            Mark("[data-testid='developer-key-all-views']", 3),
            Mark("[role='tablist'][aria-label='Expiry']", 4),
            Mark("[data-testid='developer-key-create']", 5),
        ],
        caption="Create a developer key: the name, the access with its tools, the reach, the expiry.",
    ),
    Shot(
        id="developer-key-token",
        route="/connect/keys",
        wait="[data-testid='developer-key-new']",
        before=[
            seed,
            close_tour,
            click("developer-key-new", "[data-testid='developer-key-dialog']"),
            fill("developer-key-name", "docs shot"),
            tick("Lumen project"),
            mint_screenshot_key,
            click(
                "developer-key-test-run",
                "[data-testid='developer-key-test']:has-text('Verified')",
                600,
            ),
            revoke_screenshot_key,
        ],
        clip="[data-testid='developer-key-dialog'] > div",
        marks=[
            Mark("[data-testid='developer-key-token']", 1),
            Mark("[data-testid='developer-key-snippet-curl']", 2),
            Mark("[data-testid='developer-key-test']", 3),
        ],
        caption="The token, once — with the places to paste it and a real test call.",
        remote_only=True,  # rows, a real token and usage need a populated account
    ),
    Shot(
        id="developer-key-page",
        route="/connect/keys",
        wait="[data-testid='developer-key-row']",
        before=[
            seed,
            close_tour,
            open_key("nightly-notes script"),
        ],
        marks=[
            Mark("[data-testid='key-access']", 1),
            Mark("[data-testid='key-reach']", 2),
            Mark("[data-testid='key-expiry']", 3),
            Mark("[data-testid='key-usage']", 4),
            Mark("[data-testid='key-activity']", 5),
            Mark("[data-testid='key-rotate']", 6),
            Mark("[data-testid='key-revoke']", 7),
        ],
        caption="A key's page: access, reach, expiry, usage and recent calls; Rotate and Revoke in the hero.",
        remote_only=True,  # rows, a real token and usage need a populated account
    ),
    Shot(
        id="space-page",
        route="/files",
        wait="[data-testid='space-browser']",
        before=[seed, close_tour],
        marks=[
            Mark("text=Upload", 1),
            Mark("text=New folder", 2),
        ],
        caption="Files: the account's files. Any folder can become a source.",
    ),
    Shot(
        id="ai-setup-page",
        route="/intelligence",
        wait="[data-testid='shell-nav']",
        before=[seed, close_tour, lambda p, c: p.wait_for_timeout(1200)],
        caption="AI Setup: model sources.",
    ),
    Shot(
        id="schedules-page",
        route="/schedules",
        wait="[data-testid='shell-nav']",
        before=[seed, close_tour, lambda p, c: p.wait_for_timeout(1200)],
        caption="Schedules.",
    ),
    Shot(
        id="agents-page",
        route="/ai-connections",
        wait="[data-testid='shell-nav']",
        before=[seed, close_tour, lambda p, c: p.wait_for_timeout(1200)],
        caption="Agents.",
    ),
    Shot(
        id="activity-page",
        route="/activity",
        wait="[data-testid='shell-nav']",
        before=[seed, close_tour, lambda p, c: p.wait_for_timeout(1200)],
        caption="Activity.",
    ),
    Shot(
        id="home-conversation",
        route="/app",
        wait="[data-testid='home-entries'], [data-testid='conversation-row']",
        before=[seed, close_tour, open_conversation],
        marks=[
            Mark("[data-testid='mothership-user-message']", 1),
            Mark("[data-testid='mothership-assistant-message']", 2),
            Mark("[data-testid='mothership-activity']", 3),
        ],
        caption="A conversation: your question, the answer, and the tools the assistant used to find it.",
        remote_only=True,
    ),
    Shot(
        id="memory-entry",
        route="/memories",
        wait="[data-testid='memory-home']",
        before=[seed, route_view, open_memory_entry],
        marks=[
            Mark("[data-testid='memory-entry'], [data-testid='memory-fact']", 1),
            Mark("[data-testid='memory-entry-column'], [data-testid='memory-fact-column']", 2),
        ],
        caption="Your Memory: what the memory keeps, and one item opened.",
        remote_only=True,
    ),
    Shot(
        id="marketplace-memory",
        route="/marketplace?tab=memory",
        wait="[data-testid='shell-nav']",
        before=[seed, close_tour, lambda p, c: p.wait_for_timeout(1500)],
        marks=[
            Mark("text=Browse", 1),
            Mark("text=Your listings", 2),
            Mark("text=Purchases & subscriptions", 3),
        ],
        caption="Marketplace: the Memory part, Browse tab.",
    ),
    Shot(
        id="marketplace-list-dialog",
        route="/marketplace?tab=memory&view=mine",
        wait="[data-testid='shell-nav']",
        before=[
            seed,
            close_tour,
            lambda p, c: p.wait_for_timeout(1200),
            click_text("List a memory", 800),
        ],
        clip="[data-testid='modal'], [role='dialog']",
        caption="List a memory: what buyers see, price and allowance.",
    ),
    Shot(
        id="studio-page",
        route="/studio",
        wait="[data-testid='builder-canvas']",
        before=[close_tour, lambda p, c: p.wait_for_timeout(1500)],
        caption="Studio: an agent's canvas.",
    ),
    Shot(
        id="memory-subscribed",
        route="/memories",
        wait="[data-testid='memory-home']",
        before=[seed, route_subscription],
        caption="A memory you subscribed to: who sells it, its access period, and how your AI reads it.",
        remote_only=True,
    ),
    Shot(
        id="marketplace-subscriptions",
        route="/marketplace?tab=memory&view=subs",
        wait="[data-testid='shell-nav']",
        before=[seed, close_tour, lambda p, c: p.wait_for_timeout(1500)],
        caption="Marketplace › Purchases & subscriptions.",
        remote_only=True,
    ),
    Shot(
        id="telegram-dialog",
        route="/app",
        wait="[data-testid='home-entries'], [data-testid='conversation-row']",
        before=[close_tour, open_telegram_dialog],
        caption="Connect Telegram: generate a QR and scan it with your phone.",
    ),
    Shot(
        id="settings-page",
        route="/settings",
        wait="[data-testid='shell-nav']",
        before=[seed, close_tour, lambda p, c: p.wait_for_timeout(1200)],
        caption="Settings.",
    ),
]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="regenerate the user-guide screenshots")
    ap.add_argument("ids", nargs="*", help="shot ids to (re)capture; all when empty")
    ap.add_argument(
        "--base-url", help="photograph a running deployment instead of a fresh local instance"
    )
    ap.add_argument(
        "--session",
        help="path to a JSON file with {cookie, csrf} for --base-url (the demo account's session)",
    )
    ap.add_argument("--view", help="name of the memory to photograph on the remote account")
    a = ap.parse_args(argv)
    only = a.ids
    remote = bool(a.base_url)
    home = tempfile.mkdtemp(prefix="ug-shots-")
    srv = None
    if remote:
        base = a.base_url.rstrip("/")
        sess = json.loads(Path(a.session).read_text()) if a.session else {}
        if sess.get("cookie"):
            from login_demo import refresh_if_expired

            sess = refresh_if_expired(a.session, dict(sess, base=sess.get("base") or base))
        _HEADERS["cookie"] = f"mb_session={sess['cookie']}"
        if sess.get("csrf"):
            _HEADERS["x-csrf-token"] = sess["csrf"]
    else:
        srv = _Server(_LOCAL, {"MEMBASE_HOME": home, "MEMBASE_PROFILE": "local"})
        base = srv.url
    ctx: dict = {"srv": srv, "home": home, "base": base, "remote": remote, "view_name": a.view}
    manifest = {
        "sha": _sha(),
        "viewport": VIEWPORT,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "shots": {},
    }
    if only and (OUT / "manifest.json").exists():
        # A partial re-capture keeps the other shots' records.
        manifest["shots"] = json.loads((OUT / "manifest.json").read_text()).get("shots", {})
    failures: list[str] = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context(
                viewport=VIEWPORT, device_scale_factor=2, color_scheme="light"
            )
            if remote:
                host = urllib.parse.urlparse(base).hostname
                context.add_cookies(
                    [
                        {
                            "name": "mb_session",
                            "value": sess["cookie"],
                            "domain": host,
                            "path": "/",
                            "secure": True,
                            "httpOnly": True,
                            "sameSite": "Lax",
                        }
                    ]
                )
            page = context.new_page()
            page.set_default_timeout(20000)
            for shot in SHOTS:
                if only and shot.id not in only:
                    continue
                if (shot.remote_only and not remote) or (shot.local_only and remote):
                    continue
                print("shot", shot.id)
                try:
                    page.goto(base + shot.route, wait_until="domcontentloaded", timeout=45000)
                    _wait_shell(page)
                    page.wait_for_selector(shot.wait, timeout=30000)
                    page.wait_for_timeout(500)
                    for step in shot.before:
                        step(page, ctx)
                    marks = [{"selector": m.selector, "n": m.n, "note": m.note} for m in shot.marks]
                    boxes = page.evaluate(OVERLAY_JS, [marks, shot.dim, BRAND])
                    missing = [
                        m.selector for m, b in zip(shot.marks, boxes, strict=False) if b is None
                    ]
                    if missing:
                        failures.append(f"{shot.id}: no element for {missing}")
                    out = OUT / f"{shot.id}.png"
                    if shot.clip:
                        r = page.locator(shot.clip).first.bounding_box()
                        pad = 40
                        page.screenshot(
                            path=str(out),
                            clip={
                                "x": max(0, r["x"] - pad),
                                "y": max(0, r["y"] - pad),
                                "width": r["width"] + pad * 2,
                                "height": r["height"] + pad * 2,
                            },
                        )
                    else:
                        page.screenshot(path=str(out))
                    page.evaluate(
                        "document.querySelectorAll('.ug-overlay').forEach(e => e.remove())"
                    )
                    manifest["shots"][shot.id] = {
                        "file": out.name,
                        "route": shot.route,
                        "selectors": [m.selector for m in shot.marks],
                        "wait": shot.wait,
                        "caption": shot.caption,
                        "source": base if remote else "local",
                        "sha": manifest["sha"],
                        "generated": manifest["generated"],
                    }
                except Exception as e:  # noqa: BLE001
                    failures.append(f"{shot.id}: {str(e)[:200]}")
                    print("  FAILED", str(e)[:200])
                    try:  # what the page looked like when the step gave up
                        page.screenshot(path=str(OUT / f"{shot.id}.fail.png"))
                    except Exception:  # noqa: BLE001
                        pass
                finally:
                    revoke_screenshot_key(page, ctx)
            browser.close()
    finally:
        if srv:
            srv.close()
    manifest["source"] = base if remote else "local"
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if failures:
        print("\nproblems:")
        for f in failures:
            print(" -", f)
        return 1
    print("ok:", len(manifest["shots"]), "shots")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
