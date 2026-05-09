import base64
from mimetypes import guess_type
from pathlib import Path

from helpers import files, history, plugins, runtime
from helpers.print_style import PrintStyle
from helpers.tool import Response, Tool

# Image token estimation for context window.
TOKENS_ESTIMATE = 1500


def _image_to_data_url(path: str, mime_type: str) -> str | None:
    try:
        data = Path(path).read_bytes()
    except OSError:
        return None
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


class VisionLoad(Tool):
    async def execute(self, paths: list[str] = [], **kwargs) -> Response:

        self.images_dict = {}
        self.loaded_paths: list[str] = []
        self.skipped_paths: list[str] = []

        max_embeds = self._get_max_embeds()
        limited_paths = paths if max_embeds <= 0 else paths[-max_embeds:]
        self.skipped_paths = paths[:-max_embeds] if max_embeds > 0 and len(paths) > max_embeds else []

        for path in limited_paths:
            if not await runtime.call_development_function(files.exists, str(path)):
                continue

            if path not in self.images_dict:
                mime_type, _ = guess_type(str(path))
                if mime_type and mime_type.startswith("image/"):
                    self.images_dict[path] = _image_to_data_url(str(path), mime_type)
                    self.loaded_paths.append(path)

        return Response(message="dummy", break_loop=False)

    def _get_max_embeds(self) -> int:
        cfg = plugins.get_plugin_config("_model_config", agent=self.agent) or {}
        chat_cfg = cfg.get("chat_model", {})
        max_embeds = chat_cfg.get("max_embeds", 10)
        return int(max_embeds or 0)

    async def after_execution(self, response: Response, **kwargs):

        content = []
        loaded_count = len(self.loaded_paths)
        skipped_count = len(self.skipped_paths)
        loaded_summary = "\n".join(self.loaded_paths) if self.loaded_paths else "none"
        skipped_summary = "\n".join(self.skipped_paths) if self.skipped_paths else "none"
        summary = (
            f"Loaded images: {loaded_count}\n"
            f"Loaded images:\n{loaded_summary}\n\n"
            f"Skipped images: {skipped_count}\n"
            f"Skipped images (max {self._get_max_embeds()} loaded at a time according to model configuration):\n{skipped_summary}"
        )
        if self.images_dict:
            self.agent.hist_add_tool_result(self.name, summary, id=self.log.id if self.log else "")
            for path, image_url in self.images_dict.items():
                if image_url:
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        }
                    )
                else:
                    content.append(
                        {
                            "type": "text",
                            "text": "Error processing image " + path,
                        }
                    )
            msg = history.RawMessage(raw_content=content, preview="<Image attachments loaded by path>")
            self.agent.hist_add_message(
                False, content=msg, tokens=TOKENS_ESTIMATE * len(content)
            )
        else:
            self.agent.hist_add_tool_result(self.name, summary if self.skipped_paths else "No images processed", id=self.log.id if self.log else "")

        message = (
            "No images processed"
            if not self.images_dict and not self.skipped_paths
            else f"{loaded_count} images loaded, {skipped_count} skipped"
        )
        PrintStyle(
            font_color="#1B4F72", background_color="white", padding=True, bold=True
        ).print(f"{self.agent.agent_name}: Response from tool '{self.name}'")
        PrintStyle(font_color="#85C1E9").print(message)
        self.log.update(result=message)