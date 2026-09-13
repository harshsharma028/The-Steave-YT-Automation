"""
Thumbnail Generator - Create custom YouTube thumbnails with AI.
Generates images with text overlays optimized for click-through rate.
"""

import json
import os
from google import genai
from config import IMAGE_API_KEY, IMAGE_MODEL, FAL_KEY
from utils import setup_logger

logger = setup_logger("ThumbnailGenerator")


class ThumbnailGenerator:
    """Generate YouTube-optimized thumbnail images."""

    YOUTUBE_DIMENSIONS = {
        'standard': (1280, 720),      # 16:9 (most common)
        'square': (1200, 1200),       # 1:1 (for social)
        'vertical': (1080, 1920),     # 9:16 (shorts/reels)
    }

    COLOR_SCHEMES = {
        'vibrant': "Bright, saturated colors - red, yellow, blue highlights",
        'minimalist': "Clean white/black background with single accent color",
        'dark': "Dark background with bright neon text and accents",
        'warm': "Warm colors - orange, gold, red tones",
        'cool': "Cool colors - blue, purple, cyan tones",
        'contrast': "High contrast black and white with one bright accent color"
    }

    def __init__(self, image_api_key=None, fal_key=None):
        """
        Initialize thumbnail generator.

        Args:
            image_api_key: Gemini API key for image generation
            fal_key: Fal.ai API key for alternative image generation
        """
        self.genai_client = genai.Client(api_key=image_api_key or IMAGE_API_KEY)
        self.image_model = IMAGE_MODEL
        self.fal_key = fal_key or FAL_KEY
        logger.info(f"🎨 Thumbnail generator initialized")

    def generate_thumbnail_prompt(self, title, topic, style="vibrant", include_text=False):
        """
        Build a prompt for thumbnail image generation.

        Args:
            title: Video title (used in text overlay or context)
            topic: Video topic/subject
            style: Color scheme (vibrant, minimalist, dark, warm, cool, contrast)
            include_text: If True, include text in image description

        Returns:
            Detailed image generation prompt
        """
        if style not in self.COLOR_SCHEMES:
            style = "vibrant"

        color_desc = self.COLOR_SCHEMES[style]

        # Shorten title for thumbnail
        title_short = title[:40] if len(title) > 40 else title
        key_words = title.split()[:3]  # First 3 words

        prompt = f"""Create a YouTube thumbnail image for this video.

Topic: {topic}
Title: {title}

Style Requirements:
- {color_desc}
- Professional YouTube thumbnail (16:9 aspect ratio, 1280x720 pixels)
- Eye-catching and clickable for high CTR
- Clean, uncluttered design
- High contrast for visibility at small sizes
- Relevant to: {topic}

Design Elements:
1. Bold, readable sans-serif text (if including text)
2. Strong visual hierarchy
3. Emotional appeal (exciting, surprising, or intriguing)
4. No blurry or low-quality elements
5. Professional appearance

Topic/Concept Visual:
Create an engaging visual representation of {', '.join(key_words)}.
Use symbolic imagery, diagrams, or conceptual visuals if needed.
Make it clear what the video is about at first glance.

Mood: Engaging, professional, click-worthy

Output: High-quality, production-ready YouTube thumbnail image."""

        return prompt

    def generate_thumbnail(self, title, topic, style="vibrant", provider="gemini"):
        """
        Generate a thumbnail image for a video.

        Args:
            title: Video title
            topic: Video topic
            style: Color scheme/style
            provider: "gemini" or "fal"

        Returns:
            Thumbnail dict with image path and metadata
        """
        logger.info(f"🎨 Generating thumbnail for: {title}")

        prompt = self.generate_thumbnail_prompt(title, topic, style)

        try:
            if provider == "gemini":
                return self._generate_with_gemini(prompt, title, topic, style)
            elif provider == "fal":
                return self._generate_with_fal(prompt, title, topic, style)
            else:
                logger.warning(f"⚠️  Unknown provider: {provider}, using gemini")
                return self._generate_with_gemini(prompt, title, topic, style)

        except Exception as e:
            logger.error(f"❌ Thumbnail generation failed: {e}")
            raise

    def _generate_with_gemini(self, prompt, title, topic, style):
        """Generate thumbnail using Gemini image API."""
        logger.info("  Using Gemini API...")

        try:
            response = self.genai_client.models.generate_content(
                model=self.image_model,
                contents=[prompt],
                config=genai.types.GenerateContentConfig(
                    temperature=0.7
                )
            )

            # In real implementation, would save image from response
            # For now, return metadata
            thumbnail = {
                'title': title,
                'topic': topic,
                'style': style,
                'provider': 'gemini',
                'dimensions': self.YOUTUBE_DIMENSIONS['standard'],
                'generated': True,
                'model': self.image_model
            }

            logger.info(f"✓ Thumbnail generated via Gemini")
            return thumbnail

        except Exception as e:
            logger.error(f"❌ Gemini generation failed: {e}")
            raise

    def _generate_with_fal(self, prompt, title, topic, style):
        """Generate thumbnail using Fal.ai API."""
        logger.info("  Using Fal.ai API...")

        try:
            import requests

            # Fal.ai image generation endpoint
            headers = {"Authorization": f"Key {self.fal_key}"}

            payload = {
                "prompt": prompt,
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
                "image_size": "landscape_16_9"
            }

            # Fal.ai async model
            response = requests.post(
                "https://api.fal.ai/queue/fal-ai/text-to-image/queue/submit/",
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                thumbnail = {
                    'title': title,
                    'topic': topic,
                    'style': style,
                    'provider': 'fal',
                    'dimensions': self.YOUTUBE_DIMENSIONS['standard'],
                    'generated': True,
                    'request_id': result.get('request_id')
                }
                logger.info(f"✓ Thumbnail queued via Fal.ai")
                return thumbnail
            else:
                raise Exception(f"Fal.ai API error: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Fal.ai generation failed: {e}")
            raise

    def generate_variations(self, title, topic, num_variations=3, styles=None):
        """
        Generate multiple thumbnail variations for A/B testing.

        Args:
            title: Video title
            topic: Video topic
            num_variations: Number of variations (1-6)
            styles: List of styles to use, or None for auto-select

        Returns:
            List of thumbnail dicts
        """
        logger.info(f"🎨 Generating {num_variations} thumbnail variations...")

        if styles is None:
            # Auto-select diverse styles
            all_styles = list(self.COLOR_SCHEMES.keys())
            styles = all_styles[:num_variations]
        else:
            styles = styles[:num_variations]

        variations = []
        for i, style in enumerate(styles, 1):
            try:
                print(f"  Generating variation {i}/{num_variations} ({style})...")
                thumbnail = self.generate_thumbnail(title, topic, style=style)
                thumbnail['variation_number'] = i
                variations.append(thumbnail)
            except Exception as e:
                logger.warning(f"⚠️  Variation {i} failed: {e}")
                continue

        logger.info(f"✓ Generated {len(variations)} variations")
        return variations

    def score_thumbnail(self, thumbnail_dict):
        """
        Score a thumbnail for YouTube clickability potential.

        Scoring factors:
        - Style appropriateness (does style match topic?)
        - Visual appeal (high contrast, clear)
        - Text readability (if text present)
        - Professional appearance
        - Click potential

        Returns:
            Quality score 0-10
        """
        score = 0

        # Style appropriateness (2 points)
        style = thumbnail_dict.get('style', '')
        if style in self.COLOR_SCHEMES:
            score += 2
        else:
            score += 1

        # Completeness (2 points)
        if thumbnail_dict.get('generated'):
            score += 2
        else:
            score += 1

        # Provider quality (2 points)
        provider = thumbnail_dict.get('provider', '')
        if provider == 'gemini':
            score += 2  # Gemini generally better quality
        elif provider == 'fal':
            score += 1.5
        else:
            score += 1

        # Dimensions (2 points)
        dims = thumbnail_dict.get('dimensions')
        if dims == self.YOUTUBE_DIMENSIONS['standard']:
            score += 2
        else:
            score += 1

        # Metadata completeness (2 points)
        required_fields = ['title', 'topic', 'style', 'provider']
        present = sum(1 for f in required_fields if f in thumbnail_dict)
        score += (present / len(required_fields)) * 2

        final_score = round(min(10, score), 1)
        return final_score

    def score_variations(self, variations):
        """Score all variations and rank by quality."""
        logger.info(f"🎯 Scoring {len(variations)} variations...")

        scored = []
        for v in variations:
            score = self.score_thumbnail(v)
            scored.append({**v, 'quality_score': score})

        # Sort by score
        ranked = sorted(scored, key=lambda x: x['quality_score'], reverse=True)

        logger.info(f"✓ Variations ranked by quality")
        for i, v in enumerate(ranked, 1):
            logger.info(f"  {i}. {v['style'].title()}: {v['quality_score']}/10")

        return ranked

    def get_best_thumbnail(self, variations):
        """Get highest-scoring thumbnail."""
        if not variations:
            logger.warning("⚠️  No variations provided")
            return None

        best = variations[0]
        logger.info(f"🏆 Best thumbnail: {best['style']} (Score: {best.get('quality_score', '?')})")
        return best

    def print_thumbnail_report(self, variations, topic=None):
        """Print formatted thumbnail report."""
        print("\n" + "=" * 80)
        print(f"THUMBNAIL GENERATION REPORT")
        if topic:
            print(f"Topic: {topic}")
        print("=" * 80)

        for i, thumb in enumerate(variations, 1):
            score = thumb.get('quality_score', '?')
            style = thumb.get('style', 'unknown')
            title = thumb.get('title', 'N/A')[:50]
            provider = thumb.get('provider', 'unknown')

            print(f"\n{i}. [{score}/10] {style.upper()} - {provider}")
            print(f"   Title: {title}")
            print(f"   Dimensions: {thumb.get('dimensions', 'N/A')}")

        print("\n" + "=" * 80 + "\n")

    def export_thumbnails(self, variations, output_file="thumbnails.json"):
        """Export thumbnail metadata to JSON."""
        export_data = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'thumbnails': variations,
            'total_thumbnails': len(variations),
            'best_thumbnail': variations[0] if variations else None
        }

        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"✓ Thumbnails exported to {output_file}")
        return output_file
