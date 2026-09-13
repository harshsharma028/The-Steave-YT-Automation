import json
import time
from google import genai
from google.genai import types
from config import CHAT_API_KEY, TEXT_MODEL, ACTIVE_CHANNEL
from utils import setup_logger, classify_api_error, parse_json_lenient

logger = setup_logger("ScriptAnalyzer")
client = genai.Client(api_key=CHAT_API_KEY)

def analyze_script(script_text):
    """
    Analyzes script with Gemini → breaks into narrative segments.
    Preserves exact text, assigns narrative phases (Hook, Main Plot, Ending).
    Minimal retry logic with adaptive backoff.
    """
    logger.info("📊 Analyzing script structure with Gemini...")

    prompt = f"""{ACTIVE_CHANNEL.script_persona}
Break the following script into narrative segments.

CRITICAL RULES:
1. EXACT TEXT: Use original text unchanged. Do not rephrase or modify.
2. LOGICAL CHUNKING: Group sentences by meaning, not line count.
3. NARRATIVE PHASES: Label each segment with the job it does for retention.
   Use this structure where the script supports it:
     - "Hook"          the first ~15 seconds: the absurd claim, stated flat
     - "Setup"         the context that makes the absurdity land
     - "Beat 1/2/3"    escalating madness, each one topping the last
     - "Punchline"     the most ridiculous detail, saved for last
     - "Call to Action"
   This is comedy about things that genuinely happened, so keep the
   escalation intact — each beat should feel less believable than the one
   before it.
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

            data = parse_json_lenient(response.text)
            title = data.get('title', 'Untitled')
            segment_count = len(data.get('segments', []))
            logger.info(f"✓ Script analyzed: '{title}' → {segment_count} segments")
            return data

        except Exception as e:
            should_retry, wait, msg = classify_api_error(e)
            if should_retry and attempt < max_retries:
                logger.warning(f"⚠ {msg}. Retry {attempt + 1}/{max_retries}")
                time.sleep(wait)
                continue
            logger.error(f"✗ Script analysis failed: {msg}")
            return None
    return None
