"""
Script Generation Engine - Create compelling video scripts from topics.
Uses Claude/Gemini to generate variations with hooks, structure, and CTAs.
"""

import json
import re
from google import genai
from config import TEXT_MODEL, CHAT_API_KEY
from utils import setup_logger

logger = setup_logger("ScriptGenerator")


class ScriptGenerator:
    """Generate video scripts using Claude/Gemini with multiple variations."""

    HOOKS = {
        "curiosity": "Start with an intriguing question or statement that makes viewers want to know more",
        "storytelling": "Open with a relatable personal story or anecdote",
        "statistic": "Lead with a surprising stat or fact",
        "problem": "Immediately identify a pain point the audience faces",
        "promise": "State a clear benefit or transformation the video will provide",
        "bold": "Make a controversial or bold claim to trigger discussion"
    }

    def __init__(self, api_key=None):
        """Initialize script generator with Gemini API."""
        self.client = genai.Client(api_key=api_key or CHAT_API_KEY)
        self.model = TEXT_MODEL
        logger.info(f"✍️  Script generator initialized with {self.model}")

    def generate_script(self, topic, hook_type="curiosity", video_length_seconds=300, detailed=False):
        """
        Generate a single script for a topic.

        Args:
            topic: Topic title or description
            hook_type: Type of hook (curiosity, storytelling, statistic, problem, promise, bold)
            video_length_seconds: Target video length
            detailed: If True, return detailed structure with sections

        Returns:
            Dict with script_text, hook_used, word_count, structure
        """
        logger.info(f"✍️  Generating script for: {topic} (hook: {hook_type})")

        if hook_type not in self.HOOKS:
            logger.warning(f"⚠️  Unknown hook type '{hook_type}', using 'curiosity'")
            hook_type = "curiosity"

        hook_description = self.HOOKS[hook_type]
        word_count_estimate = int(video_length_seconds * 2.5)  # ~2.5 words/sec

        prompt = self._build_script_prompt(
            topic=topic,
            hook_type=hook_type,
            hook_description=hook_description,
            word_count_estimate=word_count_estimate,
            detailed=detailed
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40
                )
            )

            script_text = response.text.strip()

            # Parse structure if requested
            structure = self._extract_structure(script_text) if detailed else None

            result = {
                'script_text': script_text,
                'hook_type': hook_type,
                'topic': topic,
                'word_count': len(script_text.split()),
                'target_length_seconds': video_length_seconds,
                'structure': structure
            }

            logger.info(f"✓ Script generated ({result['word_count']} words)")
            return result

        except Exception as e:
            logger.error(f"❌ Script generation failed: {e}")
            raise

    def generate_variations(self, topic, num_variations=3, video_length_seconds=300):
        """
        Generate multiple script variations with different hooks.

        Args:
            topic: Topic to create variations for
            num_variations: Number of variations to generate (1-6, one per hook type)
            video_length_seconds: Target video length

        Returns:
            List of script dicts, sorted by estimated quality
        """
        logger.info(f"🔄 Generating {num_variations} script variations...")

        hook_types = list(self.HOOKS.keys())[:num_variations]
        variations = []

        for hook_type in hook_types:
            try:
                script = self.generate_script(
                    topic=topic,
                    hook_type=hook_type,
                    video_length_seconds=video_length_seconds
                )
                variations.append(script)
            except Exception as e:
                logger.warning(f"⚠️  Failed to generate {hook_type} variation: {e}")
                continue

        logger.info(f"✓ Generated {len(variations)} variations")
        return variations

    def score_script(self, script_dict):
        """
        Score a script for quality and engagement potential.

        Scoring factors:
        - Hook strength (does it grab attention)
        - Structure (intro, body, conclusion present)
        - CTAs (clear calls-to-action)
        - Word count appropriateness
        - Readability (sentence variety)

        Returns:
            Quality score 0-10
        """
        script = script_dict['script_text']
        word_count = len(script.split())
        target_length = script_dict.get('target_length_seconds', 300) * 2.5

        score = 0

        # Hook strength (2 points)
        if len(script.split()) > 20:
            first_sentence = script.split('.')[0]
            if any(w in first_sentence.lower() for w in ['what', 'why', 'how', 'did you', 'imagine', 'picture']):
                score += 2
            else:
                score += 1
        else:
            score += 0.5

        # Structure (2 points) - check for common transitions
        transitions = ['first', 'next', 'finally', 'therefore', 'in conclusion']
        transition_count = sum(1 for t in transitions if t in script.lower())
        score += min(2, transition_count * 0.4)

        # CTAs (2 points) - check for calls to action
        ctas = ['subscribe', 'like', 'click', 'comment', 'follow', 'check', 'visit']
        cta_count = sum(1 for c in ctas if c in script.lower())
        score += min(2, cta_count * 0.5)

        # Word count appropriateness (2 points)
        if abs(word_count - target_length) < target_length * 0.2:
            score += 2
        elif abs(word_count - target_length) < target_length * 0.4:
            score += 1
        else:
            score += 0

        # Readability (2 points) - sentence variety
        sentences = [s.strip() for s in script.split('.') if s.strip()]
        if len(sentences) > 0:
            avg_sentence_length = word_count / len(sentences)
            if 10 < avg_sentence_length < 25:  # Ideal range
                score += 2
            elif 8 < avg_sentence_length < 30:
                score += 1
            else:
                score += 0
        else:
            score += 0

        final_score = round(min(10, score), 1)
        return final_score

    def score_variations(self, variations):
        """
        Score all variations and return sorted by quality.

        Returns:
            Sorted list of variations (highest score first)
        """
        scored = []
        for v in variations:
            score = self.score_script(v)
            scored.append({**v, 'quality_score': score})

        sorted_vars = sorted(scored, key=lambda x: x['quality_score'], reverse=True)
        logger.info(f"✓ Scored {len(sorted_vars)} variations")

        for i, v in enumerate(sorted_vars, 1):
            logger.info(f"  {i}. {v['hook_type'].title()}: {v['quality_score']}/10")

        return sorted_vars

    def _build_script_prompt(self, topic, hook_type, hook_description, word_count_estimate, detailed=False):
        """Build the prompt for script generation."""

        if detailed:
            structure_instruction = """
Structure the script with clear sections:
1. HOOK: (attention-grabbing opening)
2. INTRO: (introduce the topic)
3. MAIN BODY: (3-5 key points)
4. EVIDENCE/EXAMPLES: (proof or stories)
5. CALL-TO-ACTION: (what should viewers do)
6. CONCLUSION: (wrap up the message)

Format each section with [SECTION_NAME] headers."""
        else:
            structure_instruction = "Write a natural, flowing script without section headers."

        prompt = f"""You are an expert YouTube script writer. Create a compelling, engaging video script.

Topic: {topic}
Video Length: ~{word_count_estimate} words (~{int(word_count_estimate/2.5)} seconds)
Hook Type: {hook_type}
Hook Direction: {hook_description}

Requirements:
- {hook_description}
- Make it engaging and easy to read (for narration)
- Include specific examples or references
- Add a clear call-to-action (subscribe, like, comment, etc.)
- Keep sentences conversational (short and varied)
- NO timestamps or chapter markers
- NO brackets like [scene] or [effect] descriptions
- Pure script text that can be read aloud

{structure_instruction}

Generate ONLY the script. No meta-commentary, no explanations."""

        return prompt

    def _extract_structure(self, script_text):
        """Extract structural sections from script if present."""
        structure = {}
        current_section = "content"
        current_text = []

        for line in script_text.split('\n'):
            if line.startswith('[') and line.endswith(']'):
                if current_text and current_section:
                    structure[current_section] = '\n'.join(current_text).strip()
                current_section = line.strip('[]').lower()
                current_text = []
            else:
                current_text.append(line)

        if current_text and current_section:
            structure[current_section] = '\n'.join(current_text).strip()

        return structure if structure else {'content': script_text}

    def print_script_report(self, variations, topic=None):
        """Print formatted report of generated scripts."""
        print("\n" + "=" * 80)
        print(f"SCRIPT GENERATION REPORT")
        if topic:
            print(f"Topic: {topic}")
        print("=" * 80)

        for i, script in enumerate(variations, 1):
            print(f"\n{i}. {script['hook_type'].upper()} HOOK - Score: {script.get('quality_score', '?')}/10")
            print(f"   Word count: {script['word_count']}")
            print(f"   Length: ~{int(script['word_count'] / 2.5)} seconds")
            print(f"\n   {script['script_text'][:200]}...")

        print("\n" + "=" * 80 + "\n")

    def export_scripts(self, variations, output_file="scripts.json"):
        """Export generated scripts to JSON file."""
        export_data = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'scripts': variations,
            'total_scripts': len(variations),
            'best_script': variations[0] if variations else None
        }

        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"✓ Scripts exported to {output_file}")
        return output_file
