import os
import google.generativeai as genai
from typing import List
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_text_embedding(text: str) -> List[float]:
    """Generates an embedding for a given text using text-embedding-004"""
    try:
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return a zero-vector fallback so it doesn't crash if limits hit
        return [0.0] * 768
