"""
Title Generation Module - Create SEO-optimized titles ranked by potential CTR.
Generates multiple variations and scores each for YouTube discoverability.
"""

import json
from google import genai
from config import TEXT_MODEL, CHAT_API_KEY
from utils import setup_logger

logger = setup_logger("TitleGenerator")


class TitleGenerator:
    """Generate SEO-optimized YouTube video titles."""

    def __init__(self, api_key=None):
        """Initialize title generator with Gemini API."""
        self.client = genai.Client(api_key=api_key or CHAT_API_KEY)
        self.model = TEXT_MODEL
        logger.info(f"📝 Title generator initialized")

    def generate_titles(self, script_text, topic, num_titles=5):
        """
        Generate multiple title options from a script.

        Args:
            script_text: Full video script
            topic: Video topic/keyword
            num_titles: Number of variations (3-10)

        Returns:
            List of title dicts with text and metadata
        """
        logger.info(f"📝 Generating {num_titles} titles for: {topic}")

        prompt = f"""You are a YouTube SEO expert. Create {num_titles} compelling video titles based on this script and topic.

Topic: {topic}
Script Preview: {script_text[:300]}...

Requirements for EACH title:
1. Under 60 characters (YouTube ideal)
2. Include the main keyword/topic
3. Use power words (how, why, best, top, secret, revealed, etc.)
4. Different angle/approach for each
5. Clickable but NOT clickbait (accurate to content)
6. Mix of question format and statement format

Format your response as a JSON array with exactly {num_titles} items:
[
  {{"title": "...", "style": "question|statement|number|curiosity|promise"}},
  ...
]

ONLY return the JSON array, no other text."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.8,
                    top_p=0.95
                )
            )

            response_text = response.text.strip()

            # Parse JSON response
            titles_data = json.loads(response_text)

            # Add metadata to each
            titles = []
            for idx, title_dict in enumerate(titles_data, 1):
                title_dict['rank'] = idx
                title_dict['character_count'] = len(title_dict.get('title', ''))
                titles.append(title_dict)

            logger.info(f"✓ Generated {len(titles)} titles")
            return titles

        except json.JSONDecodeError:
            logger.error("❌ Failed to parse title JSON response")
            # Fallback: return basic titles
            return self._generate_fallback_titles(topic, num_titles)
        except Exception as e:
            logger.error(f"❌ Title generation failed: {e}")
            raise

    def score_titles(self, titles, keyword, vidiq_scorer=None):
        """
        Score titles for SEO potential and CTR.

        Scoring factors:
        - Keyword inclusion (does title have main keyword)
        - Power words (how, why, best, top, revealed, etc.)
        - Length (ideal: 50-60 chars)
        - Variety (question vs statement)
        - Clickability (would you click this?)

        Args:
            titles: List of title dicts
            keyword: Main keyword to optimize for
            vidiq_scorer: Optional VidIQ API wrapper for real scoring

        Returns:
            Sorted titles by score (highest first)
        """
        logger.info(f"🎯 Scoring {len(titles)} titles")

        power_words = ['how', 'why', 'best', 'top', 'secret', 'revealed', 'amazing', 'incredible',
                      'complete', 'ultimate', 'proven', 'easy', 'fast', 'simple', 'essential']

        scored = []

        for title_dict in titles:
            title = title_dict.get('title', '')
            score = 0

            # Keyword inclusion (3 points)
            if keyword.lower() in title.lower():
                score += 3
            elif any(word in title.lower() for word in keyword.lower().split()):
                score += 2
            else:
                score += 0

            # Power words (2 points)
            power_word_count = sum(1 for word in power_words if word in title.lower())
            score += min(2, power_word_count * 0.5)

            # Length optimization (2 points)
            char_count = len(title)
            if 50 <= char_count <= 60:
                score += 2
            elif 40 <= char_count <= 70:
                score += 1
            else:
                score += 0

            # Format variety (1 point)
            if title.endswith('?'):
                score += 1  # Question format good for engagement
            elif any(title.startswith(str(i)) for i in range(1, 10)):
                score += 1  # Number format good for lists
            else:
                score += 0.5

            # Clickability assessment (2 points) - based on intrigue
            intrigue_words = ['secret', 'revealed', 'truth', 'shocking', 'unexpected', 'finally', 'never']
            if any(word in title.lower() for word in intrigue_words):
                score += 1.5
            else:
                score += 0.5

            final_score = round(min(10, score), 1)

            scored.append({
                **title_dict,
                'seo_score': final_score,
                'keyword_present': keyword.lower() in title.lower(),
                'character_count': char_count
            })

        # Sort by score
        sorted_titles = sorted(scored, key=lambda x: x['seo_score'], reverse=True)

        logger.info(f"✓ Scored and ranked {len(sorted_titles)} titles")
        return sorted_titles

    def get_best_title(self, titles):
        """
        Get the single best title from a scored list.

        Returns:
            Best title dict
        """
        if not titles:
            logger.warning("⚠️  No titles provided")
            return None

        best = titles[0]
        logger.info(f"🏆 Best title: {best['title']} (Score: {best.get('seo_score', '?')})")
        return best

    def generate_youtube_ready_metadata(self, titles):
        """
        Format titles for YouTube upload (remove emojis, ensure compliance).

        Returns:
            List of YouTube-safe title strings
        """
        safe_titles = []

        for title_dict in titles:
            title = title_dict.get('title', '')

            # Remove problematic characters for YouTube
            title = title.replace('🎬', '').replace('📺', '').replace('⭐', '')
            title = title.replace('❌', '').replace('✅', '').replace('✨', '')

            # Ensure no excessive punctuation
            title = title.replace('!!!', '!').replace('???', '?')

            # Trim whitespace
            title = title.strip()

            safe_titles.append({
                **title_dict,
                'title': title,
                'youtube_safe': True
            })

        return safe_titles

    def _generate_fallback_titles(self, topic, num_titles):
        """Generate basic titles if API fails."""
        logger.warning("⚠️  Using fallback title generation")

        templates = [
            f"{topic} - Complete Guide",
            f"How to {topic} in 2025",
            f"7 Ways to {topic}",
            f"Why {topic} Matters",
            f"The Truth About {topic}",
            f"Master {topic} - Step by Step",
            f"Best {topic} Explained",
            f"What You Need to Know About {topic}",
            f"The Ultimate {topic} Tutorial",
            f"Proven {topic} Strategies"
        ]

        return [
            {
                'title': templates[i % len(templates)],
                'style': 'fallback',
                'rank': i + 1
            }
            for i in range(min(num_titles, len(templates)))
        ]

    def print_title_report(self, titles, topic=None):
        """Print formatted title report."""
        print("\n" + "=" * 80)
        print("TITLE GENERATION REPORT")
        if topic:
            print(f"Topic: {topic}")
        print("=" * 80)

        for i, title in enumerate(titles, 1):
            score = title.get('seo_score', '?')
            chars = title.get('character_count', '?')
            style = title.get('style', 'unknown')
            keyword = "✓" if title.get('keyword_present') else "✗"

            print(f"\n{i}. [{score}/10 | {chars} chars | {style}] {keyword} Keyword")
            print(f"   {title['title']}")

        print("\n" + "=" * 80 + "\n")

    def export_titles(self, titles, output_file="titles.json"):
        """Export generated titles to JSON."""
        export_data = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'titles': titles,
            'total_titles': len(titles),
            'best_title': titles[0] if titles else None
        }

        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"✓ Titles exported to {output_file}")
        return output_file
