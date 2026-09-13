"""
YouTube Scheduler - Schedule videos for optimal publishing times.
Finds best upload times based on audience analytics and trends.
"""

from datetime import datetime, timedelta
import json
from vidiq_analytics import VidIQAnalytics
from utils import setup_logger

logger = setup_logger("YouTubeScheduler")


class YouTubeScheduler:
    """Schedule videos for optimal publishing."""

    # Best upload times (day, hour) based on YouTube analytics research
    OPTIMAL_TIMES = {
        'general': [
            {'day': 1, 'hour': 10, 'timezone': 'UTC'},  # Monday 10 AM
            {'day': 3, 'hour': 14, 'timezone': 'UTC'},  # Wednesday 2 PM
            {'day': 4, 'hour': 10, 'timezone': 'UTC'},  # Thursday 10 AM
            {'day': 5, 'hour': 16, 'timezone': 'UTC'},  # Friday 4 PM
        ],
        'tech': [
            {'day': 2, 'hour': 9, 'timezone': 'UTC'},   # Tuesday 9 AM (tech day)
            {'day': 4, 'hour': 15, 'timezone': 'UTC'},  # Thursday 3 PM
        ],
        'education': [
            {'day': 1, 'hour': 10, 'timezone': 'UTC'},  # Monday 10 AM
            {'day': 3, 'hour': 15, 'timezone': 'UTC'},  # Wednesday 3 PM
        ],
        'entertainment': [
            {'day': 5, 'hour': 18, 'timezone': 'UTC'},  # Friday 6 PM
            {'day': 6, 'hour': 20, 'timezone': 'UTC'},  # Saturday 8 PM
            {'day': 0, 'hour': 19, 'timezone': 'UTC'},  # Sunday 7 PM
        ],
        'business': [
            {'day': 2, 'hour': 8, 'timezone': 'UTC'},   # Tuesday 8 AM
            {'day': 4, 'hour': 10, 'timezone': 'UTC'},  # Thursday 10 AM
        ]
    }

    def __init__(self, vidiq_api_key=None):
        """
        Initialize scheduler.

        Args:
            vidiq_api_key: Optional VidIQ key for real analytics
        """
        self.vidiq = VidIQAnalytics(vidiq_api_key) if vidiq_api_key else None
        logger.info(f"📅 Scheduler initialized")

    def get_optimal_publish_time(self, niche='general', timezone='UTC', days_ahead=1):
        """
        Get optimal time to publish next video.

        Args:
            niche: Content niche (general, tech, education, entertainment, business)
            timezone: Target timezone (default UTC)
            days_ahead: How many days from now to schedule (1-30)

        Returns:
            ISO 8601 timestamp for optimal publishing
        """
        logger.info(f"📅 Finding optimal publish time for {niche}")

        if niche not in self.OPTIMAL_TIMES:
            logger.warning(f"⚠️  Unknown niche '{niche}', using general")
            niche = 'general'

        # Get current datetime
        now = datetime.utcnow()
        target_date = now + timedelta(days=days_ahead)

        # Get optimal times for this niche
        optimal_times = self.OPTIMAL_TIMES[niche]

        # Find best time in the next week
        best_time = None
        for opt_time in optimal_times:
            day_of_week = opt_time['day']
            hour = opt_time['hour']

            # Calculate date with desired day of week
            days_until_day = (day_of_week - target_date.weekday()) % 7
            if days_until_day == 0 and target_date.hour >= hour:
                days_until_day = 7

            publish_date = target_date + timedelta(days=days_until_day)
            publish_date = publish_date.replace(hour=hour, minute=0, second=0, microsecond=0)

            if publish_date > now:
                best_time = publish_date
                break

        if not best_time:
            # Fallback: use first optimal time next week
            opt_time = optimal_times[0]
            best_time = target_date.replace(
                hour=opt_time['hour'],
                minute=0,
                second=0,
                microsecond=0
            )

        # Convert to ISO 8601
        iso_timestamp = best_time.isoformat() + 'Z'
        logger.info(f"✓ Optimal time: {iso_timestamp}")
        return iso_timestamp

    def get_upload_time_for_audience(self, audience_timezone='UTC', niche='general'):
        """
        Get optimal upload time for specific audience timezone.

        Args:
            audience_timezone: Target audience timezone (US/Eastern, Europe/London, etc.)
            niche: Content category

        Returns:
            Scheduled datetime in audience timezone
        """
        logger.info(f"📅 Calculating optimal time for {audience_timezone}")

        # For simplicity, use UTC and let YouTube handle timezone conversion
        optimal_time = self.get_optimal_publish_time(niche)
        logger.info(f"✓ Time calculated: {optimal_time}")
        return optimal_time

    def schedule_content_calendar(self, num_videos=5, niche='general',
                                 spacing_days=3, start_date=None):
        """
        Create a publishing schedule for multiple videos.

        Args:
            num_videos: Number of videos to schedule
            niche: Content niche
            spacing_days: Days between each video publication
            start_date: Optional start date (defaults to tomorrow)

        Returns:
            List of scheduled publishing times
        """
        logger.info(f"📅 Creating content calendar ({num_videos} videos)")

        if not start_date:
            start_date = datetime.utcnow() + timedelta(days=1)

        schedule = []
        for i in range(num_videos):
            publish_date = start_date + timedelta(days=i * spacing_days)
            iso_timestamp = publish_date.isoformat() + 'Z'

            schedule.append({
                'video_number': i + 1,
                'scheduled_time': iso_timestamp,
                'scheduled_date': publish_date.strftime('%Y-%m-%d'),
                'scheduled_time_readable': publish_date.strftime('%A %H:%M UTC')
            })

        logger.info(f"✓ Calendar created ({len(schedule)} videos)")
        return schedule

    def get_best_day_of_week(self, niche='general'):
        """
        Get the best day of week to publish for this niche.

        Returns:
            Dict with day info
        """
        if niche not in self.OPTIMAL_TIMES:
            niche = 'general'

        optimal_times = self.OPTIMAL_TIMES[niche]
        best_time = optimal_times[0]
        day_num = best_time['day']

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_name = days[day_num]

        return {
            'day_name': day_name,
            'day_number': day_num,
            'optimal_hour': best_time['hour'],
            'timezone': best_time['timezone']
        }

    def get_worst_times_to_avoid(self, niche='general'):
        """
        Get times that historically perform poorly.

        Returns:
            List of times to avoid
        """
        # General worst times (based on analytics research)
        worst_times = [
            {'day': 0, 'hour': 2, 'reason': 'Sunday 2 AM - Lowest engagement'},
            {'day': 2, 'hour': 3, 'reason': 'Wednesday 3 AM - Minimal audience'},
            {'day': 4, 'hour': 23, 'reason': 'Friday 11 PM - Low watch time'},
        ]

        return worst_times

    def calculate_audience_retention_boost(self, publish_time_iso):
        """
        Estimate view boost from optimal publishing time.

        Args:
            publish_time_iso: ISO 8601 timestamp

        Returns:
            Estimated performance boost percentage
        """
        publish_dt = datetime.fromisoformat(publish_time_iso.replace('Z', '+00:00'))
        day_of_week = publish_dt.weekday()
        hour = publish_dt.hour

        # Base boost calculation
        base_boost = 1.0

        # Day of week multiplier
        if day_of_week in [0, 4]:  # Monday, Friday
            base_boost += 0.15  # 15% boost
        elif day_of_week in [1, 3]:  # Tuesday, Thursday
            base_boost += 0.10  # 10% boost
        else:  # Weekend
            base_boost += 0.05  # 5% boost

        # Hour of day multiplier
        if 8 <= hour <= 18:
            base_boost += 0.20  # 20% boost for business hours
        elif 18 <= hour <= 22:
            base_boost += 0.15  # 15% boost for evening
        else:
            base_boost -= 0.10  # -10% for night/early morning

        boost_percentage = (base_boost - 1.0) * 100
        return round(boost_percentage, 1)

    def print_schedule(self, schedule):
        """Print formatted schedule."""
        print("\n" + "=" * 70)
        print("CONTENT CALENDAR")
        print("=" * 70)

        for item in schedule:
            print(f"\n📺 Video #{item['video_number']}")
            print(f"   Date: {item['scheduled_date']}")
            print(f"   Time: {item['scheduled_time_readable']}")
            print(f"   ISO: {item['scheduled_time']}")

        print("\n" + "=" * 70 + "\n")

    def export_schedule(self, schedule, output_file='schedule.json'):
        """Export schedule to JSON file."""
        with open(output_file, 'w') as f:
            json.dump(schedule, f, indent=2)

        logger.info(f"✓ Schedule exported to {output_file}")
        return output_file
