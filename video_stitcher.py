import os
import subprocess
from config import (
    VIDEO_FPS, VIDEO_WIDTH, VIDEO_HEIGHT,
    VIDEO_PRESET, VIDEO_CRF, KEN_BURNS_ZOOM, TRANSITION_DURATION,
)
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

def _ken_burns(index, num_frames):
    """
    Motion expression for one shot. Direction alternates between shots so the
    video breathes instead of drifting the same way for 8 minutes.
    """
    z_in = f"1+{KEN_BURNS_ZOOM}*on/{num_frames}"
    z_out = f"{1 + KEN_BURNS_ZOOM}-{KEN_BURNS_ZOOM}*on/{num_frames}"
    center_x, center_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"

    patterns = [
        (z_in, center_x, center_y),                                    # push in
        (z_out, center_x, center_y),                                   # pull out
        (z_in, f"(iw-iw/zoom)*on/{num_frames}", center_y),             # push in, drift right
        (z_out, f"(iw-iw/zoom)*(1-on/{num_frames})", center_y),        # pull out, drift left
    ]
    return patterns[index % len(patterns)]


def create_video(project_folder, segments, audio_path, subtitle_path, output_path, include_audio=True, include_captions=True, video_format="long form"):
    """
    Stitch images + audio + subtitles → MP4 via FFmpeg.
    Each image gets slow Ken Burns motion, shots are crossfaded together.
    Supports 16:9 (long) and 9:16 (short) formats.
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

    # Measure every segment first so transition length can be made safe
    seg_durations = []
    for i, segment in enumerate(segments):
        seg_audio = os.path.join(project_folder, segment["audio_filename"])
        seg_dur = get_audio_duration(seg_audio)
        if seg_dur == 0:
            logger.warning(f"⚠️  Segment {i}: audio duration 0, using 3s fallback")
            seg_dur = 3.0
        seg_durations.append(seg_dur)

    # A crossfade eats time from both shots, so it must stay short relative to
    # the shortest one. Each shot after the first is padded by exactly the
    # transition length, so the final video still matches the master audio.
    if len(seg_durations) > 1:
        transition = min(TRANSITION_DURATION, min(seg_durations) * 0.3)
    else:
        transition = 0.0

    filter_complex = []

    for i, seg_dur in enumerate(seg_durations):
        padded_dur = seg_dur + (transition if i > 0 else 0.0)
        num_frames = max(int(padded_dur * VIDEO_FPS), 1)
        z_expr, x_expr, y_expr = _ken_burns(i, num_frames)

        filter_str = (
            f"scale={scale_res},"
            f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':"
            f"d={num_frames}:s={width}x{height}:fps={VIDEO_FPS},"
            f"setsar=1/1,setpts=PTS-STARTPTS"
        )
        filter_complex.append(f"[{i}:v]{filter_str}[v{i}];")

    # Chain the shots together with crossfades
    if transition > 0:
        running = seg_durations[0]
        current = "[v0]"
        for i in range(1, len(seg_durations)):
            offset = running - transition
            label = "[v_concat]" if i == len(seg_durations) - 1 else f"[x{i}]"
            filter_complex.append(
                f"{current}[v{i}]xfade=transition=fade:"
                f"duration={transition:.3f}:offset={offset:.3f}{label};"
            )
            current = label
            running = running + (seg_durations[i] + transition) - transition
    else:
        filter_complex.append(f"[v0]copy[v_concat];")

    # Add subtitles (if requested)
    if include_captions:
        sub_path_esc = subtitle_path.replace("\\", "/").replace(":", "\\:")

        if video_format == "short form":
            # Short-form: large, amber, parked above the UI chrome
            style = (
                "force_style='FontName=Arial Black,FontSize=54,Bold=1,PrimaryColour=&H0023A6F5&,"
                "OutlineColour=&H00101010&,BorderStyle=1,Outline=5,Shadow=0,Alignment=2,MarginV=780'"
            )
        else:
            # Long-form: clean white, sits in the calm lower fifth of the frame
            style = (
                "force_style='FontName=Arial Black,FontSize=30,Bold=1,PrimaryColour=&H00F7F3E9&,"
                "OutlineColour=&H00101010&,BorderStyle=1,Outline=4,Shadow=0,Alignment=2,MarginV=85'"
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
        "-c:v", "libx264", "-preset", VIDEO_PRESET, "-crf", str(VIDEO_CRF),
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-y", output_path
    ]

    logger.info(f"🎥 FFmpeg encoding → {output_path}")
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"✓ Video created: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FFmpeg failed: {(e.stderr or '').strip()[-600:]}")
        return False
