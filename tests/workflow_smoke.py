# -*- coding: utf-8 -*-
"""Load the bundled workflow in the live ComfyUI frontend."""

from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "workflows" / "角色卡_五种卡版_单线工作流.json"
URL = os.environ.get("CCS_TEST_URL", "http://127.0.0.1:8199")


def main() -> None:
    workflow = json.loads(WORKFLOW.read_text(encoding="utf-8-sig"))
    errors: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1500, "height": 1000})
        page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
        page.goto(URL, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_function("() => Boolean(window.app && window.app.graph)", timeout=120_000)
        loaded = page.evaluate(
            """async (workflow) => {
                await window.app.loadGraphData(workflow);
                await new Promise((resolve) => setTimeout(resolve, 1200));
                return {
                    nodes: window.app.graph._nodes.length,
                    settingsNode: window.app.graph._nodes.filter((node) => node.type === "AICG3D_CardSettingsFive").length,
                    modelLoader: window.app.graph._nodes.filter((node) => node.type === "AICG3D_Qwen21ModelLoader").length,
                    generator: window.app.graph._nodes.filter((node) => node.type === "AICG3D_CharacterCardGeneratorSingle").length,
                    qwen: window.app.graph._nodes.filter((node) => node.type === "TextEncodeQwenImage21").length,
                    missing: window.app.graph._nodes.filter((node) => node.has_errors).map((node) => node.type),
                };
            }""",
            workflow,
        )
        loaded["errors"] = errors[-10:]
        page.evaluate(
            """() => {
                const node = window.app.graph._nodes.find((item) => item.type === 'AICG3D_Qwen21ModelLoader');
                if (!node) return;
                window.app.canvas.setZoom(0.55);
                window.app.canvas.centerOnNode(node);
                window.app.graph.setDirtyCanvas(true, true);
            }"""
        )
        page.wait_for_timeout(500)
        (ROOT / "_ui_test").mkdir(exist_ok=True)
        page.screenshot(path=str(ROOT / "_ui_test" / "workflow_preview.png"), full_page=False)
        print(json.dumps(loaded, ensure_ascii=False))
        browser.close()


if __name__ == "__main__":
    main()
