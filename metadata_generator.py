"""
Metadata Generator - Orchestrate title, description, and tag generation.
Creates complete YouTube metadata package from scripts.
"""

import json
from title_generator import TitleGenerator
from description_generator import DescriptionGenerator
from tag_generator import TagGenerator
from utils import setup_logger

logger = setup_logger("MetadataGenerator")


class MetadataGenerator:
    """Generate complete YouTube metadata from scripts."""

    def __init__(self, api_key=None):
        """Initialize metadata generator with sub-generators."""
        self.title_gen = TitleGenerator(api_key)
        self.desc_gen = DescriptionGenerator(api_key)
        self.tag_gen = TagGenerator(api_key)
        logger.info(f"🎬 Metadata generator initialized")

    def generate_complete_metadata(self, script_dict, topic, num_titles=5, video_length_seconds=300):
        """
        Generate complete YouTube metadata package.

        Creates:
        - 5 title variations (ranked)
        - SEO-optimized description
        - 30 tags (YouTube max)
        - Hashtags for social media

        Args:
            script_dict: Script dict (with script_text and hook_type)
            topic: Main topic/keyword
            num_titles: Number of title variations
            video_length_seconds: Video duration

        Returns:
            Complete metadata dict ready for YouTube
        """
        logger.info(f"🎬 Generating complete metadata for: {topic}")

        script_text = script_dict.get('script_text', '')
        hook_type = script_dict.get('hook_type', 'curiosity')

        # Step 1: Generate titles
        print("  Generating titles...")
        titles = self.title_gen.generate_titles(script_text, topic, num_titles=num_titles)
        titles = self.title_gen.score_titles(titles, topic)
        best_title = self.title_gen.get_best_title(titles)
        logger.info(f"✓ Generated {len(titles)} titles, best: {best_title['title']}")

        # Step 2: Generate description
        print("  Generating description...")
        description = self.desc_gen.generate_description(
            script_text, topic, best_title['title'],
            video_length_seconds=video_length_seconds
        )
        description = self.desc_gen.add_timestamps(description, script_text, video_length_seconds)
        description = self.desc_gen.finalize_description(description)
        desc_score = self.desc_gen.score_description(description, topic)
        logger.info(f"✓ Description generated (Score: {desc_score}/10)")

        # Step 3: Generate tags
        print("  Generating tags...")
        tags = self.tag_gen.generate_tags(script_text, topic, best_title['title'], max_tags=30)
        scored_tags = self.tag_gen.score_tags(tags, topic)
        tags_only = [t['tag'] for t in scored_tags]
        logger.info(f"✓ Generated {len(tags_only)} tags")

        # Step 4: Generate hashtags
        print("  Generating hashtags...")
        instagram_hashtags = self.tag_gen.generate_hashtags(
            script_text, topic, best_title['title'],
            max_hashtags=20, for_platform='instagram'
        )
        tiktok_hashtags = self.tag_gen.generate_hashtags(
            script_text, topic, best_title['title'],
            max_hashtags=15, for_platform='tiktok'
        )
        logger.info(f"✓ Generated hashtags (Instagram: {len(instagram_hashtags)}, TikTok: {len(tiktok_hashtags)})")

        # Compile complete metadata
        metadata = {
            'topic': topic,
            'hook_type': hook_type,
            'video_length_seconds': video_length_seconds,

            # Titles (ranked)
            'titles': {
                'all_variations': titles,
                'best_title': best_title['title'],
                'best_title_full': best_title,
                'total_variations': len(titles)
            },

            # Description
            'description': {
                'text': description.get('final_text', description.get('description_text', '')),
                'character_count': description.get('character_count', 0),
                'word_count': description.get('word_count', 0),
                'score': desc_score
            },

            # Tags
            'tags': {
                'youtube_tags': tags_only,
                'tag_count': len(tags_only),
                'tags_string': ' '.join(tags_only[:30])
            },

            # Hashtags
            'hashtags': {
                'instagram': instagram_hashtags,
                'tiktok': tiktok_hashtags,
                'instagram_string': ' '.join(instagram_hashtags),
                'tiktok_string': ' '.join(tiktok_hashtags)
            },

            # Ready for upload
            'ready_for_upload': True,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }

        logger.info(f"✅ Complete metadata package generated")
        return metadata

    def score_metadata(self, metadata):
        """
        Score overall metadata quality.

        Factors:
        - Title quality (SEO score)
        - Description quality
        - Tag comprehensiveness
        - Overall completeness

        Returns:
            Overall quality score 0-10
        """
        score = 0

        # Title score (3 points)
        if metadata.get('titles', {}).get('best_title_full'):
            best_title = metadata['titles']['best_title_full']
            title_score = best_title.get('seo_score', 5) / 10 * 3
            score += title_score
        else:
            score += 1

        # Description score (3 points)
        desc_score = metadata.get('description', {}).get('score', 5)
        score += (desc_score / 10) * 3

        # Tags (2 points)
        tag_count = metadata.get('tags', {}).get('tag_count', 0)
        if tag_count >= 25:
            score += 2
        elif tag_count >= 15:
            score += 1.5
        else:
            score += tag_count / 30 * 2

        # Completeness (2 points)
        components = [
            'titles' in metadata,
            'description' in metadata,
            'tags' in metadata,
            'hashtags' in metadata
        ]
        if all(components):
            score += 2
        else:
            score += sum(components) * 0.5

        final_score = round(min(10, score), 1)
        return final_score

    def print_metadata_report(self, metadata):
        """Print formatted metadata report."""
        print("\n" + "=" * 80)
        print("COMPLETE METADATA REPORT")
        print("=" * 80)

        print(f"\n📝 Topic: {metadata.get('topic', 'N/A')}")
        print(f"🎯 Hook Type: {metadata.get('hook_type', 'N/A')}")
        print(f"⏱️  Video Length: {metadata.get('video_length_seconds', 0)} seconds")

        # Titles
        titles_section = metadata.get('titles', {})
        print(f"\n📌 TITLES ({titles_section.get('total_variations', 0)} variations):")
        for title_dict in titles_section.get('all_variations', [])[:5]:
            score = title_dict.get('seo_score', '?')
            print(f"  ⭐ {score}/10 - {title_dict.get('title', 'N/A')}")

        # Description preview
        desc_section = metadata.get('description', {})
        print(f"\n📄 DESCRIPTION ({desc_section.get('character_count', 0)} chars):")
        desc_text = desc_section.get('text', '')
        preview = desc_text[:150] + "..." if len(desc_text) > 150 else desc_text
        print(f"  {preview}")

        # Tags
        tags_section = metadata.get('tags', {})
        print(f"\n🏷️  TAGS ({tags_section.get('tag_count', 0)} tags):")
        tags_list = tags_section.get('youtube_tags', [])
        print(f"  {', '.join(tags_list[:15])}...")

        # Hashtags
        hashtags_section = metadata.get('hashtags', {})
        print(f"\n#️⃣  HASHTAGS:")
        print(f"  Instagram: {' '.join(hashtags_section.get('instagram', [])[:5])}...")
        print(f"  TikTok: {' '.join(hashtags_section.get('tiktok', [])[:5])}...")

        overall_score = self.score_metadata(metadata)
        print(f"\n📊 Overall Metadata Score: {overall_score}/10")
        print("\n" + "=" * 80 + "\n")

    def export_metadata(self, metadata, output_file="metadata.json"):
        """Export complete metadata to JSON."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Metadata exported to {output_file}")
        return output_file

    def export_metadata_formatted(self, metadata, output_format="youtube"):
        """
        Export metadata in ready-to-paste format.

        Args:
            metadata: Metadata dict
            output_format: 'youtube', 'tiktok', 'instagram', 'all'

        Returns:
            Formatted strings ready to paste
        """
        outputs = {}

        # YouTube format
        if output_format in ['youtube', 'all']:
            youtube_text = f"""YOUTUBE METADATA
================

Title:
{metadata.get('titles', {}).get('best_title', 'N/A')}

Description:
{metadata.get('description', {}).get('text', 'N/A')}

Tags:
{metadata.get('tags', {}).get('tags_string', 'N/A')}
"""
            outputs['youtube'] = youtube_text

        # TikTok format
        if output_format in ['tiktok', 'all']:
            tiktok_text = f"""TIKTOK CAPTION
==============

{metadata.get('titles', {}).get('best_title', 'N/A')}

{' '.join(metadata.get('hashtags', {}).get('tiktok', []))}
"""
            outputs['tiktok'] = tiktok_text

        # Instagram format
        if output_format in ['instagram', 'all']:
            instagram_text = f"""INSTAGRAM CAPTION
=================

{metadata.get('titles', {}).get('best_title', 'N/A')}

{metadata.get('description', {}).get('text', '')[:200]}...

{' '.join(metadata.get('hashtags', {}).get('instagram', []))}
"""
            outputs['instagram'] = instagram_text

        return outputs

    def export_for_upload(self, metadata, output_dir="metadata_export"):
        """
        Export metadata as separate files ready for YouTube upload.

        Creates:
        - title.txt
        - description.txt
        - tags.txt
        - hashtags.json

        Args:
            metadata: Metadata dict
            output_dir: Directory to save files

        Returns:
            Dict of file paths created
        """
        import os
        os.makedirs(output_dir, exist_ok=True)

        files = {}

        # Title
        title_file = os.path.join(output_dir, 'title.txt')
        with open(title_file, 'w', encoding='utf-8') as f:
            f.write(metadata.get('titles', {}).get('best_title', ''))
        files['title'] = title_file

        # Description
        desc_file = os.path.join(output_dir, 'description.txt')
        with open(desc_file, 'w', encoding='utf-8') as f:
            f.write(metadata.get('description', {}).get('text', ''))
        files['description'] = desc_file

        # Tags
        tags_file = os.path.join(output_dir, 'tags.txt')
        with open(tags_file, 'w', encoding='utf-8') as f:
            f.write(metadata.get('tags', {}).get('tags_string', ''))
        files['tags'] = tags_file

        # Hashtags
        hashtags_file = os.path.join(output_dir, 'hashtags.json')
        with open(hashtags_file, 'w', encoding='utf-8') as f:
            json.dump(metadata.get('hashtags', {}), f, indent=2)
        files['hashtags'] = hashtags_file

        logger.info(f"✓ Metadata exported to {output_dir}")
        return files
