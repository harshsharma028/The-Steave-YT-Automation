"""
Topic Research Module - Find trending topics and score them for potential.
Uses VidIQ to discover what's hot, then ranks by opportunity.
"""

from vidiq_analytics import VidIQAnalytics
from utils import setup_logger

logger = setup_logger("TopicResearch")


class TopicResearcher:
    """Research and score trending topics for video creation."""

    def __init__(self, vidiq_api_key, niche="Technology"):
        """
        Initialize topic researcher.

        Args:
            vidiq_api_key: VidIQ API key
            niche: Content niche (Technology, Business, Health, etc.)
        """
        self.vidiq = VidIQAnalytics(vidiq_api_key)
        self.niche = niche
        logger.info(f"📚 Topic researcher initialized for: {niche}")

    def find_trending_topics(self, limit=10):
        """
        Get trending topics from VidIQ.

        Returns:
            List of trending topics with scores
        """
        logger.info(f"🔍 Finding trending topics in {self.niche}...")
        topics = self.vidiq.get_trending_topics(category=self.niche, limit=limit)
        return topics

    def score_topic_opportunity(self, topic_data):
        """
        Score how good a topic is for creating a video.

        Scoring factors:
        - Trending score (how hot is it)
        - Search volume (how many people search for it)
        - Difficulty (lower = easier to rank)
        - Growth rate (is it growing or dying)

        Returns:
            Opportunity score 0-100
        """
        trending = topic_data.get('trending_score', 0)
        search_volume = topic_data.get('estimated_views', 0)
        growth = topic_data.get('growth_rate', 0)
        difficulty = topic_data.get('difficulty', 50)

        # Convert to normalized scores
        trending_score = min(trending / 100 * 20, 20)  # 0-20 points
        volume_score = min(search_volume / 50000 * 30, 30)  # 0-30 points (normalized)
        growth_score = min(growth * 5, 30)  # 0-30 points (growth multiplier)
        difficulty_score = (100 - difficulty) / 100 * 20  # 0-20 points (lower difficulty = higher score)

        total_score = trending_score + volume_score + growth_score + difficulty_score
        return min(total_score, 100)

    def research_and_rank_topics(self, limit=10):
        """
        Find trending topics, score them, and rank by opportunity.

        Returns:
            Sorted list of topics by opportunity score
        """
        logger.info(f"📊 Researching and ranking {limit} topics...")

        topics = self.find_trending_topics(limit=limit)

        if not topics:
            logger.warning("⚠️  No trending topics found")
            return []

        # Score and rank each topic
        scored_topics = []
        for topic in topics:
            score = self.score_topic_opportunity(topic)
            scored_topics.append({
                **topic,
                'opportunity_score': round(score, 1)
            })

        # Sort by opportunity score
        ranked = sorted(scored_topics, key=lambda x: x['opportunity_score'], reverse=True)

        logger.info(f"✓ Ranked {len(ranked)} topics by opportunity")
        return ranked

    def get_keywords_for_topic(self, topic_title, max_keywords=5):
        """
        Get related keywords for a topic title.

        Args:
            topic_title: The topic/title
            max_keywords: Max keywords to return

        Returns:
            List of keyword research data
        """
        logger.info(f"🔑 Researching keywords for: {topic_title}")

        keywords = []
        # Split topic into potential keywords
        words = topic_title.split()

        for word in words[:max_keywords]:
            if len(word) > 3:  # Skip very short words
                keyword_data = self.vidiq.research_keyword(word)
                if keyword_data:
                    keywords.append(keyword_data)

        logger.info(f"✓ Found {len(keywords)} keywords for topic")
        return keywords

    def select_best_topic(self, min_opportunity_score=60):
        """
        Automatically select the best topic to create a video about.

        Args:
            min_opportunity_score: Minimum score to consider (0-100)

        Returns:
            Best topic dict, or None if no good topics found
        """
        ranked_topics = self.research_and_rank_topics(limit=20)

        if not ranked_topics:
            logger.warning("❌ No topics found")
            return None

        best_topic = ranked_topics[0]

        if best_topic['opportunity_score'] < min_opportunity_score:
            logger.warning(f"⚠️  Best topic score ({best_topic['opportunity_score']}) below minimum ({min_opportunity_score})")
            return None

        logger.info(f"🎯 Best topic selected: {best_topic['title']} (Score: {best_topic['opportunity_score']})")
        return best_topic

    def get_topic_insights(self, topic_title):
        """
        Get detailed insights for a specific topic.

        Returns:
            Dict with title scoring, keywords, and opportunity analysis
        """
        logger.info(f"🔬 Analyzing topic: {topic_title}")

        # Research keywords
        keywords = self.get_keywords_for_topic(topic_title)

        # Get title score suggestions
        main_keyword = keywords[0]['keyword'] if keywords else topic_title
        title_scores = []

        # Generate title variations and score them
        title_variations = [
            f"{topic_title} - Complete Guide",
            f"7 Ways to {topic_title}",
            f"Why {topic_title} Matters in 2025",
            f"The Truth About {topic_title}",
            f"How to Master {topic_title}"
        ]

        for title in title_variations:
            score_result = self.vidiq.score_title(title, main_keyword)
            if score_result:
                title_scores.append({
                    'title': title,
                    'seo_score': score_result.get('score', 0),
                    'ctr_potential': score_result.get('ctr_potential')
                })

        insights = {
            'topic': topic_title,
            'keywords': keywords[:3],  # Top 3 keywords
            'title_suggestions': sorted(title_scores, key=lambda x: x['seo_score'], reverse=True)[:3]
        }

        logger.info(f"✓ Topic insights analyzed")
        return insights

    def print_topic_report(self, topics=None, limit=10):
        """
        Print a formatted report of top topics.

        Args:
            topics: Optional list of topics (will fetch if None)
            limit: Number of topics to show
        """
        if topics is None:
            topics = self.research_and_rank_topics(limit=limit)

        if not topics:
            print("❌ No topics found\n")
            return

        print("\n" + "=" * 80)
        print(f"TOP {len(topics)} TRENDING TOPICS - {self.niche.upper()}")
        print("=" * 80)

        for i, topic in enumerate(topics, 1):
            score = topic.get('opportunity_score', 0)
            trending = topic.get('trending_score', 0)
            views = topic.get('estimated_views', 0)
            growth = topic.get('growth_rate', 0)

            print(f"\n{i}. {topic['title']}")
            print(f"   Opportunity Score: {score}/100")
            print(f"   Trending Score: {trending}/100")
            print(f"   Estimated Views: {views:,}")
            print(f"   Growth Rate: +{growth:.1%}")

        print("\n" + "=" * 80 + "\n")
