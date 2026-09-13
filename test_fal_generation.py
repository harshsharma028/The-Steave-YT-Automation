import os
import sys
import time
import requests
from dotenv import load_dotenv

# Load local .env variables
load_dotenv()

# Verify requirements installation on import
try:
    import fal_client
except ImportError:
    print("[ERROR] 'fal-client' library is not installed.")
    print("Please install it by running: pip install fal-client requests")
    sys.exit(1)

# Ensure the output directory exists
OUTPUT_DIR = "image_testing"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Get API key from environment or fallback
FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    print("\n[WARNING] FAL_KEY not found in .env file.")
    user_key = input("Please paste your Fal.ai API key here to continue (or press Enter to abort): ").strip()
    if not user_key:
        print("[ABORT] API Key is required.")
        sys.exit(1)
    os.environ["FAL_KEY"] = user_key
    FAL_KEY = user_key
else:
    # Ensure client picks up key from env
    os.environ["FAL_KEY"] = FAL_KEY

USD_TO_INR_RATE = 95.20  # Current conversion rate from config

def run_test_generation():
    print("\n===========================================")
    print("      FAL.AI IMAGE GENERATION TEST         ")
    print("===========================================")

    # Select Model
    print("Select a model:")
    print("1. FLUX.1 [dev] (~Rs.2.38 / image)")
    print("2. FLUX.1 [schnell] (~Rs.0.28 / image)")
    print("3. Google Imagen (fal-ai/nano-banana) [default]")
    choice = input("Enter choice (1, 2, or 3) [default: 3]: ").strip()
    
    if choice == '1':
        model_name = "fal-ai/flux/dev"
        cost_per_mp = 0.025
        steps = 28
        is_flux = True
    elif choice == '2':
        model_name = "fal-ai/flux/schnell"
        cost_per_mp = 0.003
        steps = 4
        is_flux = True
    else:
        model_name = "fal-ai/nano-banana"
        cost_per_mp = 0.003  # Estimated low cost for Imagen on Fal
        steps = None
        is_flux = False

    # Select Aspect Ratio
    print("\nSelect aspect ratio format:")
    print("1. Long Form (16:9)")
    print("2. Short Form (9:16)")
    ar_choice = input("Enter choice (1 or 2) [default: 1]: ").strip()
    
    if is_flux:
        aspect_ratio = "portrait_16_9" if ar_choice == '2' else "landscape_16_9"
    else:
        aspect_ratio = "9:16" if ar_choice == '2' else "16:9"

    # Input prompt
    print("\nEnter your image prompt. To use the style of the project, you should merge it with a style prompt.")
    print("Press Enter to use the pre-merged prompt in 'test_prompt.txt' if it exists.")
    prompt_input = input("Prompt: ").strip()

    if not prompt_input:
        if os.path.exists("test_prompt.txt"):
            print("[INFO] Reading prompt from 'test_prompt.txt'...")
            with open("test_prompt.txt", "r", encoding="utf-8") as f:
                prompt_input = f.read().strip()
        else:
            prompt_input = (
                "A simple cartoon stickman looking at a huge, glowing laptop screen "
                "with a happy, amazed expression. Round white face, thick black outlines, "
                "bright colorful cozy study room."
            )
            print(f"[INFO] Using fallback default prompt: '{prompt_input}'")

    filename = f"test_{int(time.time())}.png"
    output_path = os.path.join(OUTPUT_DIR, filename)

    print(f"\n[GENERATING] Sending request to {model_name}...")
    print(f"Prompt preview: \"{prompt_input[:80]}...\"")
    
    start_time = time.time()
    try:
        # Build arguments dynamically based on the model type
        api_args = {
            "prompt": prompt_input
        }
        if is_flux:
            api_args["image_size"] = aspect_ratio
            api_args["num_inference_steps"] = steps # type: ignore
            api_args["enable_safety_checker"] = True # type: ignore
        else:
            api_args["aspect_ratio"] = aspect_ratio
            
        # API call via fal-client
        result = fal_client.subscribe(
            model_name,
            arguments=api_args
        )

        if "images" in result and len(result["images"]) > 0:
            image_info = result["images"][0]
            image_url = image_info["url"]
            width = image_info.get("width")
            height = image_info.get("height")
            
            # Megapixel cost calculation with fallback
            if width and height:
                megapixels = (width * height) / 1_000_000
            else:
                megapixels = 0.58  # Default 1024x576 equivalent for estimation
            cost_usd = megapixels * cost_per_mp
            cost_inr = cost_usd * USD_TO_INR_RATE
            
            print(f"[DOWNLOADING] Image URL resolved: {image_url}")
            
            # Atomic save
            img_data = requests.get(image_url).content
            tmp_path = output_path + ".tmp"
            with open(tmp_path, "wb") as f:
                f.write(img_data)
            
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(tmp_path, output_path)

            elapsed = time.time() - start_time
            print("\n" + "="*45)
            print(">>> GENERATION SUCCESSFUL! <<<")
            print("="*45)
            print(f"File Saved: {output_path}")
            print(f"Dimensions: {width}x{height} ({megapixels:.2f} Megapixels)")
            print(f"Time Taken: {elapsed:.2f} seconds")
            print(f"Est. Cost: ${cost_usd:.4f} USD (approx. Rs.{cost_inr:.2f} INR)")
            print("="*45)
        else:
            print("[ERROR] API succeeded but returned no image payload.")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Failed to generate image: {e}")

if __name__ == "__main__":
    run_test_generation()
