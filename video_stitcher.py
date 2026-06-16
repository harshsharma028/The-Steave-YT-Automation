import os
import subprocess
from config import VIDEO_FPS, VIDEO_WIDTH, VIDEO_HEIGHT
from utils import setup_logger

logger = setup_logger("VideoStitcher")

def get_audio_duration(audio_path):
    """
    Uses ffprobe to extract the exact duration of an audio file in seconds.
    """
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except Exception as e:
        logger.error(f"Failed to extract audio duration for {audio_path}: {e}")
        return 0

def create_video(project_folder, segments, audio_path, subtitle_path, output_path, include_audio=True, include_captions=True):
    """
    Stitches static images, full audio, and styled subtitles into a final video.
    Uses a complex FFmpeg filter graph to align everything perfectly.
    """
    logger.info("Initializing Video Stitching Process...")
    
    total_audio_duration = get_audio_duration(audio_path)
    if total_audio_duration == 0:
        logger.error("Total audio duration is 0. Cannot stitch video.")
        return False

    input_args = []
    image_paths = []
    
    # 1. Collect Image Inputs
    for i, segment in enumerate(segments):
        expected_filename = segment.get("image_filename", f"segment_{i:03d}.png")
        img_path = os.path.join(project_folder, expected_filename)
        
        # Fallback to jpg if png is missing
        if not os.path.exists(img_path):
             img_path = os.path.join(project_folder, expected_filename.replace(".png", ".jpg"))
             
        if os.path.exists(img_path):
            input_args.extend(["-i", img_path])
            image_paths.append(img_path)
        else:
            logger.error(f"Missing image file for segment {i}: {img_path}")
            return False

    # 2. Add Audio Input
    input_args.extend(["-i", audio_path])
    audio_idx = len(image_paths)

    filter_complex = []
    
    for i, segment in enumerate(segments):
        # Get the actual duration of THIS segment's audio file
        seg_audio_file = os.path.join(project_folder, segment["audio_filename"])
        seg_dur = get_audio_duration(seg_audio_file)
        
        if seg_dur == 0:
            logger.warning(f"Audio duration for {seg_audio_file} is 0. Using fallback duration.")
            seg_dur = 3.0 # safe fallback
        
        # We use zoompan with z=1 to turn a single image into a video stream of the correct length, without actually zooming.
        # setsar=1/1 forces a square pixel ratio to prevent concatenation errors.
        num_frames = int(seg_dur * VIDEO_FPS)
        static_filter = (
            f"scale=3840:2160,zoompan=z=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={num_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={VIDEO_FPS},setsar=1/1,setpts=PTS-STARTPTS"
        )
        
        filter_complex.append(f"[{i}:v]{static_filter}[v{i}];")

    # 4. Concatenate Video Streams
    concat_input = "".join([f"[v{i}]" for i in range(len(image_paths))])
    filter_complex.append(f"{concat_input}concat=n={len(image_paths)}:v=1:a=0[v_concat];")

    # 5. Overlay Subtitles with Cartoon Styling (Conditional)
    if include_captions:
        # Escape path characters for FFmpeg filter syntax
        sub_path_esc = subtitle_path.replace("\\", "/").replace(":", "\\:")
        
        # Comic Sans MS, big font, thick black outline, positioned nicely near bottom (MarginV=70)
        style = (
            "force_style='FontName=Comic Sans MS,FontSize=28,PrimaryColour=&H00FFFFFF&,"
            "OutlineColour=&H00000000&,BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=70'"
        )
        filter_complex.append(f"[v_concat]subtitles='{sub_path_esc}':{style}[v_final];")
        video_map = "[v_final]"
    else:
        video_map = "[v_concat]"

    # 6. Audio Mapping (Conditional)
    if include_audio:
        audio_map_args = ["-map", f"{audio_idx}:a", "-c:a", "aac", "-b:a", "192k"]
    else:
        audio_map_args = ["-an"]

    # 7. Build Final Command
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        *input_args,
        "-filter_complex", "".join(filter_complex),
        "-map", video_map,
        *audio_map_args,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-y", output_path
    ]

    logger.info(f"Executing FFmpeg... Saving to: {output_path}")
    try:
        subprocess.run(cmd, check=True)
        logger.info("FFmpeg processing completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg encountered a critical error: {e}")
        return False
