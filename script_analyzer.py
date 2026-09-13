import json
import time
from google import genai
from google.genai import types
from config import CHAT_API_KEY, TEXT_MODEL
from utils import setup_logger

logger = setup_logger("ScriptAnalyzer")
client = genai.Client(api_key=CHAT_API_KEY)

def analyze_script(script_text):
    """
    Analyzes script with Gemini → breaks into narrative segments.
    Preserves exact text, assigns narrative phases (Hook, Main Plot, Ending).
    Minimal retry logic with adaptive backoff.
    """
    logger.info("📊 Analyzing script structure with Gemini...")

    prompt = f"""You are a retention editor for a top-tier explainer channel.
Break the following script into narrative segments.

CRITICAL RULES:
1. EXACT TEXT: Use original text unchanged. Do not rephrase or modify.
2. LOGICAL CHUNKING: Group sentences by meaning, not line count.
3. NARRATIVE PHASES: Label each segment with the job it does for retention.
   Use this structure where the script supports it:
     - "Hook"          the first ~15 seconds: the surprising claim or question
     - "Stakes"        why the viewer should care
     - "Beat 1/2/3"    escalating explanation, each answering something
                       and opening a new question
     - "Payoff"        the satisfying "so that's why" resolution
     - "Call to Action"
   Keep the Hook tight — it is the highest-value real estate in the video.
4. ORDER: Sequential integer from 1 onwards.

Script:
{script_text}

Return valid JSON:
{{
  "title": "A short descriptive title for the video",
  "segments": [
    {{
      "order": 1,
      "narrative_phase": "Hook",
      "text": "The exact original text for this segment"
    }}
  ]
}}
"""

    max_retries = 2
    for attempt in range(max_retries + 1):
        # Minimal cooldown: 0.5s (no throttling needed on first attempt)
        if attempt > 0:
            time.sleep(0.5)

        try:
            response = client.models.generate_content(
                model=TEXT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )

            data = json.loads(response.text)
            title = data.get('title', 'Untitled')
            segment_count = len(data.get('segments', []))
            logger.info(f"✓ Script analyzed: '{title}' → {segment_count} segments")
            return data

        except Exception as e:
            error_str = str(e).lower()
            # Only retry on server errors (503, 504)
            if ("503" in error_str or "504" in error_str) and attempt < max_retries:
                wait = 3 * (attempt + 1)  # 3s, then 6s
                logger.warning(f"⚠ API high demand. Retrying in {wait}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
                continue
            else:
                logger.error(f"✗ Script analysis failed: {str(e)[:100]}")
                return None
    return None
