#!/usr/bin/env python
import argparse
import json
import os
from pathlib import Path


def _load_environment() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        import django

        django.setup()
        return
    except Exception:
        pass

    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manual OpenAI smoke test for ClinicalOpenAIClient.")
    parser.add_argument("--raw", action="store_true", help="Print full raw response JSON.")
    args = parser.parse_args()

    _load_environment()

    from django.conf import settings
    from consultations.services.openai_client import ClinicalOpenAIClient

    if not getattr(settings, "OPENAI_API_KEY", ""):
        raise SystemExit("OPENAI_API_KEY is required. Set it in .env before running this smoke test.")

    client = ClinicalOpenAIClient()
    response = client.generate_clinical_response(
        messages=[
            {
                "role": "user",
                "content": "What are common causes of acute unilateral leg swelling?",
            }
        ],
        task_type="clinical_qa",
        structured=False,
    )

    print(f"selected_model: {response.get('model')}")
    print("extracted_content:")
    print(response.get("content", ""))
    print(f"usage: {json.dumps(response.get('usage', {}), ensure_ascii=False)}")

    raw = response.get("raw", {}) if isinstance(response.get("raw"), dict) else {}
    print(f"raw_response_keys: {sorted(raw.keys())}")

    if args.raw:
        print("raw_response_json:")
        print(json.dumps(raw, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
