import os
import subprocess
from config import VIDEO_FPS, VIDEO_WIDTH, VIDEO_HEIGHT
from utils import setup_logger

logger = setup_logger("VideoStitcher")

def get_audio_duration(audio_path):
    """
    Get exact audio duration (seconds) via ffprobe.
    """
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        return duration
    except Exception as e:
        logger.error(f"❌ Audio duration extract failed: {str(e)[:60]}")
        return 0

def create_video(project_folder, segments, audio_path, subtitle_path, output_path, include_audio=True, include_captions=True, video_format="long form"):
    """
    Stitch images + audio + subtitles → MP4 via FFmpeg.
    Uses zoompan (z=1) to stretch each image to match audio duration.
    Supports 16:9 (long) and 9:16 (short) formats with cartoon-style subtitles.
    """
    logger.info(f"🎬 Stitching video ({video_format})...")

    # Verify audio exists
    total_duration = get_audio_duration(audio_path)
    if total_duration == 0:
        logger.error("❌ Audio duration is 0")
        return False

    # Collect image inputs for FFmpeg
    input_args = []
    image_paths = []

    for i, segment in enumerate(segments):
        expected = segment.get("image_filename", f"segment_{i:03d}.png")
        img_path = os.path.join(project_folder, expected)

        # Fallback: try .jpg if .png doesn't exist
        if not os.path.exists(img_path):
            img_path = os.path.join(project_folder, expected.replace(".png", ".jpg"))

        if os.path.exists(img_path):
            input_args.extend(["-i", img_path])
            image_paths.append(img_path)
        else:
            logger.error(f"❌ Missing image: {expected}")
            return False

    # Add audio input
    input_args.extend(["-i", audio_path])
    audio_idx = len(image_paths)

    # Set resolution based on format
    if video_format == "short form":
        width, height, scale_res = 1080, 1920, "2160:3840"  # 9:16
    else:
        width, height, scale_res = VIDEO_WIDTH, VIDEO_HEIGHT, "3840:2160"  # 16:9

    # Build FFmpeg filter graph
    filter_complex = []

    # Per-segment: scale image → zoompan (stretch to segment duration) → assign to [v{i}]
    for i, segment in enumerate(segments):
        seg_audio = os.path.join(project_folder, segment["audio_filename"])
        seg_dur = get_audio_duration(seg_audio)

        if seg_dur == 0:
            logger.warning(f"⚠️  Segment {i}: audio duration 0, using 3s fallback")
            seg_dur = 3.0

        # zoompan z=1 stretches static image without actual zoom
        # setpts=PTS-STARTPTS resets timestamp for concat
        num_frames = int(seg_dur * VIDEO_FPS)
        filter_str = (
            f"scale={scale_res},"
            f"zoompan=z=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={num_frames}:s={width}x{height}:fps={VIDEO_FPS},"
            f"setsar=1/1,setpts=PTS-STARTPTS"
        )
        filter_complex.append(f"[{i}:v]{filter_str}[v{i}];")

    # Concatenate all video segments
    concat_inputs = "".join([f"[v{i}]" for i in range(len(image_paths))])
    filter_complex.append(f"{concat_inputs}concat=n={len(image_paths)}:v=1:a=0[v_concat];")

    # Add subtitles (if requested)
    if include_captions:
        sub_path_esc = subtitle_path.replace("\\", "/").replace(":", "\\:")

        if video_format == "short form":
            # Short-form: huge font (52pt), yellow, center-middle (MarginV=850)
            style = (
                "force_style='FontName=Comic Sans MS,FontSize=52,PrimaryColour=&H0000FFFF&,"
                "OutlineColour=&H00000000&,BorderStyle=1,Outline=4,Shadow=1,Alignment=2,MarginV=850'"
            )
        else:
            # Long-form: medium font (28pt), white, bottom (MarginV=70)
            style = (
                "force_style='FontName=Comic Sans MS,FontSize=28,PrimaryColour=&H00FFFFFF&,"
                "OutlineColour=&H00000000&,BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=70'"
            )
        filter_complex.append(f"[v_concat]subtitles='{sub_path_esc}':{style}[v_final];")
        video_map = "[v_final]"
    else:
        video_map = "[v_concat]"

    # Configure audio (if requested)
    audio_args = (
        ["-map", f"{audio_idx}:a", "-c:a", "aac", "-b:a", "192k"]
        if include_audio
        else ["-an"]
    )

    # Build FFmpeg command
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        *input_args,
        "-filter_complex", "".join(filter_complex),
        "-map", video_map,
        *audio_args,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-y", output_path
    ]

    logger.info(f"🎥 FFmpeg encoding → {output_path}")
    try:
        subprocess.run(cmd, check=True)
        logger.info(f"✓ Video created: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FFmpeg error: {str(e)[:100]}")
        return False
