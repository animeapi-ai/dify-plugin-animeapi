from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.client import PRICES, AnimeAPIError, download, generate

MODELS = ("anime", "ultra", "ultra-max")
ORIENTATIONS = ("portrait", "square", "landscape")


class GenerateImageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        prompt = str(tool_parameters.get("prompt") or "").strip()
        if not prompt:
            yield self.create_text_message("AnimeAPI: the prompt is empty.")
            return
        if len(prompt) > 1000:
            yield self.create_text_message("AnimeAPI: the prompt is longer than 1000 characters.")
            return

        model = tool_parameters.get("model") or "anime"
        if model not in MODELS:
            model = "anime"
        orientation = tool_parameters.get("orientation") or "portrait"
        if orientation not in ORIENTATIONS:
            orientation = "portrait"
        enhance = tool_parameters.get("enhance")
        enhance = True if enhance is None else bool(enhance)

        try:
            result = generate(
                self.runtime.credentials["api_key"],
                {"prompt": prompt, "model": model, "orientation": orientation, "enhance": enhance},
            )
        except AnimeAPIError as e:
            # Includes the API's own message when a prompt is refused (MODERATION_BLOCKED).
            yield self.create_text_message(str(e))
            return

        image_url = result.get("image_url") or ""
        balance = result.get("balance_usd")
        summary = "Generated 1 %s image (%s) for $%s." % (model, orientation, PRICES[model])
        if balance is not None:
            summary += " Balance left: $%s." % balance

        # Hand Dify the file itself: AnimeAPI image links are not permanent storage.
        try:
            data, mime = download(image_url)
            yield self.create_blob_message(blob=data, meta={"mime_type": mime})
        except Exception:
            yield self.create_image_message(image_url)

        yield self.create_text_message(summary)
        yield self.create_json_message(
            {
                "image_url": image_url,
                "model": model,
                "orientation": orientation,
                "enhanced_prompt": result.get("enhanced_prompt"),
                "price_usd": PRICES[model],
                "balance_usd": balance,
                "generation_time_ms": result.get("generation_time_ms"),
            }
        )
