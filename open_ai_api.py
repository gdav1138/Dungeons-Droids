#Used to contact OpenAI and get a chat gpt response to a query that's provided to the function.

from openai import OpenAI
from dotenv import load_dotenv
import os
from google import genai
import time
import re

load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def call_ai(request_text):
#     return client.responses.create(
#         model="gpt-5-nano",
#         #model="gpt-5.2-chat-latest",
#         input=request_text,
#     ).output_text

client = genai.Client()

def call_ai(request_text):
    while True:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite", contents=request_text)
            return response.text
        except:
            print("Got an exception from gemini ai call")
            time.sleep(1)


def _extract_wait_seconds(msg: str):
    """Try to read a 'wait X seconds' hint from an error message."""
    m = re.search(r"(\d+)\s*seconds", msg.lower())
    if m:
        return int(m.group(1))
    return None