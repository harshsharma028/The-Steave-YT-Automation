# Channel Strategy

The pipeline runs multiple channels from one codebase. Everything that differs
between them lives in `channels/`; everything else is shared, so a bug fixed
once is fixed for every channel.

```bash
CHANNEL=dark_psychology python main.py    # default
CHANNEL=weird_history   python main.py
```

A profile owns: art direction, voice and rate, the writing persona, the art
director persona, and the thumbnail brief. It owns nothing else.

---

## Active channel — "The Quiet Part"

**Human psychology, including the parts people would rather not look at.**
Why we obey, why we lie, why crowds turn, what manipulation actually looks like
from the inside.

**Tone: calm, clinical, quietly unsettling.** The narrator never shouts and
never moralises — the material is disturbing enough stated plainly. That
restraint *is* the hook. Anything that reads as horror-channel theatrics
cheapens it.

**Look:** minimalist psychological-thriller poster art. Near-black charcoal,
bone white, cold slate, and one small dried-blood red accent used sparingly.
One figure, small in a vast empty space, face always obscured or turned away.
Meaning comes from posture, isolation and shadow.

Three rules doing the heavy lifting:

- **Faces are never shown.** It suits the subject, and it sidesteps the fact
  that independently generated images cannot hold a consistent face.
- **Unsettling through restraint, never gore.** Blood, wounds, weapons, corpses
  and horror cliches are banned outright — partly taste, partly because graphic
  content is a monetisation risk.
- **No text in images, ever.** Models render lettering as gibberish.

**Voice:** Brian at **+3%**. Measured rather than energetic; for this subject a
calm read is far more unsettling than an excited one.

---

## Other profiles

**`weird_history`** — "Hold On, That Really Happened". Retro 1960s pulp cartoon,
cream paper and vintage red, Brian at +8%, tone of affectionate disbelief.
Kept intact and switchable.

A finance/systems profile ("Hidden Mechanics", navy flat-vector) exists in git
history at commit `517dac9` if it is ever wanted back.

---

## Shared production settings

- **Pacing:** each script chunk becomes 2–4 scenes, landing near 3.5s per shot.
  A shot held beyond ~8 seconds loses the viewer. Aim scripts at roughly
  100–170 words, which is about 40–60 seconds of narration.
- **Motion:** slow Ken Burns, direction alternating, 0.4s crossfades, shot
  lengths padded so video still matches the master audio exactly.
- **Format: shorts only.** The pipeline runs in `SHORTS_ONLY` mode, so every
  video is 1080×1920 and the format question is not asked. Images generate
  natively at 9:16. The long-form path is intact and returns with
  `SHORTS_ONLY=false`; landscape art reused in a vertical video sits over a
  blurred enlargement of itself so nothing is cropped or stretched.
- **Thumbnail:** optional, offered after the video is stitched. One image,
  1280×720, JPEG under 2MB, no text. Composed deliberately bolder than a video
  frame — a thumbnail competes at ~120px in a grid, so the subject is large and
  hard-lit even though the style stays minimal.

---

## Writing structure

| Segment | Job |
|---|---|
| **Hook** (~15s) | The claim, stated flat. No intro, no branding. |
| **Setup** | The context that makes it land. |
| **Beats** | Escalating, each less comfortable than the last. |
| **Payoff** | The part that reframes everything before it. |
| **CTA** | One line. |

**Targets:** 70%+ retention at 30s, 50%+ overall, 4%+ CTR.

---

## Constraints worth remembering

**Gemini free tier allows 20 text requests per day, per model.** A video costs
about 8, so roughly two videos a day. The quota is per model, so switching
`TEXT_MODEL` buys a fresh allowance; billing removes the cap.

**Do not chase volume.** YouTube's July 2026 Inauthentic Content policy
demonetises mass-produced, templated output, and in January 2026 terminated 16
channels holding 35M subscribers under it. The named fingerprint includes
synthetic narration and an upload pace no human editorial process could
sustain — and this pipeline uses synthetic narration. What protects a channel is
original writing, real curation and a consistent style. One or two considered
videos a week is the strategy; ten a day is how channels get removed.

**Images cost ~$0.0017 each** via Fal.ai, so roughly $0.03 per video including
a thumbnail.
