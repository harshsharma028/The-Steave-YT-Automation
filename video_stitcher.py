import os
import shutil
import subprocess
from config import (
    VIDEO_FPS, VIDEO_WIDTH, VIDEO_HEIGHT,
    VIDEO_PRESET, VIDEO_CRF, KEN_BURNS_ZOOM, TRANSITION_DURATION, EDGE_TRIM,
    MUSIC_DIR, MUSIC_VOLUME, MUSIC_FADE,
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

def get_image_size(path):
    """
    Return (width, height) for an image, or None if it cannot be read.
    """
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=s=x:p=0', path
        ]
        out = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
        w, h = out.split('x')
        return int(w), int(h)
    except Exception:
        return None


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


def list_music_beds():
    """
    Return the available music beds, sorted. Empty list when there are none.

    Beds differ in tone — driving, playful, eerie — so the caller picks one to
    match the video. Choosing at random would eventually score a grim fact with
    comedy music.
    """
    if not os.path.isdir(MUSIC_DIR):
        return []
    return sorted(
        os.path.join(MUSIC_DIR, f) for f in os.listdir(MUSIC_DIR)
        if f.lower().endswith((".wav", ".mp3", ".m4a", ".ogg"))
    )


def _render_shot(image_path, out_path, duration, index, width, height,
                 scale_res, trim, video_format):
    """
    Render one still into a short clip with Ken Burns motion.
    """
    num_frames = max(int(duration * VIDEO_FPS), 1)
    z_expr, x_expr, y_expr = _ken_burns(index, num_frames)
    motion = (
        f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':"
        f"d={num_frames}:s={width}x{height}:fps={VIDEO_FPS},setsar=1/1"
    )

    size = get_image_size(image_path)
    source_is_landscape = bool(size) and size[0] > size[1] * 1.2

    if video_format == "short form" and source_is_landscape:
        # Landscape art reused in a vertical video. Cropping to 9:16 would cut
        # the subject out of frame and stretching would distort it, so the whole
        # picture sits over a blurred enlargement of itself. Art generated at
        # 9:16 skips this and fills the frame.
        work_w, work_h = width * 3 // 2, height * 3 // 2
        graph = (
            f"[0:v]split=2[a][b];"
            f"[a]scale={work_w}:{work_h}:force_original_aspect_ratio=increase,"
            f"crop={work_w}:{work_h},boxblur=30:2,eq=brightness=-0.18[bg];"
            f"[b]{trim},scale={work_w}:-2[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1/1[c];"
            f"[c]{motion}[out]"
        )
    else:
        # Scale to cover rather than to fixed dimensions, so an image whose
        # aspect differs slightly from the target is cropped, never squashed.
        graph = (
            f"[0:v]scale={scale_res}:force_original_aspect_ratio=increase,"
            f"crop={scale_res},{trim},{motion}[out]"
        )

    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", image_path,
        "-filter_complex", graph,
        "-map", "[out]", "-frames:v", str(num_frames),
        # Intermediate only; crf 16 keeps generation loss invisible in the join.
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
        "-pix_fmt", "yuv420p", "-an", "-y", out_path,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Shot render failed: {(e.stderr or '').strip()[-400:]}")
        return False


def create_video(project_folder, segments, audio_path, subtitle_path, output_path, include_audio=True, include_captions=True, video_format="long form", music_path=None):
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

    # Collect source images
    image_paths = []
    for i, segment in enumerate(segments):
        expected = segment.get("image_filename", f"segment_{i:03d}.png")
        img_path = os.path.join(project_folder, expected)
        if not os.path.exists(img_path):
            img_path = os.path.join(project_folder, expected.replace(".png", ".jpg"))
        if not os.path.exists(img_path):
            logger.error(f"❌ Missing image: {expected}")
            return False
        image_paths.append(img_path)

    # Working resolution for the motion pass. 1.33x the output is ample
    # headroom for a 1.12x zoom without wasting memory on 4K buffers.
    if video_format == "short form":
        width, height, scale_res = 1080, 1920, "1440:2560"  # 9:16
    else:
        width, height, scale_res = VIDEO_WIDTH, VIDEO_HEIGHT, "2560:1440"  # 16:9

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

    trim = f"crop=iw*{1 - 2 * EDGE_TRIM}:ih*{1 - 2 * EDGE_TRIM}"

    # PASS 1 — render each shot on its own.
    # Rendering all shots in a single filter graph keeps every image decoded and
    # every crossfade buffered at once, which exhausted memory on a three-minute
    # video. One shot at a time keeps peak memory flat regardless of length.
    shots_dir = os.path.join(project_folder, "_shots")
    os.makedirs(shots_dir, exist_ok=True)
    shot_paths = []

    for i, seg_dur in enumerate(seg_durations):
        padded_dur = seg_dur + (transition if i > 0 else 0.0)
        shot_path = os.path.join(shots_dir, f"shot_{i:03d}.mp4")

        # Reuse a shot already rendered, so an interrupted stitch can resume.
        if not os.path.exists(shot_path):
            if not _render_shot(image_paths[i], shot_path, padded_dur, i,
                                width, height, scale_res, trim, video_format):
                logger.error(f"❌ Failed rendering shot {i + 1}")
                return False
            logger.info(f"  shot {i + 1}/{len(seg_durations)}")
        shot_paths.append(shot_path)

    # PASS 2 — join the shots, lay in audio and burn subtitles.
    input_args = []
    for path in shot_paths:
        input_args.extend(["-i", path])
    input_args.extend(["-i", audio_path])
    audio_idx = len(shot_paths)

    # Loop the bed so a short track still covers a long narration; ffmpeg cuts
    # it to length via the amix `duration=first` below.
    music_idx = None
    if include_audio and music_path and os.path.exists(music_path):
        input_args.extend(["-stream_loop", "-1", "-i", music_path])
        music_idx = audio_idx + 1

    filter_complex = []
    if transition > 0 and len(shot_paths) > 1:
        running = seg_durations[0]
        current = "[0:v]"
        for i in range(1, len(shot_paths)):
            offset = running - transition
            label = "[v_concat]" if i == len(shot_paths) - 1 else f"[x{i}]"
            filter_complex.append(
                f"{current}[{i}:v]xfade=transition=fade:"
                f"duration={transition:.3f}:offset={offset:.3f}{label};"
            )
            current = label
            running = running + (seg_durations[i] + transition) - transition
    else:
        filter_complex.append("[0:v]copy[v_concat];")

    if include_captions:
        sub_path_esc = subtitle_path.replace("\\", "/").replace(":", "\\:")

        # Sizes and margins here are in ASS script units, which libass scales by
        # video_height/PlayResY (PlayResY defaults to 288 for SRT input). They
        # are therefore much smaller than the pixel values they produce, and are
        # not interchangeable between the two formats.
        if video_format == "short form":
            style = (
                "force_style='FontName=Arial Black,FontSize=13,Bold=1,PrimaryColour=&H0023A6F5&,"
                "OutlineColour=&H00101010&,BorderStyle=1,Outline=5,Shadow=0,Alignment=2,MarginV=95'"
            )
        else:
            style = (
                "force_style='FontName=Arial Black,FontSize=18,Bold=1,PrimaryColour=&H00F7F3E9&,"
                "OutlineColour=&H00101010&,BorderStyle=1,Outline=4,Shadow=0,Alignment=2,MarginV=22'"
            )
        filter_complex.append(f"[v_concat]subtitles='{sub_path_esc}':{style}[v_final];")
        video_map = "[v_final]"
    else:
        video_map = "[v_concat]"

    if not include_audio:
        audio_args = ["-an"]
    elif music_idx is not None:
        total = get_audio_duration(audio_path)
        # Narration at full level, bed well under it and faded at both ends.
        filter_complex.append(
            f"[{music_idx}:a]volume={MUSIC_VOLUME},"
            f"afade=t=in:st=0:d={MUSIC_FADE},"
            f"afade=t=out:st={max(total - MUSIC_FADE, 0):.2f}:d={MUSIC_FADE}[bed];"
            # normalize=0 is essential: amix otherwise divides every input by the
            # input count, so adding a bed would quietly drop the narration 6dB.
            f"[{audio_idx}:a][bed]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a_mix];"
        )
        audio_args = ["-map", "[a_mix]", "-c:a", "aac", "-b:a", "192k"]
        logger.info(f"🎵 Music bed: {os.path.basename(music_path)} at {int(MUSIC_VOLUME * 100)}%")
    else:
        audio_args = ["-map", f"{audio_idx}:a", "-c:a", "aac", "-b:a", "192k"]

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
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FFmpeg failed: {(e.stderr or '').strip()[-600:]}")
        return False

    shutil.rmtree(shots_dir, ignore_errors=True)
    logger.info(f"✓ Video created: {output_path}")
    return True
