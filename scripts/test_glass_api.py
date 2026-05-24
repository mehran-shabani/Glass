import json
import os

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from consultations.services.glass_response import extract_glass_response


def main():
    key = os.getenv("GLASS_API_KEY", "")
    if not key:
        raise SystemExit("GLASS_API_KEY is missing")

    url = "https://glass.health/api/external/v2/messages"
    payload = {
        "version": "glass-5.5",
        "messages": [
            {
                "role": "user",
                "content": "Return a short clinical-style answer: What are common causes of acute unilateral leg swelling?",
            }
        ],
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    print("HTTP status:", resp.status_code)
    print("content-type:", resp.headers.get("Content-Type", ""))
    raw = resp.json()
    print("raw JSON:\n", json.dumps(raw, indent=2, ensure_ascii=False))
    parsed = extract_glass_response(raw)
    print("detected schema:", parsed["detected_schema"])
    print("extracted content:\n", parsed["content"])
    print("references:\n", json.dumps(parsed["references"], indent=2, ensure_ascii=False))
    print("citations:\n", json.dumps(parsed["citations"], indent=2, ensure_ascii=False))
    print("usage:\n", json.dumps(parsed["usage"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
