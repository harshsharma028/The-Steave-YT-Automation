"""
Thumbnail generation.

Produces one image per video, sized and compressed to YouTube's spec. The
composition brief comes from the active channel profile, so a thumbnail always
matches the channel it belongs to.

No text is drawn into the image. Image models render lettering as misspelled
gibberish, and YouTube shows the title beside the thumbnail anyway — a clean
symbolic image reads better at 120px than words competing with words.
"""

import os

from PIL import Image

from config import ACTIVE_CHANNEL
from image_generator import generate_image
from utils import setup_logger

logger = setup_logger("Thumbnail")

# YouTube: 1280x720 recommended, 2MB limit, 16:9.
THUMB_WIDTH, THUMB_HEIGHT = 1280, 720
MAX_BYTES = 2 * 1024 * 1024


def _fit_to_spec(source_path, output_path):
    """
    Crop to 16:9, resize to 1280x720, and compress until under 2MB.
    """
    with Image.open(source_path) as img:
        img = img.convert("RGB")

        # Centre-crop to exactly 16:9 before resizing so nothing is squashed.
        target_ratio = THUMB_WIDTH / THUMB_HEIGHT
        width, height = img.size
        if width / height > target_ratio:
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            img = img.crop((left, 0, left + new_width, height))
        else:
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            img = img.crop((0, top, width, top + new_height))

        img = img.resize((THUMB_WIDTH, THUMB_HEIGHT), Image.LANCZOS)

        for quality in (92, 85, 78, 70, 60):
            img.save(output_path, "JPEG", quality=quality, optimize=True)
            if os.path.getsize(output_path) <= MAX_BYTES:
                return os.path.getsize(output_path), quality

    return os.path.getsize(output_path), 60


def generate_thumbnail(title, project_folder, provider=None):
    """
    Generate a thumbnail for a video and write thumbnail.jpg into the project.

    Returns the output path, or None if generation failed.
    """
    logger.info("🖼️  Generating thumbnail...")

    scene = (
        f"{ACTIVE_CHANNEL.thumbnail_brief}\n\n"
        f"The subject of this video is: {title}\n"
        "Compose it as a single still image with nothing written anywhere in it."
    )

    raw_path = os.path.join(project_folder, "thumbnail_raw.png")
    success, cost = generate_image(
        scene, raw_path, None, False, "16:9", provider
    )

    if not success:
        logger.error("✗ Thumbnail generation failed")
        return None

    output_path = os.path.join(project_folder, "thumbnail.jpg")
    size, quality = _fit_to_spec(raw_path, output_path)

    try:
        os.remove(raw_path)
    except OSError:
        pass

    logger.info(
        f"✓ Thumbnail: {THUMB_WIDTH}x{THUMB_HEIGHT}, "
        f"{size / 1024:.0f}KB (q{quality}) | ${cost:.4f}"
    )
    return output_path
