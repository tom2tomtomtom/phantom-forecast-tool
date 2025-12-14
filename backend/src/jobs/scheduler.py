"""
Job scheduler for automated tasks.

Uses APScheduler for cron-style job scheduling.
"""

import logging
from typing import Optional
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> AsyncIOScheduler:
    """Get or create the scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(
            timezone="America/New_York",  # Market timezone
            job_defaults={
                "coalesce": True,  # Combine missed runs
                "max_instances": 1,  # Only one instance of each job
                "misfire_grace_time": 3600,  # 1 hour grace period
            }
        )
    return _scheduler


async def start_scheduler():
    """
    Start the job scheduler with configured jobs.

    Called during application startup.
    """
    from .daily_scan import run_daily_scan, run_price_update

    scheduler = get_scheduler()

    if scheduler.running:
        logger.warning("Scheduler already running")
        return

    # Schedule daily opportunity scan - 8:00 AM ET (before market open)
    scheduler.add_job(
        run_daily_scan,
        CronTrigger(hour=8, minute=0),
        id="daily_opportunity_scan",
        name="Daily Opportunity Scan",
        replace_existing=True,
    )
    logger.info("Scheduled daily opportunity scan for 8:00 AM ET")

    # Schedule price updates - Every 4 hours during market hours
    scheduler.add_job(
        run_price_update,
        CronTrigger(hour="9,13,17", minute=30),  # 9:30, 13:30, 17:30 ET
        id="price_update",
        name="Price Update",
        replace_existing=True,
    )
    logger.info("Scheduled price updates for 9:30, 13:30, 17:30 ET")

    # Start the scheduler
    scheduler.start()
    logger.info("Job scheduler started")


async def shutdown_scheduler():
    """
    Gracefully shutdown the scheduler.

    Called during application shutdown.
    """
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=True)
        logger.info("Job scheduler shut down")
        _scheduler = None


def add_manual_job(func, job_id: str, **kwargs):
    """Add a job manually (for testing or one-off runs)."""
    scheduler = get_scheduler()
    scheduler.add_job(
        func,
        id=job_id,
        replace_existing=True,
        **kwargs
    )


def get_job_status() -> dict:
    """Get status of all scheduled jobs."""
    scheduler = get_scheduler()

    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
        })

    return {
        "running": scheduler.running,
        "jobs": jobs,
        "timezone": str(scheduler.timezone),
    }
