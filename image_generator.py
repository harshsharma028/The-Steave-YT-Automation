import base64
import time
from google import genai
from google.genai import types
from config import IMAGE_API_KEY, MASTER_STYLE_PROMPT, IMAGE_COST_PER_1M_TOKENS_USD, IMAGE_TOKENS_PER_IMAGE_1K, IMAGE_MODEL
from utils import setup_logger

logger = setup_logger("ImageGenerator")

# Initialize the client
client = genai.Client(api_key=IMAGE_API_KEY)

def generate_image(scene_description, output_path):
    """
    Generates a 16:9 image using the gemini-3.1-flash-image model.
    Applies the Master Style Prompt to ensure consistent 2D cartoon visuals.
    Saves the raw bytes returned by the API directly to a file.
    Calculates and returns the estimated USD cost of the image.
    Returns (success_status: bool, cost_usd: float).
    """
    full_prompt = MASTER_STYLE_PROMPT.format(scene_description=scene_description)

    logger.info(f"Requesting image generation with model {IMAGE_MODEL} for scene:\n'{scene_description}'")

    # Delay to respect API rate limits
    time.sleep(2) 

    cost_usd = 0.0 # Default cost if generation fails or is not applicable

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

        # Calculate cost upon successful image data retrieval
        # Assuming 1K resolution equivalent for token calculation
        tokens_consumed = IMAGE_TOKENS_PER_IMAGE_1K
        cost_usd = (tokens_consumed / 1_000_000) * IMAGE_COST_PER_1M_TOKENS_USD

        # Extract the image data
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data:
                    img_data = part.inline_data.data
                    with open(output_path, "wb") as f:
                        f.write(img_data)
                    logger.info(f"Image successfully saved to: {output_path} (Estimated Cost: ${cost_usd:.4f})")
                    return True, cost_usd

        logger.warning("API call succeeded, but no image data was found in response payload. Cost not applied.")
        return False, 0.0

    except Exception as e:
        logger.error(f"Critical error during image generation process: {e}")
        return False, 0.0
        return False
