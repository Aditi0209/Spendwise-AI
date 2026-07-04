import json, os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def parse_transactions(text:str):
    prompt = f"""
Extract all transactions from the text below.

Return ONLY a JSON array.

Example:

[
  {{
    "amount": 250,
    "category": "Food",
    "merchant": "Zomato"
  }}
]

Text:
{text}
"""
    
    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ], temperature=0
    )
    
    content = response.choices[0].message.content
    
    return json.loads(content)