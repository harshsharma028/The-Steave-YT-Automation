"""
Feedback Loop - Complete self-improving system using analytics and optimization.
Closes the loop: Publish → Analyze → Learn → Improve → Repeat
"""

from youtube_analytics import YouTubeAnalytics
from content_optimizer import ContentOptimizer
from analytics_db import AnalyticsDB
from utils import setup_logger
import json
from datetime import datetime

logger = setup_logger("FeedbackLoop")


class FeedbackLoop:
    """Complete feedback loop for self-improving content system."""

    def __init__(self, token_file='youtube_token.pickle'):
        """
        Initialize feedback loop.

        Args:
            token_file: Path to YouTube OAuth token
        """
        self.analytics = YouTubeAnalytics(token_file)
        self.optimizer = ContentOptimizer()
        self.db = AnalyticsDB()
        logger.info(f"🔄 Feedback loop initialized")

    def analyze_and_learn(self):
        """
        Complete cycle: Fetch analytics → Analyze → Extract learnings.

        Returns:
            Dict with full analysis and recommendations
        """
        logger.info(f"🔄 Starting feedback loop analysis...")

        try:
            # Step 1: Fetch latest videos and metrics
            logger.info(f"  1/4 Fetching video analytics...")
            videos = self.analytics.get_latest_videos(limit=20)

            if not videos:
                logger.warning("⚠️  No videos found to analyze")
                return None

            # Step 2: Analyze performance
            logger.info(f"  2/4 Analyzing performance patterns...")
            analysis = self.analytics.analyze_performance_trend(videos)
            patterns = self.analytics.identify_successful_patterns(videos)

            # Step 3: Get optimization recommendations
            logger.info(f"  3/4 Generating recommendations...")
            recommendations = self.optimizer.get_content_recommendations(videos, analysis)
            hooks = self.optimizer.predict_successful_hooks(videos)

            # Step 4: Calculate optimization score
            logger.info(f"  4/4 Calculating overall optimization score...")
            opt_score = self.optimizer.get_optimization_score(videos, analysis)

            result = {
                'timestamp': datetime.utcnow().isoformat(),
                'videos_analyzed': len(videos),
                'analysis': analysis,
                'patterns': patterns,
                'recommendations': recommendations,
                'predicted_hooks': [{'hook': h[0], 'score': h[1]} for h in hooks],
                'optimization_score': opt_score,
                'learnings_extracted': len(recommendations)
            }

            logger.info(f"✓ Analysis complete! Score: {opt_score}/100")
            return result

        except Exception as e:
            logger.error(f"❌ Feedback loop failed: {e}")
            return None

    def store_learnings(self, analysis_result):
        """
        Store extracted learnings in database.

        Args:
            analysis_result: Result from analyze_and_learn()

        Returns:
            List of learning IDs stored
        """
        logger.info(f"💾 Storing learnings in database...")

        if not analysis_result:
            logger.warning("⚠️  No analysis to store")
            return []

        learning_ids = []

        try:
            # Store each recommendation as a learning
            for rec in analysis_result.get('recommendations', []):
                try:
                    learning_id = self.db.add_learning(
                        pattern_type=rec['type'],
                        pattern_description=rec['title'],
                        metric_name='recommendation',
                        average_performance=rec['priority'],
                        videos_tested=analysis_result['videos_analyzed'],
                        confidence_score=0.8
                    )
                    learning_ids.append(learning_id)
                except Exception as e:
                    logger.warning(f"⚠️  Failed to store learning: {e}")

            # Store hook predictions
            for hook_data in analysis_result.get('predicted_hooks', []):
                try:
                    hook_id = self.db.add_learning(
                        pattern_type='hook_effectiveness',
                        pattern_description=f"Hook: {hook_data['hook']}",
                        metric_name='views_per_hook',
                        average_performance=hook_data['score'],
                        videos_tested=analysis_result['videos_analyzed'],
                        confidence_score=0.75
                    )
                    learning_ids.append(hook_id)
                except Exception as e:
                    logger.warning(f"⚠️  Failed to store hook learning: {e}")

            logger.info(f"✓ Stored {len(learning_ids)} learnings in database")
            return learning_ids

        except Exception as e:
            logger.error(f"❌ Failed to store learnings: {e}")
            return []

    def apply_learnings_to_future_content(self):
        """
        Retrieve stored learnings and apply to future content strategy.

        Returns:
            Dict with content strategy recommendations
        """
        logger.info(f"🎯 Applying learnings to future content strategy...")

        try:
            # Get active learnings from database
            learnings = self.db.get_active_learnings()

            if not learnings:
                logger.warning("⚠️  No learnings stored yet")
                return None

            strategy = {
                'total_learnings': len(learnings),
                'hook_strategies': [],
                'topic_strategies': [],
                'metadata_strategies': [],
                'thumbnail_strategies': [],
                'timestamp': datetime.utcnow().isoformat()
            }

            for learning in learnings:
                pattern_type = learning.get('pattern_type', '')

                if 'hook' in pattern_type:
                    strategy['hook_strategies'].append({
                        'description': learning.get('pattern_description'),
                        'confidence': learning.get('confidence_score')
                    })
                elif 'topic' in pattern_type:
                    strategy['topic_strategies'].append({
                        'description': learning.get('pattern_description'),
                        'confidence': learning.get('confidence_score')
                    })
                elif 'metadata' in pattern_type:
                    strategy['metadata_strategies'].append({
                        'description': learning.get('pattern_description'),
                        'confidence': learning.get('confidence_score')
                    })
                elif 'thumbnail' in pattern_type:
                    strategy['thumbnail_strategies'].append({
                        'description': learning.get('pattern_description'),
                        'confidence': learning.get('confidence_score')
                    })

            logger.info(f"✓ Applied {len(learnings)} learnings to content strategy")
            return strategy

        except Exception as e:
            logger.error(f"❌ Failed to apply learnings: {e}")
            return None

    def run_complete_feedback_loop(self):
        """
        Execute complete feedback loop: Analyze → Learn → Apply.

        Returns:
            Complete feedback loop result
        """
        logger.info(f"🔄 Running complete feedback loop...")

        # Step 1: Analyze
        analysis = self.analyze_and_learn()
        if not analysis:
            return None

        # Step 2: Learn
        learning_ids = self.store_learnings(analysis)

        # Step 3: Apply
        strategy = self.apply_learnings_to_future_content()

        result = {
            'cycle_timestamp': datetime.utcnow().isoformat(),
            'analysis': analysis,
            'learnings_stored': len(learning_ids),
            'strategy_applied': strategy,
            'optimization_score': analysis.get('optimization_score'),
            'status': 'complete'
        }

        logger.info(f"✅ Feedback loop complete!")
        return result

    def print_feedback_report(self, result):
        """Print formatted feedback loop report."""
        print("\n" + "=" * 70)
        print("FEEDBACK LOOP REPORT")
        print("=" * 70)

        if not result:
            print("\n❌ No analysis results\n")
            return

        print(f"\n📊 Analysis Results:")
        print(f"   Videos Analyzed: {result['analysis'].get('total_videos')}")
        print(f"   Total Views: {result['analysis'].get('total_views', 0):,}")
        print(f"   Avg Views/Video: {result['analysis'].get('avg_views_per_video', 0):,.0f}")
        print(f"   Avg Engagement: {result['analysis'].get('avg_engagement_rate', 0)}%")

        print(f"\n💡 Recommendations Generated: {result['analysis'].get('learnings_extracted', 0)}")

        print(f"\n📈 Optimization Score: {result['optimization_score']}/100")

        print(f"\n💾 Learnings Stored: {result['learnings_stored']}")

        if result.get('strategy_applied'):
            strategy = result['strategy_applied']
            print(f"\n🎯 Strategy Applied:")
            if strategy.get('hook_strategies'):
                print(f"   Hook Strategies: {len(strategy['hook_strategies'])}")
            if strategy.get('topic_strategies'):
                print(f"   Topic Strategies: {len(strategy['topic_strategies'])}")

        print("\n" + "=" * 70 + "\n")

    def export_feedback_report(self, result, output_file='feedback_report.json'):
        """Export feedback loop report to JSON."""
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)

        logger.info(f"✓ Report exported to {output_file}")
        return output_file

    def schedule_feedback_loop(self, interval_hours=24):
        """
        Schedule feedback loop to run periodically.

        Args:
            interval_hours: Run feedback loop every N hours

        Returns:
            Schedule info
        """
        logger.info(f"📅 Scheduling feedback loop every {interval_hours} hours...")

        schedule = {
            'interval_hours': interval_hours,
            'purpose': 'Continuously analyze performance and improve content',
            'recommended': 'Run daily (24 hours) for consistent learning'
        }

        logger.info(f"ℹ️  To implement: Use APScheduler or similar task scheduler")
        return schedule
