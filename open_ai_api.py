#Used to contact OpenAI and get a chat gpt response to a query that's provided to the function.

from openai import OpenAI
from dotenv import load_dotenv
import os
from google import genai
import time
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_ai(request_text):
    return client.responses.create(
        model="gpt-4.1-nano",
        input=request_text,
    ).output_text


def _extract_wait_seconds(msg: str):
    """Try to read a 'wait X seconds' hint from an error message."""
    m = re.search(r"(\d+)\s*seconds", msg.lower())
    if m:
        return int(m.group(1))
    return None