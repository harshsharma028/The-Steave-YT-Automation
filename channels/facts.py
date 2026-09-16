"""
Facts — surprising, shocking, unbelievable, funny, grim. Any fact that makes
someone say "wait, what?"

Tone: fast, punchy, confident. No preamble, no padding, straight into it.
The range is deliberately wide, so the LOOK carries the brand rather than the
subject matter.
"""

from . import Channel

CHANNEL = Channel(
    key="facts",
    name="Wait, What?",

    # Fast-paced delivery. Facts channels live on momentum — the moment it
    # sounds like a lecture, the viewer is gone.
    voice="en-US-BrianMultilingualNeural",
    rate="+12%",

    style_prompt="""
Photorealistic cinematic film still, full-bleed vertical composition filling the
entire frame. Believable photographed imagery, not illustration — a facts video
carries more weight when the picture looks real.

LIGHT AND GRADE (this is the channel's brand — hold it in every image):
- A dramatic single-source key light picks the subject out in warm amber
- It sits against a cool, deep teal-blue darkness
- Heavy atmospheric haze, dust or water in the air giving real depth
- Strong contrast with rich inky shadows, shallow depth of field, subtle film grain
- Moody prestige documentary colour grade
The subject is always the warm, lit thing in a cool dark world. That single
relationship is what makes a desert scene and an underwater scene read as the
same channel.

SUBJECT:
- ONE subject, large in frame and clearly lit
- Dramatic scale: make the surprising thing enormous or tiny, whichever sells it
- Photographic realism in materials, anatomy, weathering and lighting
- People are shown from behind, in silhouette, or at a distance — faces are not
  the subject, and faces do not stay consistent between separately made images

COMPOSITION:
- Built for VERTICAL 9:16. The photograph reaches all four edges: sky, ground,
  water and haze all continue to the very bottom of the frame.
- Main subject in the upper two thirds. The lower third stays free of competing
  detail because captions sit there — quiet ground, water or haze, never an
  empty flat void.
- Must read instantly at phone size: one clear subject, strong silhouette,
  hard separation between the lit subject and the dark surroundings.

AVOID:
- Text of any kind. Signs, screens and banners are shown blank and unlettered;
  lettering renders as gibberish and gives the channel away.
- Gore, wounds, corpses, blood, injury detail, or real-world tragedy shown
  graphically. Dramatic and unsettling is right; grisly is a monetisation risk.
- Flat vector or cartoon looks, neon graphic styling, glossy plastic 3D
- Bright evenly-lit stock-photo scenes, white backgrounds, washed-out colour
- Cluttered collages or several subjects competing for attention
- Letterboxing, black bars, borders or framing devices of any kind
""",

    script_persona="""You are a retention editor for a fast-paced facts channel.
The tone is punchy and confident, and the pace never sags.""",

    art_director="""You are the art director for a fast-paced facts channel.
For each scene, describe ONE photograph that sells the fact instantly.

The house style is photorealistic cinematic imagery: a warm amber key light
picking the subject out of a cool, deep teal-blue darkness, with haze or dust
giving depth. Think a moody documentary still, not an illustration. People are
shown from behind, in silhouette or at a distance.

Describe:
- The single fact the image has to land, as one real photographed moment
- The one subject that dominates the frame, and how big it is
- Where the warm light falls and what stays in shadow
- The atmosphere in the air: dust, haze, spray, smoke, water
- The scale contrast or visual surprise that makes someone stop scrolling

The video is VERTICAL, so compose tall: subject in the upper two thirds, with
ground, water or haze continuing to the bottom edge so the lower third is quiet
but never empty. One idea per image — if a scene needs two things explained,
make it two scenes.

Never describe text, signage or lettering. Never describe gore, wounds, blood or
graphic injury — dramatic and unsettling is right, grisly is not.""",

    thumbnail_brief="""One cinematic photographic image, instantly readable at
roughly 120 pixels wide. A single subject filling a third to a half of the
frame, picked out in warm amber light against cool deep darkness, heavy
atmosphere, strong silhouette and hard contrast. Closer and bolder than a video
frame — a thumbnail competes in a grid. Nothing written anywhere.""",
)
