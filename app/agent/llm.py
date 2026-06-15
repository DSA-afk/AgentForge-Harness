from openai import OpenAI
from app.config.config import settings

_client = OpenAI(base_url=settings.LLM_BASE_URL,api_key=settings.LLM_API_KEY)


def chat(messages: list[dict]) -> str:
    resp = _client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=messages,
    )

    return resp.choices[0].message.content
