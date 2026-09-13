# Hidden Mechanics — Channel Strategy

The decisions below are locked in and already implemented in the pipeline.
Change them deliberately, not casually — consistency is the entire growth
mechanism here.

---

## 1. The niche

**Hidden Mechanics — how the systems behind everyday life actually work.**

Four content pillars, in rotation:

| Pillar | Example titles |
|---|---|
| Why things cost what they cost | Why popcorn costs more than the movie ticket |
| How everyday systems work | What actually happens when you tap your card |
| Why we do it this way | Why every keyboard is still QWERTY |
| Who actually profits | How free apps make more than paid ones |

**Why this niche:**

- **Evergreen by construction.** Nothing depends on news cycles. A video from
  today still earns views in three years.
- **Infinite supply.** This matters more than anything else for an automated
  channel. You will never run out of topics, and the topics are discoverable
  algorithmically.
- **Finance-adjacent RPM.** Money/business topics pull $10–20 RPM versus $3–5
  for generic curiosity content, without requiring you to give financial advice.
- **Built-in hooks.** Every topic is naturally a question, which is exactly the
  curiosity gap the first 15 seconds needs.
- **Works with still images.** No recurring characters means AI image
  inconsistency never shows.

**The single biggest change from before:** the old videos were scattered —
mosquitoes, giant ants, fire, borders, adulting. No theme means no returning
audience, no channel identity, and an algorithm that cannot categorise you.
One theme, held for months, is the growth mechanism.

---

## 2. The look

Locked in `config.py → MASTER_STYLE_PROMPT`.

**Flat vector editorial illustration.** Deep navy ground, warm amber focal
highlights, teal secondary, off-white, coral only for tension.

The palette *is* the brand. Every image is generated independently, so the only
thing that makes 200 images across 20 videos feel like one channel is holding
the same five colours. This is also why the style moved away from stickman
cartoons: those read as generic AI output, and thousands of channels use them.

Three rules that matter most:

- **No text in images, ever.** AI renders text as garbage, and even when legible
  it looks amateur. Explicitly forbidden in the prompt now.
- **Anonymous geometric figures, no faces.** A named character with a face will
  silently morph between every scene. Anonymous figures sidestep the problem
  entirely and read as more premium.
- **Lower fifth of frame kept calm** so subtitles always sit on clean space.

---

## 3. The edit

Locked in `video_stitcher.py`.

- **Slow Ken Burns on every shot**, direction alternating between shots so the
  video breathes. Previously `zoompan=z=1`, which is literally no zoom — it was
  a frozen slideshow, and that alone was the biggest reason it looked cheap.
- **0.4s crossfades** between shots instead of hard cuts, with the shot lengths
  padded so the video still matches the master audio exactly.
- **Captions**: Arial Black, heavy outline, no shadow. Comic Sans is gone.
- **Encoding**: `preset medium`, `crf 19`. The old `ultrafast`/`crf 22` was
  visibly soft, and flat vector art shows banding badly.

---

## 4. The writing

Locked in `script_analyzer.py`. Every script follows:

| Segment | Job |
|---|---|
| **Hook** (first ~15s) | The surprising claim or question. No intro, no branding, no "hey guys". |
| **Stakes** | Why this touches the viewer's own life. |
| **Beat 1 / 2 / 3** | Escalating explanation. Each answers something *and* opens a new question. |
| **Payoff** | The satisfying "so that's why". |
| **CTA** | One line, ~10s. |

The 15-second hook is the highest-value real estate in the video: videos that
hold 80% of viewers past 15 seconds get materially more reach, and retention
drops off a cliff without one.

**Targets:** 70%+ retention at 30 seconds, 50%+ overall on 5–10 minute videos,
4%+ CTR.

---

## 5. Cadence

- **Long form:** 6–9 minutes, 1–2 per week. Long enough for mid-roll ads, short
  enough to hold retention.
- **Shorts:** 3–5 per week, each one a single beat lifted from a long-form
  video. Shorts feed discovery; long form earns the money.
- **Voice:** one narrator voice, never changed. It is as much of the brand as
  the palette.

---

## 6. What to do next

1. Publish 10–15 videos before judging anything. Early data is noise.
2. Keep the theme fixed for at least 3 months even if it feels repetitive —
   repetition is what teaches the algorithm who to show you to.
3. After ~15 videos, run the feedback loop and let hook style and topic
   performance drive the next batch.
4. Only then consider widening the pillars.

---

## Open item

Image generation currently runs on **Fal.ai**, because this Google account's
free tier grants **zero** quota for `gemini-3.1-flash-image` (HTTP 429,
`limit: 0`). Either enable billing on the Google AI Studio project or leave the
provider set to `fal` — Fal.ai works and costs roughly $0.0017 per image, which
is cheaper than Gemini's ~$0.067 anyway.
