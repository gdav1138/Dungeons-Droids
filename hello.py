#print("Hello World")
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.responses.create(
    model="gpt-5-nano",
    input="Greet the world as our new Text Game With AI Called Dungeons and Droids. Don't give any instructions to the user."
)

print(response.output_text)