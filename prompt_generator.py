import time
import json
from google import genai
from google.api_core import exceptions
from google.genai import types
from config import CHAT_API_KEY, TEXT_MODEL
from utils import setup_logger

logger = setup_logger("PromptGenerator")
client = genai.Client(api_key=CHAT_API_KEY)

def generate_image_prompt(chunk_text, chunk_index, project_folder):
    """
    Uses Gemini to break a large chunk into 1-4 sub-scenes with specific prompts.
    Returns a JSON list of sub-scenes.
    Also saves the raw JSON response to a file.
    """
    prompt = f"""
    For each scene, describe a complete visual moment.

Do NOT describe isolated objects.

Instead describe:

- What the character is doing
- What the character is feeling
- Where the scene takes place
- What interesting details exist around them
- What makes the moment visually memorable

Think like an animation director.

The viewer should feel like they are looking at a frame from a story.

Prefer:

- Characters interacting with the world
- Characters discovering things
- Characters reacting naturally
- Interesting environments
- Visual humor
- Atmospheric scenes

Avoid:

- Characters standing still
- Objects floating in empty space
- Diagram-like scenes
- Thumbnail-style compositions
- Extreme exaggeration
- Excessive visual effects

    Script chunk:
    "{chunk_text}"

    Output ONLY valid JSON.

    {{
      "scene_count": {{number}},
      "scenes": [
        {{
          "scene_number": {{1}},
          "script_part": "exact script text",
          "image_prompt": "visual scene description"
        }}
        ...
      ]
    }}
    """

    max_retries = 2
    for attempt in range(max_retries + 1):
        # Mandatory 5-second cooldown before any API call
        time.sleep(5)
        
        try:
            response = client.models.generate_content(
                model=TEXT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            data = json.loads(response.text)

            # --- NEW LOGIC: Save raw JSON response ---
            import os # Ensure os is imported here if not at top-level
            response_filename = f"prompt_response_chunk_{chunk_index:03d}.json"
            output_filepath = os.path.join(project_folder, response_filename)
            with open(output_filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved raw Gemini prompt response to: {output_filepath}")
            # --- END NEW LOGIC ---

            return data.get("scenes", [])

        except Exception as e:
            error_str = str(e).lower()
            if ("503" in error_str or "504" in error_str or "high demand" in error_str) and attempt < max_retries:
                logger.warning(f"Gemini API high demand. Retrying in 4 seconds... (Attempt {attempt + 1}/{max_retries + 1})")
                time.sleep(4)
                continue
            else:
                logger.error(f"Prompt generation failed: {e}")
                return None
    return None
