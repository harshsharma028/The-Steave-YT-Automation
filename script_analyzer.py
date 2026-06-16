import json
import time
from google import genai
from google.api_core import exceptions
from google.genai import types
from config import CHAT_API_KEY, TEXT_MODEL
from utils import setup_logger

logger = setup_logger("ScriptAnalyzer")
client = genai.Client(api_key=CHAT_API_KEY)

def analyze_script(script_text):
    """
    Uses Gemini to analyze the user's script and break it down into 3-4 second visual segments.
    Categorizes segments (e.g., Hook, Main Plot, Ending) and ensures EXACT text preservation.
    Includes a strict 2-second cooldown and retry logic.
    """
    logger.info("Initiating script analysis with Gemini...")
    
    prompt = f"""
    You are a professional video director and script supervisor.
    Analyze the following video script and break it down logically based on the narrative structure, NOT by rigid sentence or time limits.
    
    CRITICAL RULES:
    1. EXACT TEXT: You MUST use the exact, original text provided. Do not rephrase, summarize, or modify the content. Every word from the original script must be included in the segments in order.
    2. LOGICAL CHUNKING: Group sentences together based on the point they are making. For example, a "Hook" might be 4-5 lines long, a "Main Plot" point might be 7-8 lines long, and a subplot might be 5-6 lines long. Do NOT just split it line-by-line. Think about how long a visual concept should stay on screen to explain the idea.
    3. NARRATIVE STRUCTURE: Assign a 'narrative_phase' to each chunk (e.g., "Hook", "Opening", "Main Plot Point 1", "Subplot", "Climax", "Ending", "Call to Action").
    4. ORDER: Assign a sequential 'order' integer to each segment starting from 1 to maintain strict chronological sequence.
    
    Script:
    {script_text}

    Return the response as a valid JSON object with the following structure:
    {{
      "title": "A short descriptive title for the video",
      "segments": [
        {{
          "order": 1,
          "narrative_phase": "Hook",
          "text": "The exact original text for this segment"
        }},
        ...
      ]
    }}
    """

    max_retries = 2
    for attempt in range(max_retries + 1):
        # Mandatory 2-second cooldown before any API call
        time.sleep(2)
        
        try:
            # Call the Gemini API
            response = client.models.generate_content(
                model=TEXT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            # Parse and return the JSON blueprint
            data = json.loads(response.text)
            logger.info(f"Successfully analyzed script! Title determined as: '{data.get('title')}'")
            return data

        except Exception as e:
            error_str = str(e).lower()
            if ("503" in error_str or "504" in error_str or "high demand" in error_str) and attempt < max_retries:
                logger.warning(f"Gemini API is experiencing high demand. Retrying in 4 seconds... (Attempt {attempt + 1}/{max_retries + 1})")
                time.sleep(4)
                continue
            else:
                logger.error(f"Script analysis failed: {e}")
                return None
    return None
