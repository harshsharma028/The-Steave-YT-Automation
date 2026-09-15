import os
from dotenv import load_dotenv

from channels import load_channel

load_dotenv()

CHAT_API_KEY = os.getenv("CHAT_API_KEY")
IMAGE_API_KEY = os.getenv("IMAGE_API_KEY")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-3.1-flash-image")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gemini-flash-lite-latest")
# Active channel profile. Override per run with CHANNEL=weird_history.
ACTIVE_CHANNEL = load_channel()

# Voice belongs to the channel; the env vars are an escape hatch, not the default.
TTS_VOICE = os.getenv("TTS_VOICE") or ACTIVE_CHANNEL.voice
TTS_RATE = os.getenv("TTS_RATE") or ACTIVE_CHANNEL.rate
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "projects")
FAL_MODEL = os.getenv("FAL_MODEL", "fal-ai/nano-banana")
FAL_KEY = os.getenv("FAL_KEY", "")

# Fal.ai is the default image provider: ~$0.0017/image against Gemini's ~$0.067,
# and this account's free tier grants zero quota for gemini-3.1-flash-image.
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "fal")

# Background music. Any track dropped in MUSIC_DIR can be used; the bed is
# looped to the length of the narration, ducked well underneath it, and faded.
# Narration must stay dominant, hence the low default gain.
MUSIC_DIR = os.getenv("MUSIC_DIR", "assets/music")
MUSIC_VOLUME = float(os.getenv("MUSIC_VOLUME", "0.14"))
MUSIC_FADE = 1.5  # seconds of fade in/out

# Shorts-only mode. The long-form path is fully intact and re-enabled by
# setting SHORTS_ONLY=false; it is simply not offered while this is on.
SHORTS_ONLY = os.getenv("SHORTS_ONLY", "true").strip().lower() not in ("false", "0", "no")
DEFAULT_VIDEO_FORMAT = "short form" if SHORTS_ONLY else "long form"

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
# Fraction trimmed off each edge to remove the printed paper margin the
# retro style keeps adding around the artwork.
EDGE_TRIM = 0.06

# Whisper settings
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")


# Image Generation Pricing (based on 1K resolution equivalent)
# Source: Gemini API Pricing (adjust as per latest Google pricing)
IMAGE_COST_PER_1M_TOKENS_USD = 60.00 # $60 per 1M output tokens
IMAGE_TOKENS_PER_IMAGE_1K = 1120     # 1120 tokens per 1K image (default)
USD_TO_INR_RATE = 95.20              # Current approximate conversion rate

# ============================================================
# CHANNEL IDENTITY — supplied by the active channel profile in channels/
# ============================================================

CHANNEL_NAME = ACTIVE_CHANNEL.name

# Art direction wrapped around every image prompt.
MASTER_STYLE_PROMPT = ACTIVE_CHANNEL.style_prompt.rstrip() + """

SCENE:
{scene_description}
"""
