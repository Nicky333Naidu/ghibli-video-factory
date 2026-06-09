import json
import re
from typing import Any, List, Dict

import requests

KILO_GATEWAY_URL = "https://api.kilo.ai/v1/chat/completions"
KILO_MODEL = "kilo-auto/free"


def _extract_json_array(text: str) -> List[Dict[str, Any]]:
    """Safely extract the first JSON array from a model response."""
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"[[sS]*]", text)
    if not match:
        raise ValueError("No JSON array found in model response")

    extracted = match.group(0)
    parsed = json.loads(extracted)
    if not isinstance(parsed, list):
        raise ValueError("Model response did not contain a JSON array")
    return parsed


def generate_scene_json(topic: str, api_key: str | None = None) -> List[Dict[str, Any]]:
    """Expand a topic into 4 sequential Ghibli-style scenes."""
    prompt = (
        "Turn the following topic into exactly 4 sequential scenes for a cinematic animated story. "
        "Return ONLY valid JSON as an array of 4 objects. Each object must have: "
        "scene_number (1-4), narration_text, and image_prompt. "
        "The image_prompt must be highly detailed and optimized for Studio Ghibli style art, "
        "with environment, lighting, mood, character details, composition, and color palette. "
        "No markdown, no code fences, no extra text. Topic: "
        f"{topic}"
    )

    payload = {
        "model": KILO_MODEL,
        "messages": [
            {"role": "system", "content": "You are a precise JSON generator."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    response = requests.post(KILO_GATEWAY_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()

    content = data["choices"][0]["message"]["content"]
    scenes = _extract_json_array(content)

    cleaned = []
    for i, item in enumerate(scenes[:4], start=1):
        cleaned.append(
            {
                "scene_number": item.get("scene_number", i),
                "narration_text": item.get("narration_text", ""),
                "image_prompt": item.get("image_prompt", ""),
            }
        )

    return cleaned
