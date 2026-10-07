"""Cookie-banner handling with DuckDuckGo autoconsent (vendored, MPL-2.0).

Message protocol and rule filtering follow tracker-radar-collector's
CookiePopupsCollector (Apache-2.0, see NOTICE): autoconsent starts with
autoAction=null, reports `popupFound`, and only then do we send optIn/optOut.
In "none" mode we only record whether a CMP/popup exists and never click.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from ..contracts import ConsentInfo

if TYPE_CHECKING:
    from playwright.async_api import BrowserContext, Frame

VENDOR = Path(__file__).parent / "vendor" / "autoconsent"
MODES = ("none", "optIn", "optOut")


@lru_cache(maxsize=1)
def _bundle() -> str:
    return (VENDOR / "autoconsent.playwright.js").read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _compact() -> dict:
    return json.loads((VENDOR / "compact-rules.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _full_rules_json() -> str:
    return json.dumps({"autoconsent": json.loads((VENDOR / "rules.json").read_text(encoding="utf-8"))["autoconsent"]})


def _should_run(rule: list, main_frame: bool, url: str) -> bool:
    run_context = rule[4]
    if main_frame and run_context == 1:
        return False
    if not main_frame and run_context in (20, 22, 10, 12):
        return False
    pattern = rule[3]
    if pattern:
        try:
            if re.search(pattern, url) is None:
                return False
        except re.error:
            return False
    return True


def filter_compact_rules(url: str, main_frame: bool) -> dict:
    """Python port of autoconsent's filterCompactRules (keeps the full string table)."""
    rules = _compact()
    v, s, r, index = rules["v"], rules["s"], rules["r"], rules["index"]
    if not main_frame:
        a, b = index["frameRuleRange"]
        return {"v": v, "s": s[: index["frameStringEnd"]], "r": [x for x in r[a:b] if _should_run(x, False, url)]}
    ga, gb = index["genericRuleRange"]
    sa, sb = index["specificRuleRange"]
    specific = [x for x in r[sa:sb] if _should_run(x, True, url)]
    if specific:
        return {"v": v, "s": s, "r": r[ga:gb] + specific}
    return {"v": v, "s": s[: index["genericStringEnd"]], "r": r[ga:gb]}


class ConsentBridge:
    """One per browser context. Collects results into `self.info`."""

    def __init__(self, mode: str = "none"):
        if mode not in MODES:
            raise ValueError(f"consent mode must be one of {MODES}")
        self.mode = mode
        self.info = ConsentInfo(mode=mode)

    async def install(self, context: "BrowserContext") -> None:
        await context.expose_binding("autoconsentSendMessage", self._on_message)
        await context.add_init_script(_bundle())

    async def _send(self, frame: "Frame", msg_js: str) -> None:
        try:
            await frame.evaluate(f"autoconsentReceiveMessage({msg_js})")
        except Exception:
            pass  # frame detached / navigated

    async def _on_message(self, source: dict, msg: dict) -> None:
        if not isinstance(msg, dict):
            return
        frame: Frame = source["frame"]
        kind = msg.get("type")
        if kind == "init":
            main = frame.parent_frame is None
            config = {
                "enabled": True,
                "autoAction": None,  # we trigger the action ourselves after popupFound
                "disabledCmps": [],
                "enablePrehide": False,
                # Cosmetic hiding changes the page; only allowed when we act on banners.
                "enableCosmeticRules": self.mode != "none",
                "enableHeuristicDetection": True,
                "heuristicMode": "tier2",
                "detectRetries": 20,
                "isMainWorld": False,
            }
            if self.mode == "optIn":  # compact rules omit opt-in steps
                rules = _full_rules_json()
            else:
                rules = json.dumps({"autoconsent": [], "compact": filter_compact_rules(msg.get("url") or frame.url, main)})
            await self._send(frame, f'{{"type":"initResp","config":{json.dumps(config)},"rules":{rules}}}')
        elif kind == "eval":
            result = False
            try:
                result = bool(await frame.evaluate(msg.get("code", "false")))
            except Exception:
                pass
            await self._send(frame, json.dumps({"id": msg.get("id"), "type": "evalResp", "result": result}))
        elif kind == "cmpDetected":
            self.info.cmp_detected = self.info.cmp_detected or msg.get("cmp")
        elif kind == "popupFound":
            self.info.popup_found = True
            self.info.cmp_detected = self.info.cmp_detected or msg.get("cmp")
            if self.mode in ("optIn", "optOut"):
                await self._send(frame, json.dumps({"type": self.mode}))
        elif kind in ("optInResult", "optOutResult"):
            if self.info.action_result is not True:
                self.info.action_result = bool(msg.get("result"))
        elif kind == "autoconsentError":
            self.info.errors.append(str(msg.get("details"))[:300])
