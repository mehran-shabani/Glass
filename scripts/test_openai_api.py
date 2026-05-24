import json
import os

from openai import OpenAI


def main():
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        raise SystemExit("OPENAI_API_KEY is missing")

    client = OpenAI(api_key=key, base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1"),
        input=[{"role": "user", "content": "Return a short clinical-style answer: What are common causes of acute unilateral leg swelling?"}],
    )
    print(json.dumps(response.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
