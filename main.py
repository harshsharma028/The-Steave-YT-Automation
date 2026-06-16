import os
import sys
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
from config import OUTPUT_DIR

logger = setup_logger("MainPipeline")

def save_state(filepath, state_data):
    """Saves the current pipeline state to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(state_data, f, indent=4)

def load_state(filepath):
    """Loads pipeline state from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def run_interactive_pipeline(input_path):
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
        else:
            logger.error("No blueprint.json found in the provided folder.")
            return
    elif os.path.isfile(input_path):
        logger.info("\n--- PHASE 1: Script Analysis ---")
        with open(input_path, 'r', encoding='utf-8') as f:
            script_text = f.read()
            
        state = analyze_script(script_text)
        if not state:
            logger.error("Failed to analyze script.")
            return
            
        title = state.get("title", "Untitled Project")
        project_folder = create_project_folder(title, OUTPUT_DIR)
        
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
        
        if generate_subtitles(audio_path, subtitle_path):
            state["subtitles_generated"] = True
            save_state(state_path, state)
        else:
            logger.error("Subtitle generation failed.")
            return

    # ---------------------------------------------------------
    # PHASE 4: INTERACTIVE IMAGE GENERATION
    # ---------------------------------------------------------
    logger.info("\n--- PHASE 4: Interactive Image Generation ---")
    for i, segment in enumerate(state["segments"]):
        if segment.get("image_generated"):
            continue

        print(f"\n======================================")
        print(f"Segment {i+1} / {len(state['segments'])}")
        print(f"Narrative Phase: {segment.get('narrative_phase', 'Unknown')}")
        print(f"Dialogue: \"{segment['text']}\"")
        print(f"--------------------------------------")
        print(f"AI Suggested Prompt: {segment['image_prompt']}")
        print(f"======================================")

        change = input("\nDo you want to change this prompt? (yes/no): ").strip().lower()
        if change in ['yes', 'y']:
            new_prompt = input("Enter your new custom prompt: ").strip()
            if new_prompt:
                segment['image_prompt'] = new_prompt
                save_state(state_path, state)
                print("Prompt updated.")
        
        print("\nGenerating image... Please wait.")
        img_path = os.path.join(project_folder, segment["image_filename"])
        success, cost_usd = generate_image(segment['image_prompt'], img_path)
        if success:
            segment['image_generated'] = True
            segment['image_cost_usd'] = cost_usd # Store cost
            save_state(state_path, state)

            print(f"\n[SUCCESS] Image saved: {segment['image_filename']} (Estimated Cost: ${cost_usd:.4f})")
            proceed = input("Check the image in the project folder. Type 'next' to continue, or 'exit' to pause: ").strip().lower()
            if proceed == 'exit':
                print(f"Pipeline paused at segment {i+1}. Run option 2 later to resume.")
                sys.exit(0)
        else:
            print("Failed to generate image. Please restart the pipeline to retry.")
            sys.exit(1)

    # ---------------------------------------------------------
    # PHASE 5: FINAL STITCHING VERIFICATION
    # ---------------------------------------------------------
    logger.info("\n--- PHASE 5: Final Video Stitching ---")
    if not state.get("video_generated"):
        final_check = input("\nAll segments are ready! Do you want to stitch the final video now? (yes/no): ").strip().lower()
        if final_check in ['yes', 'y']:
            add_audio = input("Include voiceover? (yes/no): ").strip().lower() in ['yes', 'y']
            add_captions = input("Include on-screen subtitles? (yes/no): ").strip().lower() in ['yes', 'y']
            
            output_video_path = os.path.join(project_folder, "final_video.mp4")
            if create_video(project_folder, state["segments"], audio_path, subtitle_path, output_video_path, include_audio=add_audio, include_captions=add_captions):
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
            run_interactive_pipeline(tmp_path)
            if os.path.exists(tmp_path): os.remove(tmp_path)
    elif choice == '2':
        folder = input("\nEnter project folder path: ").strip()
        if os.path.isdir(folder): run_interactive_pipeline(folder)
    else:
        print("Invalid choice.")
