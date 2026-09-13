import os
from dotenv import load_dotenv

load_dotenv()

CHAT_API_KEY = os.getenv("CHAT_API_KEY")
IMAGE_API_KEY = os.getenv("IMAGE_API_KEY")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-3.1-flash-image")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gemini-2.5-flash")
TTS_VOICE = os.getenv("TTS_VOICE", "en-US-AndrewMultilingualNeural")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "projects")
FAL_MODEL = os.getenv("FAL_MODEL", "fal-ai/nano-banana")
FAL_KEY = os.getenv("FAL_KEY", "")

# Fal.ai is the default image provider: ~$0.0017/image against Gemini's ~$0.067,
# and this account's free tier grants zero quota for gemini-3.1-flash-image.
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "fal")

# FFmpeg settings
VIDEO_FPS = 30
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
ASPECT_RATIO = "16:9"

# Encoding quality. ultrafast/crf22 was visibly soft on flat vector art,
# where banding and mushy edges show badly.
VIDEO_PRESET = "medium"
VIDEO_CRF = 19

# Ken Burns motion. Slow enough that the viewer feels it rather than sees it.
KEN_BURNS_ZOOM = 0.12   # total zoom travel over a shot (1.00 -> 1.12)
TRANSITION_DURATION = 0.4  # crossfade between shots, seconds

# Whisper settings
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")


# Image Generation Pricing (based on 1K resolution equivalent)
# Source: Gemini API Pricing (adjust as per latest Google pricing)
IMAGE_COST_PER_1M_TOKENS_USD = 60.00 # $60 per 1M output tokens
IMAGE_TOKENS_PER_IMAGE_1K = 1120     # 1120 tokens per 1K image (default)
USD_TO_INR_RATE = 95.20              # Current approximate conversion rate

# ============================================================
# CHANNEL IDENTITY — "Hidden Mechanics"
# Locked art direction. The palette is the brand: holding it
# across every scene makes independently-generated AI images
# read as one channel despite no character consistency.
# ============================================================

CHANNEL_NAME = "Hidden Mechanics"

# Master Style Prompt
MASTER_STYLE_PROMPT = """
Flat vector editorial illustration for a premium explainer video. Think modern
infographic storytelling — the visual language of high-end science and economics
documentaries, not a children's cartoon.

COLOR PALETTE (use these and only these — this is the channel's brand):
- Deep navy background (#1B2A4A) as the dominant ground
- Warm amber/gold (#F5A623) as the primary highlight and focal accent
- Teal (#2EC4B6) as the secondary accent
- Warm off-white (#F7F3E9) for key shapes and light
- Coral (#FF6B5A) used sparingly, only for tension or warning
Dark, rich, and moody with a few glowing warm highlights. Never pastel, never
washed out, never a white background.

FIGURES:
- People are simple, geometric, anonymous silhouette-style figures
- No facial detail, no individual identity, no recurring named character
- Readable purely through posture, gesture and scale
- Figures serve the idea; they are never the subject of a portrait

VISUAL LANGUAGE:
- Clean flat vector shapes, minimal gradients, crisp edges
- Strong single focal point with generous negative space around it
- Depth built through overlapping flat layers and scale, not realistic shading
- Subtle grain/texture is welcome; photorealism is not
- Conceptual and metaphorical: show the idea as a system, structure or scene

COMPOSITION:
- Cinematic wide framing, clear visual hierarchy
- Keep the lower fifth of the frame visually calm and uncluttered — subtitles sit there
- One clear idea per image, instantly readable at phone size

STRICTLY AVOID:
- Any text, letters, numbers, words, labels, signage, UI or watermarks
- Stick figures, googly eyes, exaggerated cartoon faces, comic-strip style
- Clickbait thumbnail energy, giant arrows, explosions, shock expressions
- Cluttered infographic dashboards or chart-salad
- White or light backgrounds

SCENE:
{scene_description}
"""
