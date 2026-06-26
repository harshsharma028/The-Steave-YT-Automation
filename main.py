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

    # ---------------------------------------------------------
    # PHASE 1: SCRIPT ANALYSIS & RESUME LOGIC
    # ---------------------------------------------------------
    if os.path.isdir(input_path):
        project_folder = input_path
        state_path = os.path.join(project_folder, state_file)
        if os.path.exists(state_path):
            logger.info(f"Resuming project: {project_folder}")
            state = load_state(state_path)
            # Retrieve video_format from state, defaulting to "long form" if missing (for backwards compatibility)
            video_format = state.get("video_format", "long form")
        else:
            logger.error("No blueprint.json found in the provided folder.")
            return
    elif os.path.isfile(input_path):
        print("\n" + "="*60)
        print("PHASE 1: SCRIPT ANALYSIS WITH GEMINI")
        print("="*60)
        logger.info("\n--- PHASE 1: Script Analysis ---")
        with open(input_path, 'r', encoding='utf-8') as f:
            script_text = f.read()
            
        state = analyze_script(script_text)
        if not state:
            logger.error("Failed to analyze script.")
            return
            
        title = state.get("title", "Untitled Project")
        state["video_format"] = video_format
        project_folder = create_project_folder(title, OUTPUT_DIR, video_format)
        
        # Track if segments have been broken into sub-scenes yet
        state["segments_flattened"] = False
        state["subtitles_generated"] = False
        state["video_generated"] = False
        
        save_state(os.path.join(project_folder, state_file), state)
        logger.info(f"Project initialized at: {project_folder}")
    else:
        logger.error("Invalid input path.")
        return

    state_path = os.path.join(project_folder, state_file)

    # ---------------------------------------------------------
    # PHASE 2: PROMPT GENERATION (Multi-Image Breakdown)
    # ---------------------------------------------------------
    if not state.get("segments_flattened"):
        print("\n" + "="*60)
        print("PHASE 2: STORYBOARD & VISUAL PROMPT GENERATION")
        print("="*60)
        logger.info("\n--- PHASE 2: Generating Visual Prompts & Sub-Scenes ---")
        final_segments = []
        
        for i, chunk in enumerate(state["segments"]):
            logger.info(f"Breaking narrative chunk {i+1} into sub-scenes...")
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
                logger.error(f"Failed to generate sub-scenes for chunk {i+1}")
                return
        
        # Replace chunks with flattened scenes
        state["segments"] = final_segments
        state["segments_flattened"] = True
        
        # Initialize filenames for final segments
        for i, seg in enumerate(state["segments"]):
            safe_phase = slugify(seg.get("narrative_phase", "scene"))
            seg["image_filename"] = f"segment_{i+1:03d}_{safe_phase}.png"
            seg["audio_filename"] = f"audio_{i+1:03d}.mp3"
            
        save_state(state_path, state)
        logger.info(f"Total visual scenes determined: {len(state['segments'])}")

    # ---------------------------------------------------------
    # PHASE 3: AUDIO & SUBTITLES
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("PHASE 3: AUDIO & SUBTITLES GENERATION")
    print("="*60)
    logger.info("\n--- PHASE 3: Audio & Subtitles ---")
    full_audio_paths = []
    for i, segment in enumerate(state["segments"]):
        seg_audio_path = os.path.join(project_folder, segment["audio_filename"])
        full_audio_paths.append(seg_audio_path)
        
        if not segment.get("audio_generated"):
            if generate_audio(segment['text'], seg_audio_path):
                segment["audio_generated"] = True
                save_state(state_path, state)
            else:
                logger.error(f"Audio generation failed for segment {i+1}.")
                return

    # Combine master audio and make subtitles
    audio_path = os.path.join(project_folder, "audio.mp3")
    subtitle_path = os.path.join(project_folder, "subtitles.srt")
    
    if not state.get("subtitles_generated"):
        logger.info("Combining audio segments and generating subtitles...")
        concat_list_path = os.path.join(project_folder, "audio_list.txt")
        with open(concat_list_path, "w") as f:
            for p in full_audio_paths:
                f.write(f"file '{os.path.basename(p)}'\n")
        
        subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_list_path, "-c", "copy", "-y", audio_path], capture_output=True)
        
        if generate_subtitles(audio_path, subtitle_path, video_format=video_format):
            state["subtitles_generated"] = True
            save_state(state_path, state)
        else:
            logger.error("Subtitle generation failed.")
            return

    # ---------------------------------------------------------
    # PHASE 4: INTERACTIVE IMAGE GENERATION
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("PHASE 4: INTERACTIVE IMAGE GENERATION")
    print("="*60)
    logger.info("\n--- PHASE 4: Interactive Image Generation ---")
    
    # Check if there are any ungenerated images
    has_ungenerated = any(not seg.get("image_generated") for seg in state["segments"])
    manual_verify = True
    if has_ungenerated:
        manual_verify = input("\nDo you want to manually verify each image prompt? (yes/no): ").strip().lower() in ['yes', 'y']
    
    background_tasks = {}

    def check_background_tasks():
        """Checks for completed background tasks and processes their results."""
        completed_indices = []
        for idx, task in background_tasks.items():
            if not task["thread"].is_alive():
                completed_indices.append(idx)
                res_container = task["result"]
                segment = task["segment"]
                if res_container:
                    success, cost_usd = res_container[0]
                    if success:
                        segment["image_generated"] = True
                        segment["image_cost_usd"] = cost_usd
                        save_state(state_path, state)
                        cost_inr = cost_usd * USD_TO_INR_RATE
                        print(f"\n[BACKGROUND SUCCESS] Image generated for Segment {idx+1}: {segment['image_filename']} (Cost: ${cost_usd:.4f} / approx. ₹{cost_inr:.2f})")
                    else:
                        print(f"\n[BACKGROUND FAILED] Image generation failed for Segment {idx+1}.")
                else:
                    print(f"\n[BACKGROUND FAILED] Image generation failed or was aborted for Segment {idx+1}.")
        for idx in completed_indices:
            del background_tasks[idx]

    for i, segment in enumerate(state["segments"]):
        # Periodically check on any finished background tasks
        check_background_tasks()

        if segment.get("image_generated"):
            continue

        # Recovery check: If the image file already exists on disk, mark it as generated to prevent duplicate billing
        img_path = os.path.join(project_folder, segment["image_filename"])
        if os.path.exists(img_path) and not segment.get("image_generated"):
            segment["image_generated"] = True
            save_state(state_path, state)
            print(f"  [RECOVERY] Found Segment {i+1} image on disk ({segment['image_filename']}). Marking as generated to save API cost.")

        if segment.get("image_generated"):
            continue

        # If a background task is already running for this segment, skip and wait up to 5 min
        if i in background_tasks:
            if manual_verify:
                print(f"\n[WAIT] Background image generation for Segment {i+1} is currently running. Waiting up to 5 minutes...")
            else:
                print(f"\n[WAIT] Segment {i+1} image generation is currently running in the background. Waiting...")
            task = background_tasks[i]
            
            waited = 0
            timeout_limit = 300
            check_interval = 10
            while task["thread"].is_alive() and waited < timeout_limit:
                time.sleep(check_interval)
                waited += check_interval
                check_background_tasks()
                if waited % 60 == 0:
                    print(f"  [STATUS] Still waiting for Segment {i+1} image generation... ({waited // 60} min elapsed)")
                    active_tasks = [f"Segment {k+1}" for k in background_tasks if k != i]
                    if active_tasks:
                        print(f"  [STATUS] Other active background processes: {', '.join(active_tasks)}")

            if task["thread"].is_alive():
                print(f"  [STATUS] Still running in the background. Moving to the next segment...")
                continue
            else:
                check_background_tasks()
                if segment.get("image_generated"):
                    continue

        if manual_verify:
            print(f"\n" + "─"*60)
            print(f"SEGMENT {i+1} / {len(state['segments'])}  [{segment.get('narrative_phase', 'Unknown').upper()}]")
            print(f"─"*60)
            print(f" Dialogue: \"{segment['text']}\"")
            print(f" AI Suggested Prompt: {segment['image_prompt']}")
            print(f"─"*60)

            change = input("\nDo you want to change this prompt? (yes/no): ").strip().lower()
            if change in ['yes', 'y']:
                new_prompt = input("Enter your new custom prompt: ").strip()
                if new_prompt:
                    segment['image_prompt'] = new_prompt
                    save_state(state_path, state)
                    print("Prompt updated.")
        else:
            print(f"\n[GENERATING] Segment {i+1} / {len(state['segments'])}: Prompting Gemini...")

        img_path = os.path.join(project_folder, segment["image_filename"])
        aspect_ratio = "9:16" if video_format == "short form" else "16:9"
        
        result_container = []
        gen_thread = threading.Thread(
            target=generate_image,
            args=(segment['image_prompt'], img_path, result_container, False, aspect_ratio)  # verbose=False to keep background thread quiet
        )
        
        task_data = {
            "thread": gen_thread,
            "segment": segment,
            "result": result_container
        }
        
        gen_thread.start()
        
        # Wait up to 5 minutes with 1-minute status updates
        waited = 0
        timeout_limit = 300
        check_interval = 10
        while gen_thread.is_alive() and waited < timeout_limit:
            time.sleep(check_interval)
            waited += check_interval
            check_background_tasks()
            if waited % 60 == 0:
                print(f"  [STATUS] Still waiting for Segment {i+1} image generation... ({waited // 60} min elapsed)")
                active_tasks = [f"Segment {k+1}" for k in background_tasks]
                if active_tasks:
                    print(f"  [STATUS] Active background processes: {', '.join(active_tasks)}")
        
        if gen_thread.is_alive():
            # If it takes more than 5 minutes, move to the next image and keep it running in the background
            print(f"\n[BACKGROUNDED] Segment {i+1} is taking longer than 5 minutes. Backgrounding task and proceeding to the next segment...")
            background_tasks[i] = task_data
        else:
            # Check results of the wait
            if result_container:
                success, cost_usd = result_container[0]
                if success:
                    segment['image_generated'] = True
                    segment['image_cost_usd'] = cost_usd # Store cost
                    save_state(state_path, state)
                    cost_inr = cost_usd * USD_TO_INR_RATE
                    print(f"\n[SUCCESS] Image saved: {segment['image_filename']} (Cost: ${cost_usd:.4f} / approx. ₹{cost_inr:.2f})")
                    
                    if manual_verify:
                        proceed = input("Check the image in the project folder. Type 'next' to continue, or 'exit' to pause: ").strip().lower()
                        if proceed == 'exit':
                            if background_tasks:
                                print("\n[WARNING] Some background image tasks are still running. Exiting will abort their updates to the state, though the files will still save if they complete.")
                            print(f"Pipeline paused at segment {i+1}. Run option 2 later to resume.")
                            sys.exit(0)
                else:
                    print(f"Failed to generate image for Segment {i+1} on this attempt. You can retry it when resuming or running the script again.")
            else:
                print(f"Generation did not complete successfully for Segment {i+1}.")

    # ---------------------------------------------------------
    # PHASE 5: FINAL STITCHING VERIFICATION
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("PHASE 5: FINAL VIDEO STITCHING")
    print("="*60)
    logger.info("\n--- PHASE 5: Final Video Stitching ---")
    
    # 1. Sync any remaining background threads before we proceed
    if background_tasks:
        print(f"\n[SYNC] Waiting for {len(background_tasks)} outstanding background image generation tasks to complete...")
        waited = 0
        check_interval = 10
        while background_tasks:
            time.sleep(check_interval)
            waited += check_interval
            check_background_tasks()
            if waited % 60 == 0:
                active_tasks = [f"Segment {k+1}" for k in background_tasks]
                print(f"  [STATUS] Still waiting for background tasks: {', '.join(active_tasks)} ({waited // 60} min elapsed)")

    # 2. Safety check: verify if ALL images have been successfully generated
    missing_images = []
    for idx, seg in enumerate(state["segments"]):
        if not seg.get("image_generated"):
            missing_images.append(idx + 1)

    if missing_images:
        print(f"\n[ERROR] Video generation cannot proceed because some images are not generated:")
        for num in missing_images:
            print(f" - Segment {num}: \"{state['segments'][num-1]['text'][:60]}...\"")
        print("\nPlease run Option 2 to resume the project and regenerate/complete these missing images first.")
        return

    # Proceed with stitching if all images are ready
    if not state.get("video_generated"):
        final_check = input("\nAll segments are ready! Do you want to stitch the final video now? (yes/no): ").strip().lower()
        if final_check in ['yes', 'y']:
            add_audio = input("Include voiceover? (yes/no): ").strip().lower() in ['yes', 'y']
            add_captions = input("Include on-screen subtitles? (yes/no): ").strip().lower() in ['yes', 'y']
            
            output_video_path = os.path.join(project_folder, "final_video.mp4")
            if create_video(project_folder, state["segments"], audio_path, subtitle_path, output_video_path, include_audio=add_audio, include_captions=add_captions, video_format=video_format):
                state["video_generated"] = True
                save_state(state_path, state)
                print(f"\n[>>> PIPELINE COMPLETE! <<<]")
                print(f"Final Video: {output_video_path}\n")
            else:
                logger.error("Final stitching failed.")
        else:
            print(f"Paused before stitching. Use Option 2 to finish later.")
    else:
        logger.info("Video already exists for this project.")



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
