"""Stable Diffusion MCP Server

An MCP server exposing Stable Diffusion WebUI (AUTOMATIC1111) capabilities
as Model Context Protocol tools.
"""

import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SD_API_URL = os.environ.get("SD_API_URL", "http://127.0.0.1:7860")
OUTPUT_DIR = Path(os.environ.get("SD_OUTPUT_DIR", "generated_images"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Path to the SD WebUI launcher script (Windows default; override via env var)
SD_LAUNCHER_PATH = os.environ.get(
    "SD_LAUNCHER_PATH",
    r"C:\stable-diffusion-webui\webui-user.bat",
)

# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP("stable-diffusion")

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _sd_get(path: str, **kwargs):
    """GET request to the SD WebUI API."""
    return requests.get(f"{SD_API_URL}{path}", timeout=30, **kwargs)


def _sd_post(path: str, payload: dict, timeout: int = 300):
    """POST request to the SD WebUI API."""
    return requests.post(f"{SD_API_URL}{path}", json=payload, timeout=timeout)


def _save_image(b64_data: str, filename: str) -> str:
    """Decode a base-64 image and save it; return the absolute path."""
    img_bytes = base64.b64decode(b64_data)
    dest = OUTPUT_DIR / filename
    dest.write_bytes(img_bytes)
    return str(dest.resolve())


def _timestamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def _is_sd_running() -> bool:
    """Return True if the SD WebUI API is reachable."""
    try:
        resp = _sd_get("/sdapi/v1/sd-models")
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def check_sd_status() -> str:
    """Check whether the Stable Diffusion WebUI is running and reachable."""
    if _is_sd_running():
        try:
            info = _sd_get("/sdapi/v1/options").json()
            model = info.get("sd_model_checkpoint", "unknown")
            return f"SD WebUI is running. Current model: {model}"
        except Exception:
            return "SD WebUI is running (could not retrieve model info)."
    return "SD WebUI is NOT running. Use start_sd_webui to launch it."


@mcp.tool()
def start_sd_webui() -> str:
    """Launch the Stable Diffusion WebUI in a background process."""
    if _is_sd_running():
        return "SD WebUI is already running."

    launcher = Path(SD_LAUNCHER_PATH)
    if not launcher.exists():
        return (
            f"Launcher not found at '{SD_LAUNCHER_PATH}'. "
            "Set the SD_LAUNCHER_PATH environment variable to the correct path."
        )

    try:
        if sys.platform == "win32":
            subprocess.Popen(
                [str(launcher)],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        else:
            subprocess.Popen(
                ["bash", str(launcher)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
    except OSError as exc:
        return f"Failed to start SD WebUI: {exc}"

    # Wait up to 60 s for the API to become available
    for _ in range(12):
        time.sleep(5)
        if _is_sd_running():
            return "SD WebUI started successfully."
    return (
        "SD WebUI process launched but the API is not yet reachable. "
        "It may still be loading — try check_sd_status in a moment."
    )


@mcp.tool()
def list_models() -> str:
    """List all Stable Diffusion models available in the WebUI."""
    if not _is_sd_running():
        return "SD WebUI is not running. Use start_sd_webui to launch it."
    try:
        models = _sd_get("/sdapi/v1/sd-models").json()
        if not models:
            return "No models found."
        lines = [f"- {m['model_name']}" for m in models]
        return "Available models:\n" + "\n".join(lines)
    except Exception as exc:
        return f"Error retrieving models: {exc}"


@mcp.tool()
def list_loras() -> str:
    """List all LoRA models available in the WebUI."""
    if not _is_sd_running():
        return "SD WebUI is not running. Use start_sd_webui to launch it."
    try:
        loras = _sd_get("/sdapi/v1/loras").json()
        if not loras:
            return "No LoRA models found."
        lines = [f"- {lr['name']}" for lr in loras]
        return "Available LoRA models:\n" + "\n".join(lines)
    except Exception as exc:
        return f"Error retrieving LoRA models: {exc}"


def _switch_model(model_name: str) -> tuple[bool, str]:
    """Internal helper: switch the active SD model. Returns (success, message)."""
    try:
        payload = {"sd_model_checkpoint": model_name}
        resp = _sd_post("/sdapi/v1/options", payload, timeout=120)
        if resp.status_code == 200:
            return True, f"Model switched to: {model_name}"
        return False, f"Failed to switch model (HTTP {resp.status_code}): {resp.text}"
    except Exception as exc:
        return False, f"Error switching model: {exc}"


@mcp.tool()
def switch_model(model_name: str) -> str:
    """Switch the active Stable Diffusion model.

    Args:
        model_name: Full or partial name of the model checkpoint to activate.
    """
    if not _is_sd_running():
        return "SD WebUI is not running. Use start_sd_webui to launch it."
    _, message = _switch_model(model_name)
    return message


@mcp.tool()
def generate_image(
    prompt: str,
    negative_prompt: str = "",
    model: str = "",
    lora: str = "",
    width: int = 512,
    height: int = 512,
    steps: int = 20,
    cfg_scale: float = 7.0,
    seed: int = -1,
) -> str:
    """Generate an image from a text prompt (txt2img).

    Args:
        prompt: Text description of the image to generate.
        negative_prompt: Things to avoid in the generated image.
        model: Model checkpoint name to use (empty = current model).
        lora: LoRA model name and weight, e.g. 'detailed_face:0.8'.
        width: Image width in pixels (default 512).
        height: Image height in pixels (default 512).
        steps: Number of sampling steps (default 20).
        cfg_scale: Classifier-free guidance scale (default 7.0).
        seed: Random seed; -1 for random (default -1).
    """
    if not _is_sd_running():
        return "SD WebUI is not running. Use start_sd_webui to launch it."

    # Optionally switch model before generating
    if model:
        success, switch_msg = _switch_model(model)
        if not success:
            return switch_msg

    # Embed LoRA into prompt if supplied
    full_prompt = prompt
    if lora:
        parts = lora.split(":", 1)
        lora_name = parts[0].strip()
        lora_weight = "1.0"
        if len(parts) > 1:
            try:
                lora_weight = str(float(parts[1].strip()))
            except ValueError:
                return f"Invalid LoRA weight '{parts[1].strip()}'. Expected a numeric value, e.g. 'detailed_face:0.8'."
        full_prompt = f"{prompt} <lora:{lora_name}:{lora_weight}>"

    payload = {
        "prompt": full_prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "seed": seed,
    }

    try:
        resp = _sd_post("/sdapi/v1/txt2img", payload)
        resp.raise_for_status()
        data = resp.json()
        images = data.get("images", [])
        if not images:
            return "No images returned by SD WebUI."
        filename = f"txt2img_{_timestamp()}.png"
        path = _save_image(images[0], filename)
        info_str = data.get("info") or "{}"
        info = json.loads(info_str)
        used_seed = info.get("seed", "unknown")
        return f"Image saved to: {path}\nSeed: {used_seed}"
    except Exception as exc:
        return f"Error generating image: {exc}"


@mcp.tool()
def img2img(
    image_path: str,
    prompt: str,
    negative_prompt: str = "",
    denoising_strength: float = 0.75,
    width: int = 512,
    height: int = 512,
    steps: int = 20,
    cfg_scale: float = 7.0,
    seed: int = -1,
) -> str:
    """Transform an existing image with a text prompt (img2img).

    Args:
        image_path: Absolute or relative path to the source image.
        prompt: Text description of the desired transformation.
        negative_prompt: Things to avoid in the result.
        denoising_strength: How much to change the image (0.0–1.0, default 0.75).
        width: Output image width (default 512).
        height: Output image height (default 512).
        steps: Number of sampling steps (default 20).
        cfg_scale: Classifier-free guidance scale (default 7.0).
        seed: Random seed; -1 for random (default -1).
    """
    if not _is_sd_running():
        return "SD WebUI is not running. Use start_sd_webui to launch it."

    src = Path(image_path)
    if not src.exists():
        return f"Image file not found: {image_path}"

    img_b64 = base64.b64encode(src.read_bytes()).decode("utf-8")

    payload = {
        "init_images": [img_b64],
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "denoising_strength": denoising_strength,
        "width": width,
        "height": height,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "seed": seed,
    }

    try:
        resp = _sd_post("/sdapi/v1/img2img", payload)
        resp.raise_for_status()
        data = resp.json()
        images = data.get("images", [])
        if not images:
            return "No images returned by SD WebUI."
        filename = f"img2img_{_timestamp()}.png"
        path = _save_image(images[0], filename)
        info_str = data.get("info") or "{}"
        info = json.loads(info_str)
        used_seed = info.get("seed", "unknown")
        return f"Image saved to: {path}\nSeed: {used_seed}"
    except Exception as exc:
        return f"Error during img2img: {exc}"


@mcp.tool()
def interrogate_image(image_path: str, model: str = "clip") -> str:
    """Extract a text prompt from an existing image (reverse-engineer the prompt).

    Args:
        image_path: Absolute or relative path to the image to analyse.
        model: Interrogation model to use — 'clip' (default) or 'deepdanbooru'.
    """
    if not _is_sd_running():
        return "SD WebUI is not running. Use start_sd_webui to launch it."

    src = Path(image_path)
    if not src.exists():
        return f"Image file not found: {image_path}"

    img_b64 = base64.b64encode(src.read_bytes()).decode("utf-8")

    payload = {"image": img_b64, "model": model}

    try:
        resp = _sd_post("/sdapi/v1/interrogate", payload, timeout=120)
        resp.raise_for_status()
        caption = resp.json().get("caption", "")
        return f"Extracted prompt:\n{caption}"
    except Exception as exc:
        return f"Error during interrogation: {exc}"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
