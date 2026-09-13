"""
Tag & Hashtag Generator - Create optimized tags for YouTube and social media.
Includes SEO tags, trending tags, and social media hashtags.
"""

import json
from google import genai
from config import TEXT_MODEL, CHAT_API_KEY
from utils import setup_logger

logger = setup_logger("TagGenerator")


class TagGenerator:
    """Generate optimized YouTube and social media tags."""

    def __init__(self, api_key=None):
        """Initialize tag generator."""
        self.client = genai.Client(api_key=api_key or CHAT_API_KEY)
        self.model = TEXT_MODEL
        logger.info(f"🏷️  Tag generator initialized")

    def generate_tags(self, script_text, topic, title, max_tags=30):
        """
        Generate SEO-optimized YouTube tags.

        YouTube limits: 30 tags maximum, each 30 chars max

        Args:
            script_text: Full video script
            topic: Main topic keyword
            title: Video title
            max_tags: Max tags to generate (YouTube limit is 30)

        Returns:
            List of tag strings, sorted by relevance
        """
        logger.info(f"🏷️  Generating tags for: {title}")

        script_preview = script_text[:400] if len(script_text) > 400 else script_text

        prompt = f"""Generate {max_tags} YouTube SEO tags for this video. ONLY return the tags as a JSON array, one per line.

Title: {title}
Topic: {topic}
Script Preview: {script_preview}...

Tag Requirements:
1. Each tag max 30 characters
2. Mix of: main keyword, long-tail keywords, related topics, trending variations
3. Include: exact topic, variations, related searches, sub-topics
4. Start with most important/popular tags
5. Use underscores for multi-word tags only if necessary
6. Avoid generic tags, focus on searchable specific terms
7. Include trending variations (e.g., "2025", "explained", "tutorial")
8. NO spam tags, NO unrelated tags

Format: Return ONLY a JSON array of strings:
["tag1", "tag2", "tag3", ...]

Return exactly {max_tags} tags."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.6,
                    top_p=0.9
                )
            )

            response_text = response.text.strip()

            # Parse JSON
            tags_list = json.loads(response_text)

            # Validate and clean tags
            validated_tags = []
            for tag in tags_list:
                tag = str(tag).strip()
                if len(tag) > 0 and len(tag) <= 30:
                    validated_tags.append(tag)

            # Limit to 30 (YouTube max)
            validated_tags = validated_tags[:30]

            logger.info(f"✓ Generated {len(validated_tags)} tags")
            return validated_tags

        except json.JSONDecodeError:
            logger.error("❌ Failed to parse tags JSON")
            return self._generate_fallback_tags(topic, title, max_tags)
        except Exception as e:
            logger.error(f"❌ Tag generation failed: {e}")
            raise

    def generate_hashtags(self, script_text, topic, title, max_hashtags=15, for_platform="instagram"):
        """
        Generate social media hashtags.

        Args:
            script_text: Full video script
            topic: Main topic
            title: Video title
            max_hashtags: Number of hashtags (15-30 typical)
            for_platform: 'instagram', 'tiktok', 'twitter', 'youtube'

        Returns:
            List of hashtag strings (with # prefix)
        """
        logger.info(f"#️⃣  Generating {for_platform} hashtags")

        platform_guidance = {
            'instagram': "Instagram hashtags (mix: 5-10 popular, 5-10 niche, use trending hashtags)",
            'tiktok': "TikTok hashtags (trending + niche mix, shorter tags work better)",
            'twitter': "Twitter hashtags (only 1-3 most important, concise)",
            'youtube': "YouTube community post hashtags (searchable, specific)"
        }

        guidance = platform_guidance.get(for_platform, platform_guidance['instagram'])

        prompt = f"""Generate {max_hashtags} {for_platform} hashtags for this video.

Title: {title}
Topic: {topic}

{guidance}

Return ONLY a JSON array of hashtags (include # symbol):
["#hashtag1", "#hashtag2", ...]

Return exactly {max_hashtags} hashtags."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.6,
                    top_p=0.9
                )
            )

            response_text = response.text.strip()
            hashtags = json.loads(response_text)

            # Ensure # prefix
            validated = []
            for tag in hashtags:
                tag = str(tag).strip()
                if not tag.startswith('#'):
                    tag = '#' + tag
                validated.append(tag)

            logger.info(f"✓ Generated {len(validated)} hashtags for {for_platform}")
            return validated

        except json.JSONDecodeError:
            logger.error("❌ Failed to parse hashtags JSON")
            return self._generate_fallback_hashtags(topic, max_hashtags)
        except Exception as e:
            logger.error(f"❌ Hashtag generation failed: {e}")
            raise

    def score_tags(self, tags, topic, search_volume_map=None):
        """
        Score tags for relevance and searchability.

        Scoring factors:
        - Exact keyword match
        - Tag specificity (longer = more specific)
        - Estimated search volume (if available)
        - Trending potential

        Args:
            tags: List of tag strings
            topic: Main topic keyword
            search_volume_map: Optional dict of tag -> search volume

        Returns:
            Scored tags dict with relevance scores
        """
        scored = []

        for tag in tags:
            score = 0

            # Keyword match (3 points)
            if tag.lower() == topic.lower():
                score += 3
            elif topic.lower() in tag.lower():
                score += 2
            else:
                score += 0.5

            # Specificity (2 points) - longer tags are more specific
            tag_length = len(tag.split())
            if tag_length >= 3:
                score += 2
            elif tag_length == 2:
                score += 1
            else:
                score += 0

            # Search volume (if provided) (3 points)
            if search_volume_map and tag in search_volume_map:
                volume = search_volume_map[tag]
                if volume > 10000:
                    score += 3
                elif volume > 1000:
                    score += 2
                elif volume > 100:
                    score += 1
            else:
                score += 1  # Default for unknown volume

            # Trending potential (2 points)
            trending_words = ['2025', 'trending', 'new', 'best', 'top', 'how to', 'tutorial']
            if any(w in tag.lower() for w in trending_words):
                score += 2
            else:
                score += 0.5

            scored.append({
                'tag': tag,
                'relevance_score': round(min(10, score), 1)
            })

        # Sort by score
        sorted_tags = sorted(scored, key=lambda x: x['relevance_score'], reverse=True)
        return sorted_tags

    def get_youtube_tags_string(self, tags, max_count=30):
        """
        Format tags for YouTube upload (space-separated).

        Args:
            tags: List of tag strings
            max_count: YouTube max is 30

        Returns:
            Space-separated tags string
        """
        tags = tags[:max_count]
        return ' '.join(tags)

    def get_social_media_hashtag_string(self, hashtags, max_count=30, separator='\n'):
        """
        Format hashtags for social media post.

        Args:
            hashtags: List of hashtag strings
            max_count: Max to include
            separator: '\n' for separate lines, ' ' for inline

        Returns:
            Formatted hashtag string
        """
        hashtags = hashtags[:max_count]
        return separator.join(hashtags)

    def _generate_fallback_tags(self, topic, title, count):
        """Generate basic tags if API fails."""
        logger.warning("⚠️  Using fallback tag generation")

        base_tags = [
            topic,
            topic + " 2025",
            topic + " explained",
            topic + " tutorial",
            topic + " guide",
            topic + " how to",
            "explained",
            "tutorial",
            "howto",
            "guide"
        ]

        return (base_tags * (count // len(base_tags) + 1))[:count]

    def _generate_fallback_hashtags(self, topic, count):
        """Generate basic hashtags if API fails."""
        words = topic.split()
        base_hashtags = [f"#{w}" for w in words]
        base_hashtags.extend(['#tutorial', '#howto', '#explained', '#learn', '#education'])

        return (base_hashtags * (count // len(base_hashtags) + 1))[:count]

    def print_tags_report(self, tags, hashtags_dict=None):
        """Print formatted tags report."""
        print("\n" + "=" * 80)
        print("TAGS & HASHTAGS REPORT")
        print("=" * 80)

        print(f"\n📌 YouTube Tags ({len(tags)} tags):")
        for i, tag in enumerate(tags, 1):
            print(f"  {i:2d}. {tag}")

        if hashtags_dict:
            print(f"\n#️⃣  Social Media Hashtags:")
            for platform, hashtags in hashtags_dict.items():
                print(f"\n  {platform.upper()} ({len(hashtags)} hashtags):")
                for i, tag in enumerate(hashtags, 1):
                    print(f"    {i:2d}. {tag}")

        print("\n" + "=" * 80 + "\n")

    def export_tags(self, tags, hashtags_dict=None, output_file="tags.json"):
        """Export tags to JSON file."""
        export_data = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'youtube_tags': tags,
            'total_youtube_tags': len(tags),
            'hashtags': hashtags_dict or {},
            'youtube_tags_string': ' '.join(tags[:30])
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Tags exported to {output_file}")
        return output_file
