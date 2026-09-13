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

    prompt = f"""You are the art director for a comedy channel about weird history.
For each scene, describe ONE complete visual moment staged like a punchline.

The house style is retro 1960s pulp cartoon poster art on warm cream paper —
heavy black ink outlines, halftone shading, bold red, teal and mustard. Think
vintage satirical cartoon, not modern flat vector. Characters are expressive and
comedic: big reactions, wild poses, faces caught mid-shock or mid-glee. The
absurdity of what actually happened is the joke, so stage it that way.

Describe:
- The single funny or astonishing beat the image must land
- Who is doing what to whom, and their exact comic reaction
- The setting, sketched loosely rather than fussed over historically
- Physical comedy: scale gags, chaos, things going wrong in the background
- What makes someone stop scrolling

Each image is held on screen for several seconds with a slow camera push, so
give it a strong silhouette and enough going on to reward a second look.

NEVER describe anything that implies written words. Do not mention signs,
signage, marquees, labels, logos, banners, posters, price tags, screens showing
text, books, newspapers or tickets with writing. The image model renders such
things as misspelled gibberish. If a scene needs one of these objects, describe
it as blank and unlettered — "a glowing empty marquee panel", "a plain unmarked
banner". Carry meaning through shape, scale, light and composition instead.

PREFER: characters mid-reaction, physical comedy, absurd scale contrast,
chaotic background detail, one clear staged gag per frame
AVOID: static portraits, people standing around doing nothing, modern
flat-vector corporate looks, dry diagrams, mean-spirited or gory imagery

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
