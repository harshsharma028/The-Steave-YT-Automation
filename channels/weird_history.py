"""
Weird history — insane laws and things that genuinely happened.

Tone: affectionate disbelief. Never mean-spirited, never gory.
"""

from . import Channel

CHANNEL = Channel(
    key="weird_history",
    name="Hold On, That Really Happened",

    voice="en-US-BrianMultilingualNeural",
    rate="+8%",

    style_prompt="""
ABSOLUTE RULE, APPLIES BEFORE EVERYTHING ELSE: render NO text of any kind.
No letters, no words, no numbers, no signage, no marquee lettering, no logos,
no labels, no captions, no watermarks. Signs, screens, marquees, banners and
posters must be left completely BLANK — plain coloured shapes. If a described
object would normally carry writing, draw it smooth and unlettered. Any text in
the image is a failed render.

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
- A strong sense of motion in the poses and action

COMPOSITION:
- FULL BLEED, THIS IS CRITICAL: the illustrated scene must reach all four edges
  and all four corners of the image. Every part of the canvas is drawn scenery.
  No borders, frames or panel outlines. No margins of bare paper. No diagonal or
  angled split leaving part of the canvas empty. No blank caption strip. The
  picture is not an object sitting on a background — it IS the whole background.
- Wide framing, clear visual hierarchy, the gag readable instantly
- Keep the lower fifth of the frame calm and uncluttered — subtitles sit there
- Must read at phone size: big shapes, strong silhouettes, high contrast

STRICTLY AVOID:
- Any text, letters, numbers, words, labels, signage, UI or watermarks
- Modern flat-vector or corporate illustration looks
- Neon or candy colours, gradients, glossy 3D rendering, photorealism
- Gore, cruelty played straight, or anything mean-spirited — the tone is
  affectionate disbelief, never nasty
""",

    script_persona="""You are a retention editor for a comedy channel about
weird history.""",

    art_director="""You are the art director for a comedy channel about weird
history. For each scene, describe ONE complete visual moment staged like a
punchline.

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
- What makes someone stop scrolling""",

    thumbnail_brief="""One loud comedic moment, staged like a vintage poster.
A single character mid-reaction, huge in frame, bold flat colour, heavy ink.
Extreme simplicity — one gag, instantly readable at 120 pixels wide.""",
)
