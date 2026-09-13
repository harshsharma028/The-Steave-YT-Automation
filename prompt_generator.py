import time
import json
import os
from google import genai
from google.genai import types
from config import CHAT_API_KEY, TEXT_MODEL
from utils import setup_logger

logger = setup_logger("PromptGenerator")
client = genai.Client(api_key=CHAT_API_KEY)

def generate_image_prompt(chunk_text, chunk_index, project_folder):
    """
    Breaks script chunk into 1-4 visual sub-scenes via Gemini.
    Returns scene list with image_prompt descriptions.
    Saves raw JSON response for debugging.
    """
    logger.info(f"🎬 Generating visual prompts for segment {chunk_index + 1}...")

    prompt = f"""For each scene, describe ONE complete visual moment (not isolated objects).

Describe:
- What the character is doing
- What the character is feeling
- Where the scene takes place
- Interesting visual details
- What makes the moment memorable

Think like an animation director. The viewer should feel like they're watching a story frame.

PREFER: Characters interacting, discovering, reacting naturally, interesting environments, visual humor
AVOID: Characters standing still, floating objects, diagrams, thumbnails, extreme exaggeration

Script chunk:
"{chunk_text}"

Output ONLY valid JSON:
{{
  "scene_count": {{number}},
  "scenes": [
    {{
      "scene_number": {{1}},
      "script_part": "exact script text",
      "image_prompt": "visual scene description"
    }}
  ]
}}
"""

    max_retries = 2
    for attempt in range(max_retries + 1):
        # Minimal cooldown: 1.5s on first attempt, 0.5s before retries
        if attempt > 0:
            time.sleep(0.5)
        else:
            time.sleep(1.5)

        try:
            response = client.models.generate_content(
                model=TEXT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text)

            # Save raw JSON for debugging
            response_filename = f"prompt_response_chunk_{chunk_index:03d}.json"
            output_filepath = os.path.join(project_folder, response_filename)
            with open(output_filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            scene_count = len(data.get("scenes", []))
            logger.info(f"✓ Segment {chunk_index + 1}: {scene_count} sub-scenes generated")
            return data.get("scenes", [])

        except Exception as e:
            error_str = str(e).lower()
            # Retry only on server errors
            if ("503" in error_str or "504" in error_str or "high demand" in error_str) and attempt < max_retries:
                wait = 3 * (attempt + 1)
                logger.warning(f"⚠ API overloaded. Retrying in {wait}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
                continue
            else:
                logger.error(f"✗ Prompt generation failed: {str(e)[:100]}")
                return None
    return None
