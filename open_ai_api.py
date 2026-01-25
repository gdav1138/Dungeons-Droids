#Used to contact OpenAI and get a chat gpt response to a query that's provided to the function.

from openai import OpenAI
from dotenv import load_dotenv
import os
from google import genai

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
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=request_text)
    return response.text