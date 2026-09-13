"""
Analytics Database - SQLite schema for tracking video performance and learnings.
Stores topics, videos, analytics, and patterns learned over time.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from utils import setup_logger

logger = setup_logger("AnalyticsDB")

DB_FILE = 'channel_analytics.db'


class AnalyticsDB:
    """SQLite database for channel analytics and performance tracking."""

    def __init__(self, db_path=DB_FILE):
        """Initialize database and create tables if needed."""
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Topics table - trending topics researched
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                niche TEXT,
                trending_score REAL,
                search_volume INTEGER,
                competition TEXT,
                difficulty REAL,
                research_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'research'
            )
        ''')

        # Scripts table - generated scripts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER,
                script_text TEXT NOT NULL,
                quality_score REAL,
                hook_type TEXT,
                estimated_length_seconds INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'draft',
                FOREIGN KEY(topic_id) REFERENCES topics(id)
            )
        ''')

        # Videos table - published videos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                youtube_id TEXT UNIQUE NOT NULL,
                script_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                tags TEXT,
                thumbnail_path TEXT,
                video_file_path TEXT,
                upload_date TIMESTAMP,
                publish_date TIMESTAMP,
                video_length_seconds INTEGER,
                FOREIGN KEY(script_id) REFERENCES scripts(id)
            )
        ''')

        # Analytics table - performance metrics (updated daily)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER,
                measurement_date TIMESTAMP,
                views INTEGER DEFAULT 0,
                watch_time_hours REAL DEFAULT 0,
                average_view_duration_seconds REAL DEFAULT 0,
                ctr_percent REAL DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0,
                FOREIGN KEY(video_id) REFERENCES videos(id),
                UNIQUE(video_id, measurement_date)
            )
        ''')

        # Learnings table - patterns discovered
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_description TEXT,
                metric_name TEXT,
                average_performance REAL,
                videos_tested INTEGER,
                confidence_score REAL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        ''')

        # Video performance ratings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER,
                rating_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                overall_score REAL,
                view_score REAL,
                engagement_score REAL,
                retention_score REAL,
                FOREIGN KEY(video_id) REFERENCES videos(id)
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("✓ Analytics database initialized")

    def add_topic(self, title, niche, trending_score, search_volume, competition, difficulty):
        """Add researched topic to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO topics (title, niche, trending_score, search_volume, competition, difficulty)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, niche, trending_score, search_volume, competition, difficulty))
            conn.commit()
            topic_id = cursor.lastrowid
            logger.info(f"✓ Topic added: {title} (ID: {topic_id})")
            return topic_id
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️  Topic already exists: {title}")
            return None
        finally:
            conn.close()

    def add_script(self, topic_id, script_text, quality_score, hook_type, length_seconds):
        """Add generated script to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO scripts (topic_id, script_text, quality_score, hook_type, estimated_length_seconds)
            VALUES (?, ?, ?, ?, ?)
        ''', (topic_id, script_text, quality_score, hook_type, length_seconds))
        conn.commit()
        script_id = cursor.lastrowid
        conn.close()

        logger.info(f"✓ Script added (ID: {script_id}, Quality: {quality_score}/10)")
        return script_id

    def add_video(self, youtube_id, script_id, title, description, tags, thumbnail_path,
                  video_file_path, publish_date, video_length_seconds):
        """Add published video to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO videos (youtube_id, script_id, title, description, tags,
                              thumbnail_path, video_file_path, upload_date, publish_date, video_length_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (youtube_id, script_id, title, description, json.dumps(tags),
              thumbnail_path, video_file_path, datetime.now(), publish_date, video_length_seconds))
        conn.commit()
        video_id = cursor.lastrowid
        conn.close()

        logger.info(f"✓ Video published: {youtube_id}")
        return video_id

    def update_analytics(self, youtube_id, views, watch_time_hours, avg_view_duration,
                        ctr, likes, comments, shares):
        """Update video analytics metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get video_id from youtube_id
        cursor.execute('SELECT id FROM videos WHERE youtube_id = ?', (youtube_id,))
        result = cursor.fetchone()

        if not result:
            logger.error(f"❌ Video not found: {youtube_id}")
            conn.close()
            return

        video_id = result[0]
        engagement_rate = ((likes + comments + shares) / max(views, 1)) * 100

        cursor.execute('''
            INSERT INTO analytics
            (video_id, measurement_date, views, watch_time_hours, average_view_duration_seconds,
             ctr_percent, likes, comments, shares, engagement_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (video_id, datetime.now(), views, watch_time_hours, avg_view_duration,
              ctr, likes, comments, shares, engagement_rate))
        conn.commit()
        conn.close()

        logger.info(f"📊 Analytics updated: {youtube_id} - {views} views, {engagement_rate:.2f}% engagement")

    def add_learning(self, pattern_type, description, metric_name, avg_performance, videos_tested, confidence):
        """Record a pattern learned from video data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO learnings (pattern_type, pattern_description, metric_name,
                                 average_performance, videos_tested, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (pattern_type, description, metric_name, avg_performance, videos_tested, confidence))
        conn.commit()
        conn.close()

        logger.info(f"💡 Learning recorded: {description} (Confidence: {confidence:.1%})")

    def get_active_learnings(self):
        """Get all active learnings to apply to future content."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT pattern_description, metric_name, average_performance, confidence_score
            FROM learnings
            WHERE is_active = 1
            ORDER BY confidence_score DESC
        ''')

        learnings = [dict(row) for row in cursor.fetchall()]
        conn.close()

        logger.info(f"📚 Found {len(learnings)} active learnings")
        return learnings

    def get_video_performance(self, youtube_id):
        """Get all analytics for a video."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT v.title, v.publish_date, a.views, a.watch_time_hours,
                   a.average_view_duration_seconds, a.ctr_percent, a.engagement_rate
            FROM videos v
            LEFT JOIN analytics a ON v.id = a.video_id
            WHERE v.youtube_id = ?
            ORDER BY a.measurement_date DESC
        ''', (youtube_id,))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

    def get_channel_statistics(self):
        """Get overall channel statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total videos
        cursor.execute('SELECT COUNT(*) FROM videos')
        total_videos = cursor.fetchone()[0]

        # Total views
        cursor.execute('SELECT COALESCE(SUM(views), 0) FROM analytics')
        total_views = cursor.fetchone()[0]

        # Average watch time
        cursor.execute('SELECT COALESCE(AVG(watch_time_hours), 0) FROM analytics')
        avg_watch_time = cursor.fetchone()[0]

        # Average engagement
        cursor.execute('SELECT COALESCE(AVG(engagement_rate), 0) FROM analytics')
        avg_engagement = cursor.fetchone()[0]

        conn.close()

        stats = {
            'total_videos': total_videos,
            'total_views': int(total_views),
            'avg_watch_time_hours': round(avg_watch_time, 2),
            'avg_engagement_rate': round(avg_engagement, 2)
        }

        logger.info(f"📊 Channel Stats: {total_videos} videos, {int(total_views)} views")
        return stats

    def export_report(self, output_file='channel_report.json'):
        """Export full analytics report to JSON."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        report = {}

        # Channel statistics
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM analytics ORDER BY measurement_date DESC LIMIT 10')
        report['recent_analytics'] = [dict(row) for row in cursor.fetchall()]

        # Learnings
        cursor.execute('SELECT * FROM learnings WHERE is_active = 1 ORDER BY confidence_score DESC')
        report['learnings'] = [dict(row) for row in cursor.fetchall()]

        # Video performance
        cursor.execute('''
            SELECT v.youtube_id, v.title, COUNT(a.id) as data_points,
                   MAX(a.views) as latest_views, MAX(a.engagement_rate) as latest_engagement
            FROM videos v
            LEFT JOIN analytics a ON v.id = a.video_id
            GROUP BY v.id
            ORDER BY v.upload_date DESC
        ''')
        report['videos'] = [dict(row) for row in cursor.fetchall()]

        conn.close()

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"✓ Report exported: {output_file}")
        return output_file
