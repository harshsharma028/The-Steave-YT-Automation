import os
import sys
import threading
import time
import json


import subprocess
import logging
from script_analyzer import analyze_script
from audio_generator import generate_audio
from subtitle_generator import generate_subtitles
from prompt_generator import generate_image_prompt
from image_generator import generate_image
from video_stitcher import create_video
from utils import create_project_folder, setup_logger, slugify
from config import OUTPUT_DIR, USD_TO_INR_RATE


logger = setup_logger("MainPipeline")

def save_state(filepath, state_data):
    """Saves the current pipeline state to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(state_data, f, indent=4)

def load_state(filepath):
    """Loads pipeline state from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def run_interactive_pipeline(input_path, video_format="long form"):
    logger.info("\n===========================================")
    logger.info("   INTERACTIVE VIDEO GENERATION PIPELINE   ")
    logger.info("===========================================")

    state_file = "blueprint.json"
    project_folder = ""
    state = {}

    # ========== PHASE 1: ANALYZE SCRIPT OR RESUME PROJECT ==========
    if os.path.isdir(input_path):
        # Resume existing project from folder
        project_folder = input_path
        state_path = os.path.join(project_folder, state_file)
        if os.path.exists(state_path):
            logger.info(f"📂 Resuming: {project_folder}")
            state = load_state(state_path)
            video_format = state.get("video_format", "long form")
        else:
            logger.error("❌ No blueprint.json found in folder")
            return
    elif os.path.isfile(input_path):
        # New project: analyze script
        print("\n" + "="*60)
        print("PHASE 1: SCRIPT ANALYSIS")
        print("="*60)
        logger.info("📝 Phase 1: Script Analysis")

        with open(input_path, 'r', encoding='utf-8') as f:
            script_text = f.read()

        state = analyze_script(script_text)
        if not state:
            logger.error("❌ Script analysis failed")
            return

        title = state.get("title", "Untitled Project")
        state["video_format"] = video_format
        project_folder = create_project_folder(title, OUTPUT_DIR, video_format)

        # Initialize phase completion flags
        state["segments_flattened"] = False
        state["subtitles_generated"] = False
        state["video_generated"] = False

        save_state(os.path.join(project_folder, state_file), state)
        logger.info(f"✓ Project created: {project_folder}")
    else:
        logger.error("❌ Invalid input path")
        return

    state_path = os.path.join(project_folder, state_file)

    # ========== PHASE 2: BREAK SEGMENTS INTO VISUAL SUB-SCENES ==========
    if not state.get("segments_flattened"):
        print("\n" + "="*60)
        print("PHASE 2: STORYBOARD GENERATION")
        print("="*60)
        logger.info("🎨 Phase 2: Visual Prompt Generation")

        final_segments = []
        total_chunks = len(state["segments"])

        for i, chunk in enumerate(state["segments"]):
            logger.info(f"  Segment {i+1}/{total_chunks}")
            sub_scenes = generate_image_prompt(chunk["text"], i, project_folder)

            if sub_scenes:
                for j, scene in enumerate(sub_scenes):
                    new_seg = {
                        "narrative_phase": chunk.get("narrative_phase", "Scene"),
                        "text": scene["script_part"],
                        "image_prompt": scene["image_prompt"],
                        "parent_order": i + 1,
                        "sub_order": j + 1,
                        "audio_generated": False,
                        "image_generated": False
                    }
                    final_segments.append(new_seg)
            else:
                logger.error(f"❌ Prompt generation failed for segment {i+1}")
                return

        # Flatten: replace chunks with visual scenes
        state["segments"] = final_segments
        state["segments_flattened"] = True

        # Generate output filenames (one-time operation)
        for i, seg in enumerate(state["segments"]):
            safe_phase = slugify(seg.get("narrative_phase", "scene"))
            seg["image_filename"] = f"segment_{i+1:03d}_{safe_phase}.png"
            seg["audio_filename"] = f"audio_{i+1:03d}.mp3"

        save_state(state_path, state)
        logger.info(f"✓ Storyboard: {len(state['segments'])} visual scenes")

    # ========== PHASE 3: GENERATE AUDIO & SUBTITLES ==========
    print("\n" + "="*60)
    print("PHASE 3: AUDIO & SUBTITLES")
    print("="*60)
    logger.info("🔊 Phase 3: Audio & Subtitles Generation")

    full_audio_paths = []
    total_segments = len(state["segments"])

    # Generate per-segment audio (TTS)
    for i, segment in enumerate(state["segments"]):
        seg_audio_path = os.path.join(project_folder, segment["audio_filename"])
        full_audio_paths.append(seg_audio_path)

        if not segment.get("audio_generated"):
            logger.info(f"  Audio {i+1}/{total_segments}...")
            if generate_audio(segment['text'], seg_audio_path):
                segment["audio_generated"] = True
            else:
                logger.error(f"❌ Audio generation failed for segment {i+1}")
                return

    # Batch state save after all audio is done (not per-segment)
    save_state(state_path, state)

    # Combine audio + generate subtitles (if not done)
    audio_path = os.path.join(project_folder, "audio.mp3")
    subtitle_path = os.path.join(project_folder, "subtitles.srt")

    if not state.get("subtitles_generated"):
        logger.info("🎬 Concatenating audio & generating subtitles...")
        concat_list_path = os.path.join(project_folder, "audio_list.txt")

        # Create FFmpeg concat manifest
        with open(concat_list_path, "w") as f:
            for p in full_audio_paths:
                f.write(f"file '{os.path.basename(p)}'\n")

        # Concatenate audio files
        subprocess.run(
            ["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_list_path, "-c", "copy", "-y", audio_path],
            capture_output=True
        )

        # Generate subtitles via Whisper
        if generate_subtitles(audio_path, subtitle_path, video_format=video_format):
            state["subtitles_generated"] = True
            save_state(state_path, state)
            logger.info("✓ Audio & subtitles complete")
        else:
            logger.error("❌ Subtitle generation failed")
            return

    # ========== PHASE 4: GENERATE IMAGES ==========
    print("\n" + "="*60)
    print("PHASE 4: IMAGE GENERATION")
    print("="*60)
    logger.info("🖼️  Phase 4: Image Generation")

    # Determine if any images are ungenerated
    has_ungenerated = any(not seg.get("image_generated") for seg in state["segments"])
    manual_verify = True
    image_provider = state.get("image_provider", "gemini")

    if has_ungenerated:
        manual_verify = input("\nManually verify prompts? (yes/no): ").strip().lower() in ['yes', 'y']

        # Select image provider (Gemini is faster, Fal has more models)
        prov_choice = input("Provider (gemini/fal) [default: gemini]: ").strip().lower()
        image_provider = "fal" if "fal" in prov_choice else "gemini"
        state["image_provider"] = image_provider
        save_state(state_path, state)
    
    background_tasks = {}  # Tracks running image generation threads

    def check_background_tasks():
        """Check completed background tasks & update state (non-blocking)."""
        completed = []
        for idx, task in background_tasks.items():
            if not task["thread"].is_alive():
                completed.append(idx)
                res = task["result"]
                seg = task["segment"]

                if res:
                    success, cost_usd = res[0]
                    if success:
                        seg["image_generated"] = True
                        seg["image_cost_usd"] = cost_usd
                        cost_inr = cost_usd * USD_TO_INR_RATE
                        logger.info(f"✓ BG: Segment {idx+1} | ${cost_usd:.4f} (₹{cost_inr:.2f})")
                    else:
                        logger.warning(f"✗ BG: Segment {idx+1} failed")
                else:
                    logger.warning(f"✗ BG: Segment {idx+1} aborted")

        # Batch state save for all completed tasks
        if completed:
            save_state(state_path, state)
            for idx in completed:
                del background_tasks[idx]

    for i, segment in enumerate(state["segments"]):
        # Check for completed background tasks
        check_background_tasks()

        # Skip if already generated
        if segment.get("image_generated"):
            continue

        # Recovery: check if image already exists on disk (prevents re-billing)
        img_path = os.path.join(project_folder, segment["image_filename"])
        if os.path.exists(img_path):
            segment["image_generated"] = True
            save_state(state_path, state)
            logger.info(f"📂 Recovery: Segment {i+1} already on disk (saved API cost)")
            continue

        # If task is already running in background, wait or skip
        if i in background_tasks:
            logger.info(f"⏳ Segment {i+1}: waiting for background task...")
            task = background_tasks[i]

            # Wait up to 5 min for completion
            waited = 0
            max_wait = 300
            while task["thread"].is_alive() and waited < max_wait:
                time.sleep(10)
                waited += 10
                check_background_tasks()
                if waited % 60 == 0:
                    logger.info(f"  ⏳ {waited//60} min elapsed...")

            # If still running, move on (task continues in background)
            if task["thread"].is_alive():
                logger.info(f"⏸️  Backgrounding: segment {i+1} (>5 min, proceeding)")
                continue
            else:
                check_background_tasks()
                if segment.get("image_generated"):
                    continue

        # ========== Manual Verification Mode ==========
        if manual_verify:
            print(f"\n{'─'*60}")
            print(f"SEGMENT {i+1}/{len(state['segments'])} | {segment.get('narrative_phase', 'Scene').upper()}")
            print(f"{'─'*60}")
            print(f"Dialogue: \"{segment['text'][:60]}...\"")
            print(f"Prompt: {segment['image_prompt'][:80]}...")
            print(f"{'─'*60}")

            if input("\nEdit prompt? (yes/no): ").strip().lower() in ['yes', 'y']:
                new_prompt = input("New prompt: ").strip()
                if new_prompt:
                    segment['image_prompt'] = new_prompt
                    save_state(state_path, state)

        else:
            logger.info(f"📸 Segment {i+1}/{len(state['segments'])}")

        # ========== START IMAGE GENERATION THREAD ==========
        aspect_ratio = "9:16" if video_format == "short form" else "16:9"
        result_container = []

        gen_thread = threading.Thread(
            target=generate_image,
            args=(segment['image_prompt'], img_path, result_container, False, aspect_ratio, image_provider)
        )

        gen_thread.start()

        # Wait up to 5 min with status updates
        waited = 0
        max_wait = 300
        while gen_thread.is_alive() and waited < max_wait:
            time.sleep(10)
            waited += 10
            check_background_tasks()
            if waited % 60 == 0:
                logger.info(f"  ⏳ Segment {i+1}: {waited//60} min elapsed")

        if gen_thread.is_alive():
            # Timeout: move to background task tracking
            logger.info(f"⏸️  Backgrounding: segment {i+1} (>5 min)")
            background_tasks[i] = {
                "thread": gen_thread,
                "segment": segment,
                "result": result_container
            }
        else:
            # Completed within timeout
            if result_container:
                success, cost_usd = result_container[0]
                if success:
                    segment['image_generated'] = True
                    segment['image_cost_usd'] = cost_usd
                    save_state(state_path, state)
                    cost_inr = cost_usd * USD_TO_INR_RATE
                    logger.info(f"✓ Segment {i+1}: ${cost_usd:.4f} (₹{cost_inr:.2f})")

                    if manual_verify:
                        if input("Check image. Continue? (yes/no): ").strip().lower() != 'yes':
                            logger.info(f"⏸️  Pipeline paused at segment {i+1}")
                            sys.exit(0)
                else:
                    logger.warning(f"✗ Segment {i+1}: generation failed (retry on resume)")
            else:
                logger.warning(f"✗ Segment {i+1}: no result")

    # ========== PHASE 5: STITCH FINAL VIDEO ==========
    print("\n" + "="*60)
    print("PHASE 5: VIDEO STITCHING")
    print("="*60)
    logger.info("🎬 Phase 5: Final Video Stitching")

    # Sync remaining background tasks before stitching
    if background_tasks:
        logger.info(f"⏳ Waiting for {len(background_tasks)} background tasks...")
        waited = 0
        while background_tasks:
            time.sleep(10)
            waited += 10
            check_background_tasks()
            if waited % 60 == 0:
                active = [f"Seg {k+1}" for k in background_tasks]
                logger.info(f"  ⏳ Still waiting: {', '.join(active)}")

    # Verify all images exist
    missing = [idx + 1 for idx, seg in enumerate(state["segments"]) if not seg.get("image_generated")]
    if missing:
        logger.error(f"❌ Missing images: segments {missing}")
        logger.info("Run option 2 to resume & complete")
        return

    # Stitch video
    if not state.get("video_generated"):
        if input("\n✓ All ready! Stitch video? (yes/no): ").strip().lower() in ['yes', 'y']:
            add_audio = input("Add voiceover? (yes/no): ").strip().lower() in ['yes', 'y']
            add_captions = input("Add subtitles? (yes/no): ").strip().lower() in ['yes', 'y']

            output_video_path = os.path.join(project_folder, "final_video.mp4")
            if create_video(
                project_folder,
                state["segments"],
                audio_path,
                subtitle_path,
                output_video_path,
                include_audio=add_audio,
                include_captions=add_captions,
                video_format=video_format
            ):
                state["video_generated"] = True
                save_state(state_path, state)
                logger.info(f"✓✓✓ COMPLETE! Video: {output_video_path}\n")
            else:
                logger.error("❌ Stitching failed")
        else:
            logger.info("⏸️  Paused. Run option 2 to resume")
    else:
        logger.info("✓ Video already generated")



if __name__ == "__main__":
    logging.getLogger().handlers.clear()
    
    print("\n===========================================")
    print("      VIDEO GENERATION PIPELINE CLI        ")
    print("===========================================")
    print("1. Start a New Project (Enter Script)")
    print("2. Resume an Existing Project")
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == '1':
        format_choice = input("\nEnter video format (long form / short form) [default: long form]: ").strip().lower()
        if "short" in format_choice or format_choice == "s":
            video_format = "short form"
        else:
            video_format = "long form"

        has_blueprint = input("\nDo you have a video blueprint? (yes/no): ").strip().lower() in ['yes', 'y']
        
        if has_blueprint:
            project_name = input("\nEnter project name: ").strip()
            if not project_name:
                project_name = "Imported Project"
                
            print("\n--- Paste your storyboard JSON below ---")
            print("(Type 'DONE' on a new line when finished)\n")
            json_lines = []
            while True:
                try:
                    line = input()
                    if line.strip().upper() == 'DONE': break
                    json_lines.append(line)
                except EOFError: break
            
            json_text = "\n".join(json_lines).strip()
            if not json_text:
                print("[ERROR] No JSON input provided.")
                sys.exit(1)
                
            prompt_key = input("\nEnter the image prompt key name: ").strip()
            script_key = input("Enter the script text (dialogue) key name: ").strip()
            
            try:
                parsed_json = json.loads(json_text)
                
                # Extract the list of items
                items_list = None
                if isinstance(parsed_json, list):
                    items_list = parsed_json
                elif isinstance(parsed_json, dict):
                    for k, v in parsed_json.items():
                        if isinstance(v, list):
                            items_list = v
                            break
                    if items_list is None:
                        items_list = [parsed_json]
                        
                if not items_list:
                    raise ValueError("Could not find any list of items in the JSON.")
                
                # Build segments
                segments = []
                for idx, item in enumerate(items_list):
                    text_val = item.get(script_key, "")
                    prompt_val = item.get(prompt_key, "")
                    
                    # Case-insensitive fallback check
                    if not text_val and not prompt_val:
                        for k, v in item.items():
                            if k.lower() == script_key.lower():
                                text_val = v
                            if k.lower() == prompt_key.lower():
                                prompt_val = v
                                
                    segments.append({
                        "narrative_phase": item.get("narrative_phase", f"Scene {idx+1}"),
                        "text": str(text_val),
                        "image_prompt": str(prompt_val),
                        "parent_order": idx + 1,
                        "sub_order": 1,
                        "audio_generated": False,
                        "image_generated": False,
                        "image_filename": f"segment_{idx+1:03d}_scene.png",
                        "audio_filename": f"audio_{idx+1:03d}.mp3"
                    })
                    
                state = {
                    "title": project_name,
                    "segments": segments,
                    "segments_flattened": True,
                    "subtitles_generated": False,
                    "video_generated": False,
                    "video_format": video_format
                }
                
                # Create nested project folder
                project_folder = create_project_folder(project_name, OUTPUT_DIR, video_format)
                state_path = os.path.join(project_folder, "blueprint.json")
                save_state(state_path, state)
                print(f"\n[INFO] Project successfully imported from blueprint. Saved at: {project_folder}")
                
                # Execute pipeline passing the folder (which resumes directly to Phase 3)
                run_interactive_pipeline(project_folder)
                
            except Exception as e:
                print(f"\n[ERROR] Failed to parse JSON or build blueprint: {e}")
                
        else:
            # Traditional script analysis pipeline
            print("\n--- Paste your script below ---")
            print("(Type 'DONE' on a new line when finished)\n")
            lines = []
            while True:
                try:
                    line = input()
                    if line.strip().upper() == 'DONE': break
                    lines.append(line)
                except EOFError: break
            
            script_text = "\n".join(lines).strip()
            if script_text:
                tmp_path = "temp_script_input.txt"
                with open(tmp_path, "w", encoding="utf-8") as f: f.write(script_text)
                run_interactive_pipeline(tmp_path, video_format)
                if os.path.exists(tmp_path): os.remove(tmp_path)
    elif choice == '2':
        folder = input("\nEnter project folder path: ").strip()
        if os.path.isdir(folder): run_interactive_pipeline(folder)
    else:
        print("Invalid choice.")
