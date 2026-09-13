import time
import json
import os
from google import genai
from google.genai import types
from config import CHAT_API_KEY, TEXT_MODEL, ACTIVE_CHANNEL
from utils import setup_logger, classify_api_error, parse_json_lenient

logger = setup_logger("PromptGenerator")
client = genai.Client(api_key=CHAT_API_KEY)

def generate_image_prompt(chunk_text, chunk_index, project_folder):
    """
    Breaks script chunk into 1-4 visual sub-scenes via Gemini.
    Returns scene list with image_prompt descriptions.
    Saves raw JSON response for debugging.
    """
    # Reuse a cached response if this chunk was already generated. Phase 2 aborts
    # the whole run on any failure, and the free tier only allows 20 text
    # requests a day, so re-running must not pay for the same chunk twice.
    cached_path = os.path.join(project_folder, f"prompt_response_chunk_{chunk_index:03d}.json")
    if os.path.exists(cached_path):
        try:
            with open(cached_path, encoding="utf-8") as f:
                scenes = json.load(f).get("scenes", [])
            if scenes:
                logger.info(f"📂 Segment {chunk_index + 1}: reusing cached prompts ({len(scenes)} scenes)")
                return scenes
        except Exception:
            pass  # fall through and regenerate

    logger.info(f"🎬 Generating visual prompts for segment {chunk_index + 1}...")

    prompt = f"""{ACTIVE_CHANNEL.art_director}

PACING — this matters as much as the art. Split the chunk into 2 to 4 scenes,
cutting on each new idea and each turn in the script. One image per chunk is too
slow: a held shot longer than about eight seconds loses the viewer. Short chunks
get 2 scenes, longer ones get 3 or 4. Never return a single scene unless the
chunk is one very short sentence.

Each image is held for several seconds under a slow camera push, so give it a
strong silhouette and enough going on to reward a second look.

NEVER describe anything that implies written words. Do not mention signs,
signage, marquees, labels, logos, banners, posters, price tags, screens showing
text, books, newspapers or tickets with writing. The image model renders such
things as misspelled gibberish. If a scene needs one of these objects, describe
it as blank and unlettered — "a glowing empty marquee panel", "a plain unmarked
banner". Carry meaning through shape, scale, light and composition instead.

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
            data = parse_json_lenient(response.text)

            # Save raw JSON for debugging
            response_filename = f"prompt_response_chunk_{chunk_index:03d}.json"
            output_filepath = os.path.join(project_folder, response_filename)
            with open(output_filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            scene_count = len(data.get("scenes", []))
            logger.info(f"✓ Segment {chunk_index + 1}: {scene_count} sub-scenes generated")
            return data.get("scenes", [])

        except Exception as e:
            should_retry, wait, msg = classify_api_error(e)
            if should_retry and attempt < max_retries:
                logger.warning(f"⚠ {msg}. Retry {attempt + 1}/{max_retries}")
                time.sleep(wait)
                continue
            logger.error(f"✗ Prompt generation failed: {msg}")
            return None
    return None
