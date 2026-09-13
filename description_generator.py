"""
Description Generator - Create keyword-optimized YouTube descriptions.
Includes timestamps, links, hashtags, and SEO optimization.
"""

import json
from google import genai
from config import TEXT_MODEL, CHAT_API_KEY
from utils import setup_logger

logger = setup_logger("DescriptionGenerator")


class DescriptionGenerator:
    """Generate optimized YouTube video descriptions."""

    def __init__(self, api_key=None):
        """Initialize description generator."""
        self.client = genai.Client(api_key=api_key or CHAT_API_KEY)
        self.model = TEXT_MODEL
        logger.info(f"📄 Description generator initialized")

    def generate_description(self, script_text, topic, title, tags=None, video_length_seconds=300):
        """
        Generate SEO-optimized YouTube description.

        Args:
            script_text: Full video script
            topic: Main topic/keyword
            title: Video title (for consistency)
            tags: Optional list of relevant tags
            video_length_seconds: Video duration (for timestamps)

        Returns:
            Description dict with text, segments, SEO analysis
        """
        logger.info(f"📄 Generating description for: {title}")

        script_preview = script_text[:500] if len(script_text) > 500 else script_text

        tags_text = f"\nKey tags to include: {', '.join(tags)}" if tags else ""

        prompt = f"""You are a YouTube SEO expert. Write an engaging, keyword-optimized YouTube video description.

Title: {title}
Topic: {topic}
Script Preview: {script_preview}...{tags_text}

Requirements:
1. Start with 2-3 sentence hook explaining what viewers will learn
2. Include main keyword in first 2 sentences
3. Add "Key Topics Covered:" section with bullet points (5-7 key points from script)
4. Add "Timestamps:" section (estimate 3-4 chapter times based on typical pacing)
5. Add "Resources & Links:" placeholder for relevant links
6. End with engagement CTAs (like, subscribe, comment)
7. Keep first 150 characters punchy (shows in preview)
8. Optimize for search: naturally include related keywords
9. Format with line breaks for readability
10. NO emojis, NO spam, NO clickbait

Output format:
[HOOK SECTION]
...

[KEY TOPICS]
- Point 1
- Point 2
...

[TIMESTAMPS]
0:00 Introduction
...

[LINKS]
(Links section for user to fill in)

[ENGAGEMENT CTA]
..."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95
                )
            )

            description_text = response.text.strip()

            result = {
                'description_text': description_text,
                'topic': topic,
                'title': title,
                'character_count': len(description_text),
                'word_count': len(description_text.split()),
                'video_length_seconds': video_length_seconds
            }

            logger.info(f"✓ Description generated ({result['character_count']} chars)")
            return result

        except Exception as e:
            logger.error(f"❌ Description generation failed: {e}")
            raise

    def score_description(self, description_dict, topic, tags=None):
        """
        Score description for SEO quality.

        Scoring factors:
        - Keyword inclusion (topic in first 2 sentences)
        - Length (150-5000 chars ideal)
        - Structure (has sections)
        - CTA presence (engagement request)
        - Readability (line breaks, bullet points)

        Returns:
            Quality score 0-10
        """
        text = description_dict.get('description_text', '')
        char_count = len(text)
        word_count = len(text.split())

        score = 0

        # Keyword inclusion (2 points)
        first_two_sentences = ' '.join(text.split('.')[:2]).lower()
        if topic.lower() in first_two_sentences:
            score += 2
        elif any(word in first_two_sentences for word in topic.lower().split()):
            score += 1
        else:
            score += 0

        # Length optimization (2 points)
        if 500 <= char_count <= 5000:
            score += 2
        elif 300 <= char_count <= 6000:
            score += 1
        else:
            score += 0

        # Structure (2 points) - check for sections
        sections = ['[', 'KEY TOPICS', 'TIMESTAMPS', 'LINKS', 'RESOURCES']
        section_count = sum(1 for s in sections if s in text)
        score += min(2, section_count * 0.4)

        # CTA presence (2 points)
        ctas = ['subscribe', 'like', 'comment', 'ring', 'notification']
        cta_count = sum(1 for c in ctas if c in text.lower())
        score += min(2, cta_count * 0.5)

        # Readability (2 points) - line breaks and formatting
        line_breaks = text.count('\n')
        bullet_points = text.count('-')
        if line_breaks > 5 and bullet_points > 3:
            score += 2
        elif line_breaks > 3 or bullet_points > 2:
            score += 1
        else:
            score += 0

        final_score = round(min(10, score), 1)
        return final_score

    def add_timestamps(self, description, script_text, video_length_seconds=300):
        """
        Generate timestamps based on script segments.

        Args:
            description: Description dict
            script_text: Full script
            video_length_seconds: Total duration

        Returns:
            Description with [TIMESTAMPS] section populated
        """
        # Split script into rough sections
        sentences = [s.strip() for s in script_text.split('.') if s.strip()]

        # Estimate 30-40 words per ~10 seconds
        words_per_10s = 35
        total_words = len(script_text.split())

        timestamps = []
        current_time = 0
        section_size = total_words // 4  # 4 chapters

        for i, sentence in enumerate(sentences):
            word_count = len(sentence.split())
            time_offset = (word_count / words_per_10s) * 10

            if i % (len(sentences) // 4) == 0 and i > 0:
                section_title = sentence[:40] + "..."
                timestamps.append(f"{int(current_time // 60)}:{int(current_time % 60):02d} {section_title}")

            current_time += time_offset

        # Add intro and outro
        timestamps_text = "0:00 Introduction\n"
        timestamps_text += "\n".join(timestamps)
        timestamps_text += f"\n{int(current_time // 60)}:{int(current_time % 60):02d} Conclusion"

        description['timestamps'] = timestamps_text
        return description

    def add_links_section(self, description, links_dict=None):
        """
        Add customizable links section to description.

        Args:
            description: Description dict
            links_dict: Optional dict with link names and URLs

        Returns:
            Description with links section
        """
        if links_dict is None:
            links_dict = {}

        links_text = "📚 Resources & Links:\n"

        if links_dict:
            for name, url in links_dict.items():
                links_text += f"• {name}: {url}\n"
        else:
            links_text += "• [Add your links here]\n"

        description['links_section'] = links_text
        return description

    def finalize_description(self, description, add_hashtags=True):
        """
        Finalize description for YouTube upload.

        Adds:
        - Links section
        - Timestamps
        - Optional hashtags
        - Final engagement CTA

        Returns:
            Final description ready to paste into YouTube
        """
        text = description.get('description_text', '')

        # Add custom sections if not already present
        if 'LINKS' not in text and 'links_section' in description:
            text += "\n\n" + description['links_section']

        if 'TIMESTAMPS' not in text and 'timestamps' in description:
            text += "\n\n[TIMESTAMPS]\n" + description['timestamps']

        # Clean up formatting
        text = text.replace('[', '').replace(']', '')  # Remove bracket markers
        text = text.strip()

        final_description = {
            **description,
            'final_text': text,
            'character_count': len(text),
            'word_count': len(text.split()),
            'ready_for_upload': True
        }

        logger.info(f"✓ Description finalized ({final_description['character_count']} chars)")
        return final_description

    def print_description_report(self, description_dict):
        """Print formatted description report."""
        print("\n" + "=" * 80)
        print("DESCRIPTION GENERATION REPORT")
        print("=" * 80)

        text = description_dict.get('description_text', description_dict.get('final_text', ''))
        print(f"\nTitle: {description_dict.get('title', 'N/A')}")
        print(f"Characters: {description_dict.get('character_count', 0)}")
        print(f"Words: {description_dict.get('word_count', 0)}")

        print(f"\n[PREVIEW - First 300 chars]")
        print(f"{text[:300]}...\n")

        print(f"\n[FULL DESCRIPTION]")
        print(text)

        print("\n" + "=" * 80 + "\n")

    def export_description(self, description, output_file="description.txt"):
        """Export description to text file."""
        text = description.get('final_text', description.get('description_text', ''))

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)

        logger.info(f"✓ Description exported to {output_file}")
        return output_file
