import os
from dotenv import load_dotenv

load_dotenv()

CHAT_API_KEY = os.getenv("CHAT_API_KEY")
IMAGE_API_KEY = os.getenv("IMAGE_API_KEY")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-3.1-flash-image")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gemini-2.5-flash")
TTS_VOICE = os.getenv("TTS_VOICE", "en-US-BrianMultilingualNeural")
# Slightly faster than default. Andrew at 0% read like a nature documentary.
TTS_RATE = os.getenv("TTS_RATE", "+8%")
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
# CHANNEL IDENTITY — "Hold On, That Really Happened"
# Weird history, told for laughs. Locked art direction: the
# retro pulp palette is the brand, and holding it across every
# scene makes independently-generated images read as one channel.
# ============================================================

CHANNEL_NAME = "Hold On, That Really Happened"

# Master Style Prompt
MASTER_STYLE_PROMPT = """
ABSOLUTE RULE, APPLIES BEFORE EVERYTHING ELSE: render NO text of any kind.
No letters, no words, no numbers, no signage, no marquee lettering, no logos,
no labels, no captions, no watermarks. Signs, screens, marquees, banners and
posters must be left completely BLANK — glowing empty panels, plain coloured
shapes. If a described object would normally carry writing, draw it smooth and
unlettered. Any text in the image is a failed render.

Retro 1960s pulp cartoon poster art. Vintage comic energy — the look of an old
adventure paperback cover or a mid-century satirical cartoon, hand-inked and
printed on aged paper.

COLOR PALETTE (use these and only these — this is the channel's brand):
- Warm cream paper background (#F2E8D5) as the ground, with subtle halftone grain
- Bold vintage red (#D6473E)
- Deep teal (#2A7E7B)
- Mustard gold (#E8A33D)
- Near-black ink (#1E1A17) for outlines and shadow
Printed, slightly worn, warm. Never neon, never pastel, never digital-looking.

FIGURES:
- Expressive cartoon characters with big comic reactions — this is the joke
- Heavy black ink outlines, bold confident linework
- Exaggerated poses, wild gestures, faces mid-shock, mid-glee or mid-panic
- Period-appropriate clothing drawn loosely, not historically fussy

VISUAL LANGUAGE:
- Hand-inked comic style with halftone dot shading
- Flat printed colour that slightly misregisters, like old offset printing
- One clear comedic moment per frame, staged like a punchline
- Dynamic diagonal compositions with a strong sense of motion

COMPOSITION:
- FULL BLEED: the artwork fills the entire frame edge to edge. No borders, no
  frames, no panel outlines, no postcard margins, no empty caption strip along
  the bottom. Nothing may box the image in.
- Wide framing, clear visual hierarchy, the gag readable instantly
- Keep the lower fifth of the frame calm and uncluttered — subtitles sit there
- Must read at phone size: big shapes, strong silhouettes, high contrast

STRICTLY AVOID:
- Any text, letters, numbers, words, labels, signage, UI or watermarks
- Modern flat-vector or corporate illustration looks
- Neon or candy colours, gradients, glossy 3D rendering, photorealism
- Gore, cruelty played straight, or anything mean-spirited — the tone is
  affectionate disbelief, never nasty

SCENE:
{scene_description}
"""
