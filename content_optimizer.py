"""
Content Optimizer - Use performance data to optimize future content.
Analyzes what works and provides recommendations for improvement.
"""

from utils import setup_logger
import json

logger = setup_logger("ContentOptimizer")


class ContentOptimizer:
    """Optimize content strategy based on performance analytics."""

    def __init__(self):
        """Initialize content optimizer."""
        logger.info(f"🚀 Content optimizer initialized")

    def analyze_title_performance(self, videos):
        """
        Analyze which title patterns perform best.

        Args:
            videos: List of video dicts with title and metrics

        Returns:
            Analysis of title patterns
        """
        logger.info(f"📝 Analyzing title patterns...")

        if not videos:
            return None

        analysis = {
            'total_videos': len(videos),
            'patterns': []
        }

        # Look for common words in high-performing videos
        top_videos = sorted(videos, key=lambda x: x.get('views', 0), reverse=True)[:3]
        bottom_videos = sorted(videos, key=lambda x: x.get('views', 0))[:3]

        # Extract words from titles
        top_words = set()
        for v in top_videos:
            words = v.get('title', '').lower().split()
            top_words.update([w for w in words if len(w) > 3])

        bottom_words = set()
        for v in bottom_videos:
            words = v.get('title', '').lower().split()
            bottom_words.update([w for w in words if len(w) > 3])

        # Find words unique to top videos
        unique_top_words = top_words - bottom_words

        analysis['top_performing_words'] = list(unique_top_words)[:5]
        analysis['words_to_avoid'] = list(bottom_words - top_words)[:5]

        logger.info(f"✓ Identified {len(unique_top_words)} high-performing title patterns")
        return analysis

    def get_content_recommendations(self, videos, analysis=None):
        """
        Get recommendations for future content based on performance.

        Args:
            videos: List of video metrics
            analysis: Optional analysis dict from analytics module

        Returns:
            List of actionable recommendations
        """
        logger.info(f"💡 Generating content recommendations...")

        recommendations = []

        if not videos:
            return recommendations

        # Analyze engagement
        high_engagement = [v for v in videos if v.get('engagement_rate', 0) > 5]
        low_engagement = [v for v in videos if v.get('engagement_rate', 0) < 2]

        if high_engagement:
            rec = {
                'priority': 'HIGH',
                'type': 'engagement',
                'title': 'Create more videos like your top performers',
                'details': f"Your high-engagement videos ({len(high_engagement)}) average {sum(v.get('engagement_rate', 0) for v in high_engagement)/len(high_engagement):.1f}% engagement",
                'action': 'Analyze titles, topics, and hooks of high-engagement videos'
            }
            recommendations.append(rec)

        # Analyze view performance
        high_views = [v for v in videos if v.get('views', 0) > sum(v.get('views', 0) for v in videos) / len(videos)]

        if len(high_views) > 2:
            rec = {
                'priority': 'HIGH',
                'type': 'views',
                'title': 'Replicate your most-viewed content',
                'details': f"Your top {len(high_views)} videos get {len(high_views)*100//len(videos)}% of all views",
                'action': 'Create similar content to your highest-performing videos'
            }
            recommendations.append(rec)

        # Low-performing content
        if low_engagement:
            rec = {
                'priority': 'MEDIUM',
                'type': 'improvement',
                'title': 'Improve low-engagement videos',
                'details': f"{len(low_engagement)} videos have <2% engagement",
                'action': 'Review titles, thumbnails, and hooks of low performers'
            }
            recommendations.append(rec)

        # Upload frequency analysis
        if len(videos) >= 3:
            avg_views = sum(v.get('views', 0) for v in videos) / len(videos)
            rec = {
                'priority': 'MEDIUM',
                'type': 'consistency',
                'title': 'Maintain consistent upload schedule',
                'details': f"Average views per video: {avg_views:,.0f}",
                'action': 'Keep uploading regularly to maintain algorithm visibility'
            }
            recommendations.append(rec)

        logger.info(f"✓ Generated {len(recommendations)} recommendations")
        return recommendations

    def predict_successful_hooks(self, videos):
        """
        Predict which hooks will perform best based on past data.

        Args:
            videos: List of video dicts with title and metrics

        Returns:
            Ranked list of recommended hooks
        """
        logger.info(f"🎯 Predicting successful hooks...")

        hook_scores = {}

        hooks = {
            'how_to': ['how to', 'how', 'tutorial', 'guide'],
            'list': ['7', '5', '10', '15', 'ways', 'tips'],
            'question': ['why', 'what', 'which', 'should', 'is'],
            'superlative': ['best', 'worst', 'top', 'ultimate', 'proven'],
            'curiosity': ['secret', 'revealed', 'truth', 'shocking', 'hidden'],
            'number': ['#1', 'ranking', 'before', 'after']
        }

        top_videos = sorted(videos, key=lambda x: x.get('views', 0), reverse=True)[:5]

        for hook_name, keywords in hooks.items():
            score = 0
            for video in top_videos:
                title = video.get('title', '').lower()
                for keyword in keywords:
                    if keyword in title:
                        score += video.get('views', 0)

            hook_scores[hook_name] = score

        ranked_hooks = sorted(hook_scores.items(), key=lambda x: x[1], reverse=True)

        logger.info(f"✓ Top hook: {ranked_hooks[0][0]}")
        return ranked_hooks

    def get_optimization_score(self, videos, analysis=None):
        """
        Calculate overall optimization score (0-100).

        Factors:
        - View consistency (do videos perform similarly?)
        - Engagement consistency (is engagement predictable?)
        - Growth trend (are views improving?)

        Args:
            videos: List of video metrics
            analysis: Optional analysis dict

        Returns:
            Optimization score 0-100
        """
        logger.info(f"📊 Calculating optimization score...")

        if not videos or len(videos) < 2:
            return 0

        score = 0

        # View consistency (20 points)
        views = [v.get('views', 0) for v in videos]
        if views:
            avg_views = sum(views) / len(views)
            variance = sum((v - avg_views) ** 2 for v in views) / len(views)
            consistency = 1 - min(variance / (avg_views ** 2 + 1), 1)
            score += consistency * 20

        # Engagement consistency (20 points)
        engagements = [v.get('engagement_rate', 0) for v in videos]
        if engagements:
            avg_eng = sum(engagements) / len(engagements)
            if avg_eng > 0:
                eng_consistency = 1 - min(
                    sum((e - avg_eng) ** 2 for e in engagements) / (avg_eng ** 2 + 1) / len(engagements),
                    1
                )
                score += eng_consistency * 20

        # Growth trend (20 points)
        if len(videos) >= 3:
            recent_views = [v.get('views', 0) for v in videos[:3]]
            older_views = [v.get('views', 0) for v in videos[3:]]
            if older_views:
                recent_avg = sum(recent_views) / len(recent_views)
                older_avg = sum(older_views) / len(older_views)
                if older_avg > 0:
                    growth = (recent_avg - older_avg) / older_avg
                    growth_score = min(max(growth * 100, -100), 100) + 100
                    score += (growth_score / 200) * 20

        # Content quality (20 points)
        high_engagement_count = len([v for v in videos if v.get('engagement_rate', 0) > 5])
        quality_score = min((high_engagement_count / len(videos)) * 100, 100)
        score += (quality_score / 100) * 20

        # Content consistency (20 points)
        if len(videos) >= 5:
            score += 15  # Bonus for having enough content

        final_score = round(min(score, 100), 1)
        logger.info(f"✓ Optimization score: {final_score}/100")
        return final_score

    def print_recommendations(self, recommendations):
        """Print formatted recommendations."""
        print("\n" + "=" * 70)
        print("CONTENT OPTIMIZATION RECOMMENDATIONS")
        print("=" * 70)

        if not recommendations:
            print("\n✅ Your content is already well-optimized!\n")
            return

        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. [{rec['priority']}] {rec['title']}")
            print(f"   Type: {rec['type']}")
            print(f"   Details: {rec['details']}")
            print(f"   Action: {rec['action']}")

        print("\n" + "=" * 70 + "\n")

    def export_optimization_report(self, recommendations, hooks, score, output_file='optimization_report.json'):
        """Export optimization report to JSON."""
        report = {
            'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
            'optimization_score': score,
            'recommendations': recommendations,
            'predicted_hooks': hooks,
            'total_recommendations': len(recommendations)
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"✓ Report exported to {output_file}")
        return output_file
