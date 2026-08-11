import os
import json
import time
import google.generativeai as genai
from PIL import Image as PILImage
from schemas import ImageTags
from dotenv import load_dotenv

load_dotenv()

# Gemini pricing estimates
COST_PER_CALL = 0.001 

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-3-flash-preview')

def process_image_with_ai(filepath: str) -> dict:
    """
    Sends an image to Gemini and asks for a structured JSON response.
    Includes retry logic for API limits.
    """
    prompt = """
    Analyze this image and return a JSON object exactly matching this schema:
    {
      "subject": "The primary subject (e.g. 'red fox', 'gray wolf')",
      "category": "The general category (e.g. 'animal')",
      "attributes": ["list", "of", "visual", "attributes"],
      "caption": "A short descriptive caption",
      "confidence": 0.95
    }
    Return ONLY valid JSON.
    """
    
    img = PILImage.open(filepath)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content([prompt, img])
            
            # Clean up potential markdown formatting from the response
            text = response.text
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            data = json.loads(text.strip())
            
            # Validate with Pydantic
            validated_tags = ImageTags(**data)
            
            return {
                "tags": validated_tags.model_dump() if hasattr(validated_tags, 'model_dump') else validated_tags.dict(),
                "cost": COST_PER_CALL
            }
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {filepath}: {str(e)}")
            if attempt == max_retries - 1:
                raise e
            time.sleep(2) # Backoff before retry
