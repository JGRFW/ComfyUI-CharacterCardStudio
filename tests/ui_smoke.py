# -*- coding: utf-8 -*-
"""Headless browser smoke test for the ComfyUI workbench."""

from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


URL = os.environ.get("CCS_TEST_URL", "http://127.0.0.1:8199")
IMAGE = os.environ.get(
    "CCS_TEST_IMAGE",
    r"K:\6.人物多视图\22785d770f0efdcf632f8e8a954a4b05032b63a4ac5a92e74da551fed6020ab2.jpg",
)
OUT = Path(__file__).resolve().parents[1] / "_ui_test"
OUT.mkdir(exist_ok=True)


def main() -> None:
    errors: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1500, "height": 1000})
        page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
        page.on(
            "console",
            lambda message: errors.append(f"console {message.type}: {message.text}")
            if message.type == "error"
            else None,
        )
        page.goto(URL, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_function("() => Boolean(window.app && window.app.graph)", timeout=120_000)
        created = page.evaluate(
            """() => {
                const type = "AICG3D_CharacterCardStudio";
                const node = globalThis.LiteGraph.createNode(type);
                if (!node) return { ok: false, reason: "node type missing" };
                window.app.graph.add(node);
                node.pos = [80, 80];
                window.app.canvas.setZoom(0.78);
                window.app.canvas.selectNode(node, false);
                window.app.canvas.centerOnNode(node);
                window.app.graph.setDirtyCanvas(true, true);
                return { ok: true, type: node.type, title: node.title };
            }"""
        )
        page.wait_for_selector(".ccs-root", timeout=60_000)
        page.wait_for_timeout(1200)
        page.evaluate(
            """() => {
                const node = window.app.graph._nodes.find((item) => item.type === 'AICG3D_CharacterCardStudio');
                if (!node) return;
                window.app.canvas.setZoom(0.72);
                window.app.canvas.centerOnNode(node);
                node.setDirtyCanvas(true, true);
            }"""
        )
        page.wait_for_timeout(500)
        page.locator(".ccs-root").screenshot(path=str(OUT / "desktop_default.png"))

        page.set_input_files(".ccs-root input[type=file]", IMAGE)
        page.wait_for_timeout(5000)
        page.select_option(".ccs-topbar select", "scene_six_view")
        page.wait_for_timeout(1200)
        before_drag = page.locator(".ccs-cell-caption").nth(0).inner_text()
        page.locator(".ccs-cell").nth(0).drag_to(page.locator(".ccs-cell").nth(2))
        page.wait_for_timeout(700)
        after_drag = page.locator(".ccs-cell-caption").nth(2).inner_text()
        page.locator(".ccs-root").screenshot(path=str(OUT / "desktop_profile.png"))

        summary = page.evaluate(
            """() => {
                const root = document.querySelector(".ccs-root");
                const rect = root.getBoundingClientRect();
                return {
                    cells: root.querySelectorAll(".ccs-cell").length,
                    images: root.querySelectorAll(".ccs-cell img").length,
                    library: root.querySelectorAll(".ccs-thumb").length,
                    template: root.querySelector(".ccs-topbar select")?.value,
                    compact: root.classList.contains("is-compact"),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height),
                    parts: Object.fromEntries([
                        ["topbar", ".ccs-topbar"], ["body", ".ccs-body"], ["library", ".ccs-library"],
                        ["stage", ".ccs-stage"], ["board", ".ccs-board"], ["templates", ".ccs-template-strip"]
                    ].map(([name, selector]) => {
                        const node = root.querySelector(selector);
                        const box = node?.getBoundingClientRect();
                        return [name, box ? { x: Math.round(box.x), y: Math.round(box.y), w: Math.round(box.width), h: Math.round(box.height) } : null];
                    })),
                    parents: [...(function*(){ let n=root; while(n && n!==document.body){ yield `${n.tagName}.${n.className}`; n=n.parentElement; } })()].slice(0,8),
                    bodyOverflow: document.body.scrollWidth > document.body.clientWidth,
                    serializedState: (() => {
                        const graph = window.app.graph.serialize();
                        const node = graph.nodes.find((item) => item.type === 'AICG3D_CharacterCardStudio');
                        try { return JSON.parse(node?.widgets_values?.[0] || '{}'); } catch (error) { return {}; }
                    })(),
                    cardState: (() => {
                        const node = window.app.graph._nodes.find((item) => item.type === 'AICG3D_CharacterCardStudio');
                        const widget = node?.widgets?.find((item) => item.name === 'card_state');
                        try { return JSON.parse(widget?.value || '{}'); } catch (error) { return {}; }
                    })(),
                };
            }"""
        )
        summary["created"] = created
        summary["drag"] = {
            "before": before_drag,
            "afterAtTarget": after_drag,
            "firstSlot": summary.get("cardState", {}).get("slots", [{}])[0].get("label"),
            "thirdSlot": summary.get("cardState", {}).get("slots", [{}, {}, {}])[2].get("label"),
        }
        summary.pop("cardState", None)
        summary["serialized"] = {
            "template": summary.get("serializedState", {}).get("templateId"),
            "slots": len(summary.get("serializedState", {}).get("slots", [])),
            "library": len(summary.get("serializedState", {}).get("library", [])),
        }
        summary.pop("serializedState", None)
        summary["errors"] = [error for error in errors if error.startswith("pageerror") or "CharacterCardStudio" in error]
        summary["otherConsoleErrors"] = len(errors) - len(summary["errors"])
        (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False))
        browser.close()


if __name__ == "__main__":
    main()
