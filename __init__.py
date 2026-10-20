# -*- coding: utf-8 -*-
"""Character Card Studio for ComfyUI."""

from __future__ import annotations

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
from .templates import get_templates_payload

WEB_DIRECTORY = "./web"
__version__ = "1.0.0"

try:
    from aiohttp import web
    from server import PromptServer

    if PromptServer.instance is not None:
        @PromptServer.instance.routes.get("/aicg3d/character-card/templates")
        async def character_card_templates(_request):
            return web.json_response(get_templates_payload())
except Exception as exc:
    print(f"[CharacterCardStudio] Template route unavailable: {exc}")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
