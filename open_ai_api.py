from dotenv import load_dotenv
import os

load_dotenv()

DEFAULT_CLAUDE_MODEL = "claude-haiku-4-5-20251001"
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL)
_client = None


def _get_client():
    global _client
    if _client is None:
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("Missing ANTHROPIC_API_KEY in environment.")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def call_ai(request_text):
    message = _get_client().messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": request_text}],
    )
    return message.content[0].text.strip()
