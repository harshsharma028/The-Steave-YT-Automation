"""
Dark psychology — why people do the things they do, including the ugly parts.

Tone: calm, clinical, quietly unsettling. The narrator never shouts and never
moralises; the material is disturbing enough stated plainly.
"""

from . import Channel

CHANNEL = Channel(
    key="dark_psychology",
    name="The Quiet Part",

    # Measured and low rather than energetic. For this subject a calm delivery
    # is far more unsettling than an excited one.
    voice="en-US-BrianMultilingualNeural",
    rate="+3%",

    style_prompt="""
ABSOLUTE RULE, APPLIES BEFORE EVERYTHING ELSE: render NO text of any kind.
No letters, words, numbers, signage, logos, labels or watermarks. Anything that
would normally carry writing is drawn blank and smooth. Text in the image is a
failed render.

Minimalist psychological-thriller poster art. Stark, quiet and cold — the
visual language of a prestige thriller title sequence. Restraint is the whole
point: one idea, enormous negative space, nothing decorative.

COLOR PALETTE (use these and only these — this is the channel's brand):
- Near-black charcoal (#0E0E11) as the dominant ground, deep and flat
- Bone white (#E8E4DC) for the subject and the few lit shapes
- Cold slate grey-blue (#46525E) for secondary form and shadow
- Desaturated dried blood red (#8C2F2F) used very sparingly, one small accent
  per image at most, as the single point of unease
Overwhelmingly dark. No bright colour, no warmth, no glow, no neon.

FIGURES:
- Usually ONE human figure, small in a large empty space
- Faces are obscured, turned away, cropped out, shadowed or blank — never
  detailed features, never eye contact, never a caricature
- Meaning carried by posture, isolation and scale
- Groups, when used, are identical anonymous silhouettes to feel inhuman

VISUAL LANGUAGE:
- Flat matte shapes with hard edges and heavy shadow, high contrast
- Strong single light source cutting across a dark field
- Subtle film grain; no gloss, no gradients, no 3D rendering
- Symbolic and restrained: a door, a chair, a thread, a mirror, a doorway of
  light, a hand entering frame. Suggest rather than depict.
- Unsettling through emptiness and what is withheld, never through gore

COMPOSITION:
- FULL BLEED: the scene reaches all four edges and corners. No borders, frames,
  panel outlines, paper margins, angled splits or blank caption strips.
- Enormous negative space with one small clear subject, often off-centre
- Must read instantly at phone size as a silhouette

STRICTLY AVOID:
- Any text, letters or numbers
- Gore, blood, wounds, weapons, corpses, self-harm, distressed children
- Horror-movie cliches: jump-scare faces, monsters, skulls, demons
- Bright or warm colour, cartoon styling, cluttered detail
""",

    script_persona="""You are a retention editor for a psychology channel with a
calm, clinical, quietly unsettling tone.""",

    art_director="""You are the art director for a psychology channel with a
cold, minimalist, quietly unsettling look.

The house style is minimalist psychological-thriller poster art: near-black
charcoal, bone white, cold slate, and one small dried-red accent. Usually a
single figure, small in a vast empty space, face obscured or turned away.
Meaning comes from posture, isolation, scale and shadow — never from facial
expression, and never from gore.

Describe:
- The single idea the image must carry, stated as one symbolic image
- The lone subject and how the light falls on it
- What is deliberately hidden or left out of frame
- How much empty darkness surrounds the subject
- Why it feels wrong before the viewer can say why

Restraint is the style. One object, one figure, one shaft of light. If a scene
feels busy, cut it down.""",

    thumbnail_brief="""A single arresting symbolic image on near-black.

A thumbnail competes in a crowded grid at roughly 120 pixels wide, so it is
composed differently from a video frame: the subject is LARGE and close, filling
a third to a half of the frame, lit hard against the dark so its silhouette is
unmistakable when tiny. Still one idea and still mostly empty space — minimal,
not busy — but bold rather than distant.

One bone-white subject with an obscured or turned-away face, off-centre, a
strong shaft of cold light, and at most one small dried-red accent as the point
of unease. Nothing written anywhere.""",
)
