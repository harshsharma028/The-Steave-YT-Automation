# Hold On, That Really Happened — Channel Strategy

Weird history, told for laughs. The decisions below are implemented in the
pipeline. Change them deliberately — consistency is the growth mechanism.

> **Why this replaced the first plan.** The original strategy here was a
> finance-adjacent "hidden systems" channel, chosen for RPM. It was boring to
> watch and boring to make, and got abandoned halfway through its own demo
> video. A niche you will actually keep making for months beats a higher-paying
> one you won't. That lesson is the reason for everything below.

---

## 1. The niche

**Weird history** — insane laws, bizarre historical figures, and things that
genuinely happened but sound invented.

Four pillars, in rotation:

| Pillar | Example topics |
|---|---|
| Laws that actually existed | Peter the Great's beard tax |
| People who really did that | The emperor who declared war on birds |
| Trials and punishments | Medieval animals put on trial |
| Everyday life was insane | What Victorians did for fun |

**Why it works:**

- **Fun to make.** The single most important factor. The scripts are jokes, not
  lectures.
- **Infinite supply.** Recorded history is bottomless and algorithmically
  searchable — critical for an automated channel.
- **Evergreen by construction.** Nothing depends on the news cycle.
- **Naturally shareable.** "You will not believe this" is the whole format.
- **Hook writes itself.** Every topic opens on an absurd claim.

Tone: **affectionate disbelief.** Never mean-spirited, never gory, never
punching down. The comedy is "humans are ridiculous", not cruelty.

---

## 2. The look

Locked in `config.py → MASTER_STYLE_PROMPT`.

**Retro 1960s pulp cartoon poster art.** Warm cream paper, bold vintage red,
deep teal, mustard gold, heavy black ink, halftone texture.

Chosen over brighter flat-vector options because it is **distinctive and
ownable** — very little on YouTube looks like this, so a frame is recognisably
yours. The palette is the brand: it is what makes independently generated images
read as one channel.

Three rules that carry the most weight:

- **No text in images, ever.** The model renders it as gibberish — an early test
  produced a popcorn tub reading "POPORN". Banned in the style prompt *and* in
  the scene writer, because words like "marquee" or "sign" in a scene
  description will summon lettering on their own.
- **Full bleed.** Without this rule the model boxes artwork inside a decorative
  border and wastes 40% of the frame on empty margin.
- **Expressive characters.** Unlike a systems channel, comedy needs faces
  mid-shock. Character consistency across scenes is not guaranteed, but the
  heavy stylisation hides it and the gag matters more.

---

## 3. The edit

Locked in `video_stitcher.py`.

- **Slow Ken Burns on every shot**, direction alternating. Previously
  `zoompan=z=1`, which applies no zoom at all — a frozen slideshow, and the
  biggest single reason early videos felt lifeless.
- **0.4s crossfades**, with shot lengths padded so video still matches the
  master audio exactly.
- **Captions**: Arial Black, heavy outline. Sizes are ASS script units scaled by
  `video_height/288`, *not* pixels — getting this wrong once pushed short-form
  captions entirely off screen.
- **Encoding**: `preset medium`, `crf 19`.

---

## 4. The voice

`en-US-BrianMultilingualNeural` at **+8% rate**.

Tagged "approachable, casual, sincere" — it sounds like a person telling you
something ridiculous. The previous voice (Andrew, 0% rate) is tagged "warm,
confident, authentic", which reads as a nature documentary and made everything
feel slow. Rate is most of what separates energetic from sleepy.

One voice, never changed. It is as much the brand as the palette.

---

## 5. The writing

Locked in `script_analyzer.py`. Every script:

| Segment | Job |
|---|---|
| **Hook** (~15s) | The absurd claim, stated flat. No intro, no "hey guys". |
| **Setup** | The context that makes the absurdity land. |
| **Beat 1 / 2 / 3** | Escalating madness — each less believable than the last. |
| **Punchline** | The most ridiculous detail, saved for the end. |
| **CTA** | One line. |

Escalation is the engine: the viewer stays because it keeps getting worse.

**Targets:** 70%+ retention at 30s, 50%+ overall, 4%+ CTR.

---

## 6. Cadence

- **Long form:** 6–9 minutes, 1–2 per week. Multiple laws/stories per video
  suits the format naturally.
- **Shorts:** 3–5 per week, one story each. Shorts feed discovery, long form
  earns.

---

## 7. What to do next

1. Publish 10–15 videos before judging anything. Early data is noise.
2. Hold the theme for at least 3 months. Repetition teaches the algorithm.
3. After ~15 videos, run the feedback loop and let hook and topic performance
   drive the next batch.

---

## Operational note

Image generation runs on **Fal.ai** (`IMAGE_PROVIDER=fal`), ~$0.0017/image
versus Gemini's ~$0.067. This Google account's free tier also grants zero quota
for `gemini-3.1-flash-image` (HTTP 429, `limit: 0`), so Fal is both cheaper and
the only one that currently works.
