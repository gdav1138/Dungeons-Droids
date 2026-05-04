from dotenv import load_dotenv
import os

load_dotenv()

DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite-preview"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
_client = None


def _get_client():
    global _client
    if _client is None:
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GEMINI_API_KEY in environment.")
        _client = genai.Client(api_key=api_key)
    return _client


def call_ai(request_text):
    response = _get_client().models.generate_content(
        model=GEMINI_MODEL,
        contents=request_text,
    )
    return (response.text or "").strip()
