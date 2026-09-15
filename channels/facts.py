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
ABSOLUTE RULE, APPLIES BEFORE EVERYTHING ELSE: render NO text of any kind.
No letters, words, numbers, signage, logos, labels or watermarks. Anything that
would normally carry writing is drawn blank and smooth. Text in the image is a
failed render.

Bold high-contrast graphic poster illustration. Punchy, cinematic and loud —
the visual language of a striking magazine cover. Every image is built to stop a
thumb mid-scroll.

COLOR PALETTE (use these and only these — this is the channel's brand):
- Deep ink near-black (#0D1014) as the ground
- Electric cyan (#1FD1F9) as the primary light and glow
- Hot magenta-red (#FF2E63) as the secondary accent and point of drama
- Bright bone white (#F5F7FA) for highlights and key shapes
- Warm amber (#FFC93C) used sparingly for emphasis
High saturation, hard contrast, strong rim lighting against darkness. Never
pastel, never washed out, never a white background.

SUBJECT:
- ONE subject, large and central, lit hard against a dark field
- Dramatic scale: make the surprising thing enormous or tiny, whichever sells it
- People appear as bold silhouettes or simplified figures with obscured faces
- Objects, animals and places are drawn graphic and stylised, never photoreal

VISUAL LANGUAGE:
- Flat graphic shapes with crisp edges, bold blocks of colour
- Strong directional light, glow and rim light doing the dramatic work
- Subtle grain; no glossy 3D renders, no photorealism
- The tone flexes with the fact — playful, eerie or jaw-dropping — but the
  palette and the hard-lit graphic treatment never change. That consistency is
  what makes a frame recognisable as this channel.

COMPOSITION:
- FULL BLEED: the scene reaches all four edges and corners. No borders, frames,
  panel outlines, paper margins, angled splits or blank caption strips.
- Built for VERTICAL 9:16. The artwork must fill the WHOLE tall frame, top edge
  to bottom edge — background, ground, atmosphere and glow all continue to the
  very bottom. Never leave the lower part of the frame as empty flat background.
  Place the main subject in the upper two thirds and keep the lower third free
  of competing detail, because captions sit there — uncluttered, but never blank.
- Must read instantly at phone size: big shapes, strong silhouette, high contrast

STRICTLY AVOID:
- Any text, letters or numbers
- Gore, wounds, corpses, blood, injury detail, real-world tragedy depicted
  graphically. Unsettling is fine; grisly is not — it is a monetisation risk.
- Cluttered collages, busy infographics, multiple competing subjects
- Muted or washed-out colour, white backgrounds, stock-photo looks
""",

    script_persona="""You are a retention editor for a fast-paced facts channel.
The tone is punchy and confident, and the pace never sags.""",

    art_director="""You are the art director for a fast-paced facts channel.
For each scene, describe ONE bold image that sells the fact instantly.

The house style is high-contrast graphic poster art: deep ink background,
electric cyan light, hot magenta-red accents, hard rim lighting. One large
central subject, stylised and graphic, never photoreal. People appear as bold
silhouettes with obscured faces.

Describe:
- The single fact the image has to land, as one striking picture
- The one subject that dominates the frame, and how big it is
- Where the hard light falls and what glows
- The scale contrast or visual surprise that sells it
- Why someone scrolling would stop

The video is VERTICAL, so compose tall: subject in the upper two thirds, lower
third kept calm for captions. One idea per image — if a scene needs two things
explained, make it two scenes.

Never describe gore, wounds, blood or graphic injury. Unsettling and dramatic
is right; grisly is not.""",

    thumbnail_brief="""One bold, loud, instantly readable image on deep ink.
A single subject filling a third to a half of the frame, hard-lit with electric
cyan and a hot magenta accent, high contrast, strong silhouette. It competes in
a grid at roughly 120 pixels wide, so bigger and bolder beats subtle every time.
Nothing written anywhere.""",
)
