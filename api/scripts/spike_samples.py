"""Model spike: send every image in /samples to Gemma 4 and print the structured results.

Usage: cd api && uv run python scripts/spike_samples.py [--samples ../samples]
Only use anonymized documents. Prints extracted fields to stdout; nothing is saved.
"""

import argparse
import base64
import json
import sys
import time
from pathlib import Path

import httpx
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings  # noqa: E402
from app.schemas import DocumentAnalysis  # noqa: E402

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "analyze_v1.md"


def analyze(client: httpx.Client, image: Path) -> tuple[str, float]:
    settings = get_settings()
    schema = DocumentAnalysis.model_json_schema()
    prompt = PROMPT_PATH.read_text(encoding="utf-8").replace("{schema}", json.dumps(schema))
    payload = {
        "model": settings.ollama_model,
        "stream": False,
        "think": False,
        "format": schema,
        "options": {"temperature": 0},
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [base64.b64encode(image.read_bytes()).decode()],
            }
        ],
    }
    start = time.perf_counter()
    response = client.post(f"{settings.ollama_base_url}/api/chat", json=payload)
    response.raise_for_status()
    return response.json()["message"]["content"], time.perf_counter() - start


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--samples", type=Path, default=Path(__file__).resolve().parents[2] / "samples"
    )
    args = parser.parse_args()

    images = sorted(p for p in args.samples.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
    if not images:
        sys.exit(f"No images found in {args.samples}")

    timeout = get_settings().ollama_timeout_seconds
    with httpx.Client(timeout=timeout) as client:
        for image in images:
            print(f"\n=== {image.name}")
            raw, seconds = analyze(client, image)
            try:
                result = DocumentAnalysis.model_validate_json(raw)
                print(result.model_dump_json(indent=2))
            except ValidationError as error:
                print(f"INVALID OUTPUT ({error.error_count()} errors):\n{raw}")
            print(f"--- {seconds:.1f}s")


if __name__ == "__main__":
    main()
