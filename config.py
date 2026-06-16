import os
from dotenv import load_dotenv

load_dotenv()

CHAT_API_KEY = os.getenv("CHAT_API_KEY")
IMAGE_API_KEY = os.getenv("IMAGE_API_KEY")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-3.1-flash-image")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gemini-2.5-flash")
TTS_VOICE = os.getenv("TTS_VOICE", "en-US-AndrewMultilingualNeural")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "projects")

# FFmpeg settings
VIDEO_FPS = 30
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
ASPECT_RATIO = "16:9"

# Whisper settings
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")


# Image Generation Pricing (based on 1K resolution equivalent)
# Source: Gemini API Pricing (adjust as per latest Google pricing)
IMAGE_COST_PER_1M_TOKENS_USD = 60.00 # $60 per 1M output tokens
IMAGE_TOKENS_PER_IMAGE_1K = 1120     # 1120 tokens per 1K image (default)
USD_TO_INR_RATE = 95.20              # Current approximate conversion rate

# Master Style Prompt
MASTER_STYLE_PROMPT = """
Create the scene in a colorful 2D educational cartoon style designed for modern YouTube explainer videos.

CHARACTERS:

- Simple stickman-inspired characters
- Perfectly round white faces
- Thick black outlines
- Simple expressive facial features
- Minimal but clear emotions
- Thin stick-figure bodies
- Consistent character design across all scenes
- Simple cartoon hair when needed

VISUAL STYLE:

- Bright colorful environments
- Rich colors but not oversaturated
- Clean vector-cartoon appearance
- Thick outlines
- Soft stylized shading allowed
- Cozy and visually appealing
- Storybook-like atmosphere
- Educational but entertaining

ENVIRONMENTS:

- Detailed enough to feel alive
- Simple enough to remain readable
- Colorful landscapes
- Colorful buildings
- Natural scenery
- Props relevant to the scene

COMPOSITION:

- Clear focal point
- Easy to understand
- Balanced composition
- Strong storytelling
- Natural scene layouts
- Avoid empty backgrounds

VISUAL STORYTELLING:

Focus on creating scenes that feel like moments from an animated story.

Show:

- Character actions
- Character emotions
- Interesting environments
- Visual contrast
- Size comparison when relevant
- Funny situations
- Curious discoveries

The image should feel:

- Curious
- Fun
- Educational
- Cozy
- Interesting
- Story-driven

Avoid:

- Thumbnail-style clickbait
- Giant arrows
- Explosions
- Extreme reaction faces
- Excessive motion effects
- Overly saturated colors
- Empty infographic layouts

The final image should look like a frame from a high-quality animated educational YouTube video rather than a YouTube thumbnail.

SCENE:
{scene_description}
"""
