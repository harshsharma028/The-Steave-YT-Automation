# The Steave - AI Video Generation Pipeline

## Project Overview

**The Steave** is an ambitious automation platform that transforms text scripts or JSON storyboards into fully generated videos with AI-generated imagery, voiceovers, and captions.

### Goal
Automate video generation from provided JSON input (scenes + dialogue) through a complete 5-phase pipeline, reducing manual video creation time from hours to minutes.

---

## Architecture & Phases

### Phase 1: Script Analysis
- **File**: `script_analyzer.py`
- **Input**: Raw script text
- **Output**: JSON with segments, each assigned a narrative_phase (Hook, Main Plot, Climax, etc.)
- **API**: Gemini 2.5 Flash (TEXT_MODEL)
- **Key**: Preserves exact original text, no rephrasing

### Phase 2: Visual Prompt Generation  
- **File**: `prompt_generator.py`
- **Input**: Script segments
- **Output**: Sub-scenes (1-4 per segment) with image_prompt descriptions
- **API**: Gemini 2.5 Flash
- **Logic**: Animation-director style prompts (characters, emotions, environments, composition)
- **Saves**: Raw JSON responses to `prompt_response_chunk_*.json` for debugging

### Phase 3: Audio & Subtitles
- **Files**: `audio_generator.py`, `subtitle_generator.py`
- **Audio**: Microsoft Edge TTS (async) → MP3 per scene
- **Subtitles**: FFmpeg concat → master audio → Whisper transcription → SRT
- **Output**: Full `audio.mp3` + `subtitles.srt`

### Phase 4: Interactive Image Generation
- **File**: `image_generator.py`
- **Providers**: 
  - **Gemini** (default): `gemini-3.1-flash-image`, 1K resolution, applies MASTER_STYLE_PROMPT
  - **Fal.ai**: `fal-ai/nano-banana` or flux models, supports dynamic aspect ratios
- **Features**:
  - Manual verification mode (review & edit prompts before generating)
  - Parallel background task handling (threads, result containers)
  - Aspect ratio: 16:9 (long-form) or 9:16 (short-form)
  - Cost tracking (USD → INR conversion)
  - Atomic file writes (.tmp → rename pattern)
  - Recovery: checks disk for existing images to save API costs
- **Retry Logic**: 4 attempts with exponential backoff (5s, 10s, 20s, 40s)

### Phase 5: Video Stitching
- **File**: `video_stitcher.py`
- **Tool**: FFmpeg with complex filter graphs
- **Features**:
  - Zoompan filter (z=1) to stretch static images to match audio duration
  - Subtitle overlay with cartoon styling (Comic Sans, thick outlines)
  - Supports 16:9 (1920×1080) and 9:16 (1080×1920) formats
  - Optional voiceover and captions toggles
- **Output**: `final_video.mp4`

---

## Key Files & Responsibilities

| File | Purpose |
|------|---------|
| `main.py` | Entry point, orchestrates pipeline phases, handles state save/resume |
| `config.py` | API keys, models, pricing, master style prompt, video settings |
| `script_analyzer.py` | Gemini script→segments analysis |
| `prompt_generator.py` | Gemini segment→visual sub-scenes breakdown |
| `image_generator.py` | Image generation (Gemini/Fal.ai), cost calculation, retries |
| `audio_generator.py` | Edge TTS async wrapper |
| `subtitle_generator.py` | Whisper transcription, SRT generation |
| `video_stitcher.py` | FFmpeg orchestration, filter graphs |
| `utils.py` | Project folder creation, logging, text slugification |
| `blueprint.json` | State file (project-level, auto-created), enables resume capability |

---

## Configuration & APIs

### Environment Variables (.env)
```
CHAT_API_KEY=<Gemini API key>
IMAGE_API_KEY=<Gemini API key (same)>
IMAGE_MODEL=gemini-3.1-flash-image
TEXT_MODEL=gemini-2.5-flash
TTS_VOICE=en-US-AndrewMultilingualNeural
OUTPUT_DIR=projects
FAL_MODEL=fal-ai/nano-banana
FAL_KEY=<Fal.ai API key>
WHISPER_MODEL=base
```

### Pricing & Cost Tracking
- **Gemini Images**: $60 per 1M output tokens, ~1120 tokens per 1K image → ~$0.067 per image
- **Fal.ai**: ~$0.003 per megapixel (varies by model)
- **USD→INR**: 95.20 (adjustable in config.py)
- Costs are tracked per-image and stored in state

### Master Style Prompt
Located in `config.py` → applied to all image generation requests. Ensures:
- 2D educational cartoon style (YouTube explainer aesthetic)
- Stickman characters with thick outlines
- Bright, colorful environments
- Story-driven composition (no floating objects, no thumbnails)

---

## Development Guidelines

### When Adding Features
1. **Modify main.py first** - Add phase logic in appropriate section (marked by comments)
2. **Create new helper module** if it deserves its own scope (e.g., `new_feature.py`)
3. **Update state tracking** - Add flags to `blueprint.json` schema if needed
4. **Preserve resume logic** - Check `state.get("flag")` to support resuming mid-pipeline
5. **Test with both paths**:
   - Fresh script input (Phase 1 start)
   - Resume from existing project (Phase 3+ start)

### State Management
- Single source of truth: `blueprint.json` in project folder
- Save via `save_state()` after each phase milestone
- Load via `load_state()` on resume
- Flags track completion: `segments_flattened`, `subtitles_generated`, `video_generated`, etc.

### Error Handling
- Use logger (from utils) for all errors/info
- Return `(success: bool, cost_usd: float)` from image_generator
- Use result_container lists for thread results (append tuples)
- Implement retry logic with exponential backoff for API calls

### Threading & Background Tasks
- Image generation runs in threads to parallelize
- Store thread references in `background_tasks = {index: {"thread": t, "segment": s, "result": r}}`
- Check completion periodically with `check_background_tasks()`
- Wait max 5 minutes per image, then background and move on

### File Naming Conventions
- Images: `segment_001_scene.png`, `segment_002_hook.png` (slugified narrative_phase)
- Audio: `audio_001.mp3`, `audio_002.mp3`
- Prompts: `prompt_response_chunk_000.json`, `prompt_response_chunk_001.json`
- Master: `audio.mp3`, `subtitles.srt`, `final_video.mp4`, `blueprint.json`

---

## JSON Blueprint Format (User Input)

Users can skip Phase 1 by providing a JSON blueprint directly:

```json
{
  "title": "My Video",
  "scenes": [
    {
      "narrative_phase": "Hook",
      "script_text": "Welcome to...",
      "image_prompt": "A bright character standing in..."
    },
    {
      "narrative_phase": "Main Plot",
      "script_text": "Let me show you...",
      "image_prompt": "The character pointing at..."
    }
  ]
}
```

- **Flexible**: Accepts nested objects or top-level lists
- **Key mapping**: User specifies `script_key` and `prompt_key` names
- **Case-insensitive**: Falls back to lowercase key matching
- **Output**: Converts to internal segment format, skips to Phase 3

---

## Workflow Examples

### Example 1: Fresh Script Start
```
1. User runs main.py → Choice 1
2. User selects "long form"
3. User pastes script
→ Phase 1: Script analyzed, segments created
→ Phase 2: Prompts generated, sub-scenes created
→ Phase 3: Audio generated, subtitles made
→ Phase 4: Images generated (with manual verification if chosen)
→ Phase 5: Video stitched
```

### Example 2: Resume from Checkpoint
```
1. User runs main.py → Choice 2
2. User enters project folder path
3. System loads blueprint.json
→ Phase 3+: Skips to first incomplete phase
→ E.g., if audio is done but images aren't, starts Phase 4
```

### Example 3: JSON Blueprint Import
```
1. User runs main.py → Choice 1 → "yes to blueprint"
2. User provides JSON + key names
→ Skips Phase 1 & 2, goes straight to Phase 3
```

---

## Known Patterns & Gotchas

1. **API Rate Limits**: Gemini throttles during high demand. All API calls include 2-5s cooldown + retry logic.
2. **FFmpeg Paths**: Requires ffmpeg & ffprobe in PATH. Windows users should install via chocolatey or add to PATH manually.
3. **Atomic Writes**: Images use .tmp pattern to prevent partial/corrupted saves.
4. **Thread Safety**: Result containers are lists (thread-safe for append), checked in main thread.
5. **Cost Precision**: Gemini cost is theoretical ($0.067/img). Actual billing may vary; Fal.ai cost based on dimensions.
6. **Subtitle Escape**: FFmpeg filter strings require escaping backslashes and colons for file paths.
7. **Image Recovery**: If a segment's image exists on disk, it's marked as generated without re-billing (line 224 in main.py).

---

## Testing & Debugging

### Test Files (in `testing_artifacts/`)
- `test_image.py` - Test image generation independently
- `test_audio.py` - Test TTS audio generation
- `test_script.py` - Test script analysis
- `test_image_prompt.py` - Test prompt generation
- `debug_image_format.py` - Debug image format/resolution issues

### Quick Debugging
1. **Check logs**: Each module sets up `setup_logger()` → outputs to console + file
2. **Verify API keys**: Ensure .env has valid CHAT_API_KEY, IMAGE_API_KEY, FAL_KEY
3. **Test Gemini API**: Run `python -c "from google import genai; print('OK')"` to verify installation
4. **Check FFmpeg**: Run `ffmpeg -version` and `ffprobe -version` in terminal
5. **Inspect state**: Read `blueprint.json` in project folder to see current progress

---

## Future Enhancements

- [ ] Batch processing: Handle multiple scripts in parallel
- [ ] Custom voice profiles beyond Edge TTS
- [ ] Real-time progress dashboard / web UI
- [ ] Analytics: Track costs, generation times, success rates
- [ ] Music/SFX integration (currently audio is voiceover only)
- [ ] More video formats (4:3, 1:1, etc.)
- [ ] Caching layer for repeated prompts/images

---

## Collaboration Notes

- **Git commits**: Include the attribution lines from Claude sessions (model + session ID)
- **State files**: Never manually edit `blueprint.json` while pipeline is running
- **API costs**: Test with small projects first; Gemini images @ $0.067 each
- **Async work**: Audio generation is async; image generation is threaded but controlled in main thread
