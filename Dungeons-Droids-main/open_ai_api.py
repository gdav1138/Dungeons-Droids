#Used to contact Google Gemini AI and get a response to a query that's provided to the function.

from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

client = genai.Client()

def call_ai(request_text):
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=request_text)
    return response.text