import base64
import time
import os
from google import genai
from google.genai import types
from config import IMAGE_API_KEY, MASTER_STYLE_PROMPT, IMAGE_COST_PER_1M_TOKENS_USD, IMAGE_TOKENS_PER_IMAGE_1K, IMAGE_MODEL
from utils import setup_logger

logger = setup_logger("ImageGenerator")

# Initialize the client
client = genai.Client(api_key=IMAGE_API_KEY)



def generate_image(scene_description, output_path, result_container=None, verbose=True):
    """
    Generates a 16:9 image using the gemini-3.1-flash-image model.
    Applies the Master Style Prompt to ensure consistent 2D cartoon visuals.
    Saves the raw bytes returned by the API directly to a file.
    Calculates and returns the estimated USD cost of the image.
    If result_container (list) is provided, appends (success_status, cost_usd) to it.
    Returns (success_status: bool, cost_usd: float).
    """
    full_prompt = MASTER_STYLE_PROMPT.format(scene_description=scene_description)

    logger.info(f"Requesting image generation with model {IMAGE_MODEL} for scene:\n'{scene_description}'")

    max_retries = 4
    base_delay = 5  # start with a 5 second delay

    for attempt in range(1, max_retries + 1):
        if verbose:
            print(f"  [API CALL] Image Generation Attempt {attempt}/{max_retries} for: \"{scene_description[:50]}...\"")
        logger.info(f"Image generation attempt {attempt}/{max_retries} for scene: {scene_description}")
        
        # Respect API rate limits
        time.sleep(2) 

        try:
            # Call the new generate_content API for images
            response = client.models.generate_content(
                model=IMAGE_MODEL,
                contents=[full_prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(
                        image_size="1K", # Explicitly set to 1K for cost consistency
                        aspect_ratio="16:9" # Explicitly set for video format
                    )
                ),
            )

            # Extract the image data
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if part.inline_data:
                        img_data = part.inline_data.data
                        tmp_path = output_path + ".tmp"
                        with open(tmp_path, "wb") as f:
                            f.write(img_data)
                        if os.path.exists(output_path):
                            os.remove(output_path)
                        os.rename(tmp_path, output_path)
                        
                        # Calculate cost upon successful image data retrieval
                        tokens_consumed = IMAGE_TOKENS_PER_IMAGE_1K
                        cost_usd = (tokens_consumed / 1_000_000) * IMAGE_COST_PER_1M_TOKENS_USD
                        
                        logger.info(f"Image successfully saved to: {output_path} (Estimated Cost: ${cost_usd:.4f})")
                        if result_container is not None:
                            result_container.append((True, cost_usd))
                        return True, cost_usd

            logger.warning("API call succeeded, but no image data was found in response payload.")
            if verbose:
                print("  [WARNING] Response received, but no image payload was present in candidates.")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during image generation (Attempt {attempt}/{max_retries}): {error_msg}")
            
            # Print a clear error message to the console
            if verbose:
                print(f"  [ERROR] Attempt {attempt} failed: {error_msg}")
            
            if attempt < max_retries:
                # Exponential backoff: 5s, 10s, 20s, 40s
                sleep_time = base_delay * (2 ** (attempt - 1))
                if verbose:
                    print(f"  [RETRY] Connection reset, timeout, or API error. Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                if verbose:
                    print(f"  [CRITICAL] All {max_retries} attempts failed to generate this image.")
                
    if result_container is not None:
        result_container.append((False, 0.0))
    return False, 0.0



