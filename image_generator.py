import base64
import time
import os
import requests
from google import genai
from google.genai import types
from config import IMAGE_API_KEY, MASTER_STYLE_PROMPT, IMAGE_COST_PER_1M_TOKENS_USD, IMAGE_TOKENS_PER_IMAGE_1K, IMAGE_MODEL, FAL_MODEL, USD_TO_INR_RATE
from utils import setup_logger

logger = setup_logger("ImageGenerator")

# Initialize the Gemini client
client = genai.Client(api_key=IMAGE_API_KEY)

try:
    import fal_client
except ImportError:
    fal_client = None


def generate_image(scene_description, output_path, result_container=None, verbose=True, aspect_ratio="16:9", provider="gemini"):
    """
    Generates image via Gemini or Fal.ai with retry & cost tracking.
    - Applies Master Style Prompt for consistent 2D cartoon look
    - Atomic write: .tmp → rename (prevents corruption)
    - Returns (success: bool, cost_usd: float)
    - Appends to result_container if provided (for threading)
    """
    full_prompt = MASTER_STYLE_PROMPT.format(scene_description=scene_description)
    provider_name = provider.lower().strip() if provider else "gemini"

    if provider_name == "fal":
        if fal_client is None:
            logger.error("fal-client library is not installed. Cannot use Fal.ai provider.")
            if result_container is not None:
                result_container.append((False, 0.0))
            return False, 0.0

        fal_key = os.getenv("FAL_KEY")
        if not fal_key:
            logger.error("FAL_KEY environment variable not set. Cannot use Fal.ai provider.")
            if result_container is not None:
                result_container.append((False, 0.0))
            return False, 0.0
            
        os.environ["FAL_KEY"] = fal_key

        model_name = FAL_MODEL
        logger.info(f"Requesting image generation via Fal.ai using model {model_name} and aspect ratio {aspect_ratio}...")
        
        # Determine cost per megapixel / flat cost
        if "flux/dev" in model_name:
            cost_per_mp = 0.025
            is_flux = True
        elif "flux/schnell" in model_name:
            cost_per_mp = 0.003
            is_flux = True
        else:
            cost_per_mp = 0.003  # default fallback for nano-banana
            is_flux = False

        # Build dynamic arguments based on model type
        api_args = {
            "prompt": full_prompt
        }
        if is_flux:
            # Flux expects image_size as landscape_16_9 or portrait_16_9
            api_args["image_size"] = "portrait_16_9" if aspect_ratio == "9:16" else "landscape_16_9"
            api_args["num_inference_steps"] = 28 if "dev" in model_name else 4
            api_args["enable_safety_checker"] = True
        else:
            # Nano-banana and standard Imagen models expect aspect_ratio as 16:9 or 9:16
            api_args["aspect_ratio"] = aspect_ratio

        max_retries = 3

        for attempt in range(1, max_retries + 1):
            if verbose:
                print(f"  [Fal.ai] Attempt {attempt}/{max_retries}: {scene_description[:40]}...")

            try:
                result = fal_client.subscribe(model_name, arguments=api_args)

                # Extract image from response
                if "images" in result and len(result["images"]) > 0:
                    image_info = result["images"][0]
                    image_url = image_info["url"]
                    width = image_info.get("width")
                    height = image_info.get("height")

                    # Atomic write: download → .tmp → rename (prevents partial saves)
                    img_data = requests.get(image_url).content
                    tmp_path = output_path + ".tmp"
                    with open(tmp_path, "wb") as f:
                        f.write(img_data)

                    if os.path.exists(output_path):
                        os.remove(output_path)
                    os.rename(tmp_path, output_path)

                    # Calculate megapixel-based cost
                    megapixels = (width * height) / 1_000_000 if width and height else 0.58
                    cost_usd = megapixels * cost_per_mp

                    logger.info(f"✓ Fal.ai image: {output_path} | ${cost_usd:.4f}")
                    if result_container is not None:
                        result_container.append((True, cost_usd))
                    return True, cost_usd

                logger.warning("⚠ Fal.ai: No image in response")

            except Exception as e:
                wait = 2 * attempt  # 2s, 4s, 6s backoff
                if attempt < max_retries:
                    logger.warning(f"⚠ Fal.ai attempt {attempt} failed. Retry in {wait}s...")
                    if verbose:
                        print(f"  [Retry] Waiting {wait}s...")
                    time.sleep(wait)
                else:
                    logger.error(f"✗ Fal.ai: All {max_retries} attempts failed")
                        
        if result_container is not None:
            result_container.append((False, 0.0))
        return False, 0.0

    else:
        # Gemini image generation (3.1-flash-image model)
        logger.info(f"🖼️  Gemini {aspect_ratio} generation: {scene_description[:60]}...")

        max_retries = 3

        for attempt in range(1, max_retries + 1):
            if verbose:
                print(f"  [Gemini] Attempt {attempt}/{max_retries}: {scene_description[:40]}...")

            # Minimal rate limit respect: 0.5s between retries only
            if attempt > 1:
                time.sleep(0.5)

            try:
                response = client.models.generate_content(
                    model=IMAGE_MODEL,
                    contents=[full_prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        image_config=types.ImageConfig(
                            image_size="1K",  # Fixed for cost predictability
                            aspect_ratio=aspect_ratio
                        )
                    ),
                )

                # Extract image from response
                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        if part.inline_data:
                            # Atomic write: write to .tmp, then rename
                            img_data = part.inline_data.data
                            tmp_path = output_path + ".tmp"
                            with open(tmp_path, "wb") as f:
                                f.write(img_data)
                            if os.path.exists(output_path):
                                os.remove(output_path)
                            os.rename(tmp_path, output_path)

                            # Calculate token-based cost
                            tokens_consumed = IMAGE_TOKENS_PER_IMAGE_1K
                            cost_usd = (tokens_consumed / 1_000_000) * IMAGE_COST_PER_1M_TOKENS_USD

                            logger.info(f"✓ Gemini image: {output_path} | ${cost_usd:.4f}")
                            if result_container is not None:
                                result_container.append((True, cost_usd))
                            return True, cost_usd

                logger.warning("⚠ Gemini: No image in response")

            except Exception as e:
                wait = 2 * attempt  # 2s, 4s, 6s backoff
                if attempt < max_retries:
                    logger.warning(f"⚠ Gemini attempt {attempt} failed. Retry in {wait}s...")
                    if verbose:
                        print(f"  [Retry] Waiting {wait}s...")
                    time.sleep(wait)
                else:
                    logger.error(f"✗ Gemini: All {max_retries} attempts failed")
                    
        if result_container is not None:
            result_container.append((False, 0.0))
        return False, 0.0
