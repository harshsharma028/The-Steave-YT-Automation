"""
Script Validation & Quality Assessment - Verify scripts meet quality standards.
Checks for engagement, structure, timing, and SEO readiness.
"""

import re
from utils import setup_logger

logger = setup_logger("ScriptValidator")


class ScriptValidator:
    """Validate and assess script quality."""

    # Common words that weaken content
    WEAK_WORDS = ['basically', 'actually', 'just', 'really', 'very', 'sort of', 'kind of']

    # Words that signal strong CTAs
    CTA_WORDS = ['subscribe', 'like', 'comment', 'click', 'follow', 'watch', 'check', 'visit', 'share']

    # Words that signal emotional engagement
    ENGAGEMENT_WORDS = ['amazing', 'incredible', 'beautiful', 'powerful', 'awesome', 'shocking', 'surprising']

    def validate_script(self, script_dict):
        """
        Comprehensive validation of a script.

        Returns:
            {
                'is_valid': bool,
                'issues': [],
                'warnings': [],
                'metrics': {}
            }
        """
        script = script_dict.get('script_text', '')
        target_length = script_dict.get('target_length_seconds', 300)

        issues = []
        warnings = []
        metrics = {}

        # Check 1: Length appropriateness
        word_count = len(script.split())
        target_words = target_length * 2.5
        metrics['word_count'] = word_count

        if word_count < target_words * 0.7:
            warnings.append(f"Script is short: {word_count} words (target: ~{int(target_words)})")
        elif word_count > target_words * 1.3:
            warnings.append(f"Script is long: {word_count} words (target: ~{int(target_words)})")

        # Check 2: Structure
        sentences = [s.strip() for s in script.split('.') if s.strip()]
        metrics['sentence_count'] = len(sentences)

        if len(sentences) < 3:
            issues.append("Script needs more sentences for natural pacing")

        # Check 3: Hook strength
        first_50_chars = script[:50].lower()
        has_hook = any(word in first_50_chars for word in ['what', 'why', 'how', 'did you', 'imagine', 'picture', 'wait', 'stop', 'believe'])
        metrics['has_hook'] = has_hook

        if not has_hook:
            warnings.append("Opening doesn't use typical hook patterns - may lose viewers early")

        # Check 4: CTA presence
        cta_count = sum(1 for cta in self.CTA_WORDS if cta in script.lower())
        metrics['cta_count'] = cta_count

        if cta_count == 0:
            issues.append("No call-to-action found - add 'subscribe', 'like', 'comment', etc.")
        elif cta_count == 1:
            warnings.append("Only one CTA found - consider adding more throughout the script")

        # Check 5: Engagement words
        engagement_count = sum(1 for word in self.ENGAGEMENT_WORDS if word in script.lower())
        metrics['engagement_word_count'] = engagement_count
        avg_engagement_per_100_words = (engagement_count / max(1, word_count)) * 100

        if avg_engagement_per_100_words < 1:
            warnings.append("Low emotional engagement - add more powerful/descriptive words")

        # Check 6: Weak words density
        weak_count = sum(script.lower().count(w) for w in self.WEAK_WORDS)
        metrics['weak_word_count'] = weak_count

        if weak_count > word_count * 0.05:  # More than 5%
            warnings.append(f"High weak word density ({weak_count} instances) - remove 'just', 'really', etc.")

        # Check 7: Readability - Average sentence length
        if len(sentences) > 0:
            avg_sentence_length = word_count / len(sentences)
            metrics['avg_sentence_length'] = round(avg_sentence_length, 1)

            if avg_sentence_length < 8:
                warnings.append("Sentences are very short - may sound choppy when read")
            elif avg_sentence_length > 30:
                warnings.append("Sentences are very long - may be hard to follow")
        else:
            metrics['avg_sentence_length'] = 0

        # Check 8: Question usage (good for engagement)
        question_count = script.count('?')
        metrics['question_count'] = question_count

        if question_count == 0:
            warnings.append("No questions asked - consider adding rhetorical questions for engagement")

        # Check 9: Repetition check (repeated words)
        words = [w.lower() for w in re.findall(r'\b\w+\b', script)]
        from collections import Counter
        word_counts = Counter(words)
        repeated_words = {word: count for word, count in word_counts.items() if count > 5 and len(word) > 4}

        if repeated_words:
            warnings.append(f"Repeated words found: {', '.join(repeated_words.keys())}")

        metrics['repeated_words'] = repeated_words

        # Check 10: Format issues
        if '  ' in script:  # Double spaces
            warnings.append("Double spaces found - clean up formatting")

        if script.startswith(' ') or script.endswith(' '):
            warnings.append("Extra whitespace at start/end")

        # Determine validity
        is_valid = len(issues) == 0

        result = {
            'is_valid': is_valid,
            'issues': issues,
            'warnings': warnings,
            'metrics': metrics,
            'status': 'PASS' if is_valid else 'FAIL'
        }

        return result

    def print_validation_report(self, validation_result):
        """Print formatted validation report."""
        status = validation_result['status']
        status_emoji = '✅' if validation_result['is_valid'] else '❌'

        print(f"\n{status_emoji} Validation Status: {status}")

        if validation_result['issues']:
            print("\n⚠️  ISSUES (must fix):")
            for issue in validation_result['issues']:
                print(f"  • {issue}")

        if validation_result['warnings']:
            print("\n⚡ WARNINGS (recommended):")
            for warning in validation_result['warnings']:
                print(f"  • {warning}")

        metrics = validation_result['metrics']
        print("\n📊 Metrics:")
        print(f"  • Word count: {metrics.get('word_count', 0)}")
        print(f"  • Sentences: {metrics.get('sentence_count', 0)}")
        print(f"  • Avg sentence length: {metrics.get('avg_sentence_length', 0)}")
        print(f"  • CTAs: {metrics.get('cta_count', 0)}")
        print(f"  • Engagement words: {metrics.get('engagement_word_count', 0)}")
        print(f"  • Weak words: {metrics.get('weak_word_count', 0)}")
        print(f"  • Questions: {metrics.get('question_count', 0)}")
        print(f"  • Has hook: {'✓' if metrics.get('has_hook') else '✗'}")

        if metrics.get('repeated_words'):
            print(f"  • Repeated words: {list(metrics['repeated_words'].keys())[:3]}")

        print()

    def suggest_improvements(self, script_dict, validation_result):
        """Suggest specific improvements for the script."""
        script = script_dict['script_text']
        suggestions = []

        # Suggestion 1: Add hook if missing
        if not validation_result['metrics'].get('has_hook'):
            suggestions.append({
                'type': 'hook',
                'title': 'Add a stronger hook',
                'example': "Start with: 'Wait, before you scroll past this...'",
                'priority': 'HIGH'
            })

        # Suggestion 2: Strengthen CTAs
        if validation_result['metrics'].get('cta_count', 0) < 2:
            suggestions.append({
                'type': 'cta',
                'title': 'Add more calls-to-action',
                'example': "Add: 'If you found this helpful, please like and subscribe'",
                'priority': 'HIGH'
            })

        # Suggestion 3: Reduce weak words
        if validation_result['metrics'].get('weak_word_count', 0) > 5:
            suggestions.append({
                'type': 'weak_words',
                'title': 'Remove weak filler words',
                'example': "Replace 'I just really think...' with 'I believe...'",
                'priority': 'MEDIUM'
            })

        # Suggestion 4: Add questions
        if validation_result['metrics'].get('question_count', 0) == 0:
            suggestions.append({
                'type': 'questions',
                'title': 'Add rhetorical questions',
                'example': "Add: 'Have you ever wondered why...?'",
                'priority': 'MEDIUM'
            })

        # Suggestion 5: Improve engagement words
        if validation_result['metrics'].get('engagement_word_count', 0) < 2:
            suggestions.append({
                'type': 'engagement',
                'title': 'Use more powerful descriptive words',
                'example': "Instead of 'good', use 'incredible', 'amazing', 'powerful'",
                'priority': 'LOW'
            })

        return suggestions

    def print_suggestions(self, suggestions):
        """Print improvement suggestions."""
        if not suggestions:
            print("✅ No suggestions - script looks great!")
            return

        print("\n💡 IMPROVEMENT SUGGESTIONS:\n")

        high_priority = [s for s in suggestions if s['priority'] == 'HIGH']
        medium_priority = [s for s in suggestions if s['priority'] == 'MEDIUM']
        low_priority = [s for s in suggestions if s['priority'] == 'LOW']

        if high_priority:
            print("🔴 HIGH Priority:")
            for s in high_priority:
                print(f"  • {s['title']}")
                print(f"    Example: {s['example']}\n")

        if medium_priority:
            print("🟡 MEDIUM Priority:")
            for s in medium_priority:
                print(f"  • {s['title']}")
                print(f"    Example: {s['example']}\n")

        if low_priority:
            print("🟢 LOW Priority:")
            for s in low_priority:
                print(f"  • {s['title']}")
                print(f"    Example: {s['example']}\n")

    def validate_batch(self, script_dicts):
        """Validate multiple scripts at once."""
        results = []
        for script in script_dicts:
            validation = self.validate_script(script)
            results.append({
                **script,
                'validation': validation
            })

        logger.info(f"✓ Validated {len(results)} scripts")
        return results

    def get_valid_scripts(self, validated_scripts):
        """Filter and return only valid scripts."""
        valid = [s for s in validated_scripts if s['validation']['is_valid']]
        logger.info(f"✓ {len(valid)} out of {len(validated_scripts)} scripts passed validation")
        return valid
