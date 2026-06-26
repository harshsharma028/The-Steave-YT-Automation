# The Steave: Automated Explainer Video Generation Pipeline

An interactive Python command-line utility that converts raw text scripts into fully compiled, animated educational videos in a 2D vector cartoon style. It automatically handles script chunking, prompt generation, image synthesis, text-to-speech voiceovers, subtitle transcriptions, and video/audio stitching.

---

## 🚀 Key Features

- **Script Analysis**: Uses Gemini (`gemini-2.5-flash`) to group scripts into logical narrative phases (e.g., Hook, Main Plot, Climax) rather than rigid sentences.
- **Visual Storyboard Breakdown**: Divides narrative chunks into 1–4 specific scenes with automatically generated image prompts.
- **Automated / Manual Modes**: Prompt verification options allow you to either visually verify and edit prompts segment-by-segment (Manual), or run the pipeline completely unattended (Automated).
- **Concurrent Image Generation with Backgrounding**: Spawns image requests in separate background worker threads. The script waits up to 5 minutes for each image to complete; if it takes longer, the task is backgrounded so you can continue setting up or generating other segments.
- **1-Minute Live Status Polling**: Displays console updates every 1 minute showing progress, elapsed time, and a list of all active background generation tasks.
- **API Cost-Savings Recovery**: Automatically scans the project folder on startup. If an image file already exists on disk, it marks it as generated and skips the API request, preventing accidental double-billing.
- **Atomic Image Writes**: Saves images to a temporary path (`.tmp`) first and renames them only upon 100% completion. This prevents corrupt/partially-downloaded files from being registered as successful.
- **Daily Date Folders**: Automatically nested folders (`projects/YYYY-MM-DD/`) organize your workspace by date.
- **Double Currency Cost Reporting**: Prints estimated generation costs in both USD ($) and Indian Rupees (₹).
- **Edge Text-to-Speech (TTS)**: Converts segment scripts into high-quality spoken audio using Microsoft Edge Neural voices.
- **Automated Subtitles**: Transcribes master audio using OpenAI's Whisper model (size configurable in `.env`) to generate timed, logically-aligned SRT subtitles.
- **FFmpeg Stitching**: Synchronizes static images to audio clip durations, overlays styled subtitles (Comic Sans, outlined), and stitches the elements into a final `.mp4` video.

---

## 🛠️ Prerequisites

This project relies on **FFmpeg** and **FFprobe** for audio/video stitching, which must be installed on your operating system and added to your system's PATH.

### Installing FFmpeg

#### Windows (using winget or Chocolatey)
```powershell
# Using winget
winget install Gyan.FFmpeg

# Using Chocolatey
choco install ffmpeg
```

#### macOS (using Homebrew)
```bash
brew install ffmpeg
```

#### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install ffmpeg
```

---

## 📦 Project Directory Structure

```text
├── .env                  # Configuration keys and environment settings (ignored by Git)
├── .gitignore            # Specifying untracked files to ignore
├── requirements.txt      # Python dependencies to install on new devices
├── config.py             # Setup configurations, style prompts, and API models
├── utils.py              # File logger, slugify helper, and folder creator
├── script_analyzer.py    # Sub-module analyzing input script with Gemini
├── prompt_generator.py   # Sub-module generating detailed scene visual descriptions
├── image_generator.py    # Sub-module creating scenes using Gemini image synthesis
├── audio_generator.py    # Sub-module generating TTS voice files via Edge TTS
├── subtitle_generator.py # Sub-module producing SRT subtitle transcripts via Whisper
├── video_stitcher.py     # Sub-module running FFmpeg command pipelines to build videos
├── main.py               # Central interactive CLI coordinator and state manager
└── projects/             # Directory containing generated output assets (ignored by Git)
```

---

## 💻 Setup & Installation on New Devices

Follow these steps to run the project from scratch on any new computer:

### 1. Clone the Repository
```bash
git clone <your-github-repo-url>
cd the-steave
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

> [!NOTE]
> Installing `openai-whisper` will automatically download PyTorch (`torch`) as a dependency. If you have an Nvidia GPU and want faster transcription, make sure to install a CUDA-compatible version of PyTorch from the [official PyTorch website](https://pytorch.org/).

### 4. Configure Environment Variables
Create a file named `.env` in the root folder of the project:
```env
CHAT_API_KEY=your_gemini_api_key_here
IMAGE_API_KEY=your_gemini_api_key_here
IMAGE_MODEL=gemini-3.1-flash-image
TEXT_MODEL=gemini-2.5-flash
TTS_VOICE=en-US-AndrewMultilingualNeural
OUTPUT_DIR=projects

# Whisper Subtitles Transcription Settings
WHISPER_MODEL=base
```

---

## 📖 Step-by-Step Function Walkthrough

Here is an analysis of each Python module and function in the pipeline:

### 1. `config.py`
Defines the base configurations for the application:
- **`load_dotenv()`**: Loads configuration variables from the `.env` file.
- **Style Settings**: Sets video size parameters (`1920x1080`), aspect ratios (`16:9`), Whisper model config, and conversion rates for tracking image generation costs.
- **`MASTER_STYLE_PROMPT`**: The core prompt template used to enforce a consistent 2D cartoon, stick-figure aesthetic with thick outlines and round faces across generated images.

### 2. `utils.py`
Helper utilities for project execution:
- **`setup_logger(name)`**: Configures a logger to output clean and compact logs to the console (`[ComponentName] LEVEL: Message`) and detailed logs with timestamps to `pipeline.log`.
- **`slugify(text)`**: Cleans up text inputs to create safe file and folder names by removing special characters and replacing spaces with underscores.
- **`create_project_folder(script_title, base_dir)`**: Creates a timestamped folder inside a daily date-stamped folder (e.g., `projects/YYYY-MM-DD/project_name_timestamp`) for storing script analysis, generated audio, images, SRT files, and final videos.

### 3. `script_analyzer.py`
Handles initial narrative planning:
- **`analyze_script(script_text)`**: Sends the raw text script to Gemini. The model groups the script into logical chunked segments (e.g., Hook, Main Plot, Ending) instead of strict sentence limits. Returns a JSON blueprint containing a descriptive video title and segments. Features API cooldown wait times and retries.

### 4. `prompt_generator.py`
Translates narrative segments into visual scenes:
- **`generate_image_prompt(chunk_text, chunk_index, project_folder)`**: Takes a script chunk and prompts Gemini to break it down into 1-4 individual visual scenes. Returns a list of sub-scenes detailing actions, emotions, environments, and background descriptions. Saves the raw response to `prompt_response_chunk_xxx.json`.

### 5. `image_generator.py`
Handles image creation:
- **`generate_image(scene_description, output_path, result_container, verbose)`**: Sends the visual description combined with the `MASTER_STYLE_PROMPT` to Gemini (`gemini-3.1-flash-image`). It extracts the returned inline image data, saves the image atomically using temporary files to avoid corruption, and calculates the USD cost based on tokens consumed. Supports appending results to a container for threaded background calls.

### 6. `audio_generator.py`
Generates voiceover tracks:
- **`generate_audio_async(text, output_path, voice)`**: Asynchronously communicates with Microsoft's Edge TTS API to generate high-quality voiceovers for a segment's dialogue text.
- **`generate_audio(text, output_path)`**: Synchronous wrapper around the async engine to allow integration in standard loops.

### 7. `subtitle_generator.py`
Generates subtitle tracks:
- **`generate_subtitles(audio_path, output_path)`**: Loads the Whisper transcription model. Transcribes the master audio and extracts word-level timestamps.
- **`format_timestamp(seconds)`**: Helper converting float seconds into SubRip (`HH:MM:SS,mmm`) formats.
- **Logical Flow Chunking**: Groups words into subtitle lines using commas, sentence ends, duration silence gaps (>0.4s), or a 5-word limit to keep reading flow natural.

### 8. `video_stitcher.py`
Performs final multimedia assembly:
- **`get_audio_duration(audio_path)`**: Executes `ffprobe` to determine the exact length of individual audio files in seconds.
- **`create_video(...)`**: Constructs an FFmpeg commands array. Uses a `zoompan` filter to turn static images into video clips matching the duration of their corresponding audio clip. Concatenates all clips together, overlays the master audio track, and applies customized styled captions (e.g., Comic Sans MS, outline styling, centered position) to create the final `.mp4` file.

### 9. `main.py`
The CLI application controller:
- **`save_state(...)` / `load_state(...)`**: Writes the current run progress to `blueprint.json` to enable crash resistance and resuming.
- **`run_interactive_pipeline(input_path)`**: Executes the 5-phase pipeline:
  1. *Phase 1*: Parses script text to establish project directories and blueprint states.
  2. *Phase 2*: Expands parent chunks into individual sub-scenes.
  3. *Phase 4*: Automatically detects if any image files already exist on disk and skips them. If there are new images, prompts the user to select **Manual** or **Automated** generation mode. Spawns background threads for Gemini requests, polling them every 10 seconds and printing status reports every 1 minute.
  4. *Phase 3*: Generates individual TTS audio clips, merges them into `audio.mp3`, and transcribes them to `subtitles.srt`.
  5. *Phase 5*: Waits for any remaining background generation threads to finish. Conducts validation checks to ensure no missing or corrupted images, then stitches them into `final_video.mp4`.

---

## 🛠️ Usage Instructions

Activate your virtual environment and run:

```bash
python main.py
```

### Options:
1. **Option 1 (Start New Project)**: Ask if you have a pre-existing video blueprint (storyboard JSON):
   - **If Yes (Blueprint Import)**: You will be asked to enter a project name, paste your storyboard JSON (terminated by typing `DONE` on a new line), and specify the exact key names for your image prompts and script text (dialogue). The script will automatically parse the JSON, set up the project folder under `projects/YYYY-MM-DD/`, and proceed directly to **Phase 3 (Audio & Subtitles)**—skipping Phase 1 and Phase 2 entirely (saving you processing time and API costs).
   - **If No (Standard script)**: You will be prompted to paste your raw script (terminated by typing `DONE`). The script will run the traditional pipeline, using Gemini to perform Phase 1 (Script Analysis) and Phase 2 (Sub-scene Breakdown & Prompt Generation).
2. **Option 2 (Resume Existing Project)**: Enter the path of an existing project folder (e.g. `projects/2026-06-16/how_does_gravity_work_20260616_120000`) to pick up where you left off.

---

## 🔒 Git and GitHub Preparation

Before adding this repository to your GitHub account:
1. Initialize the git repository:
   ```bash
   git init
   ```
2. Your `.gitignore` file is configured to prevent the following files from being committed:
   - **`.env`**: Contains your private Gemini API keys. **Never share these keys!**
   - **`projects/`**: Directory containing all generated large assets (MP3s, PNGs, SRTs, and MP4 videos).
   - **`pipeline.log`**: Log files generated during runtime.
   - **`__pycache__/`**: Python-compiled files.
3. Commit and push:
   ```bash
   git add .
   git commit -m "Initial commit: The Steave Explainer Video Pipeline"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```
