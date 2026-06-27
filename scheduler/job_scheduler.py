import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import logging
from scraper.dashboard_scraper import DashboardScraper
from analyzer.deadline_checker import DeadlineChecker
from notifications.telegram_bot import TelegramNotifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobMonitorScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scraper = DashboardScraper()
        self.deadline_checker = DeadlineChecker()
        self.notifier = TelegramNotifier()
        self.processed_jobs = set()  # Track already seen jobs
        
    async def monitor_jobs(self):
        """Run every 30 seconds to check new jobs"""
        try:
            logger.info("🔍 Scanning dashboard for new jobs...")
            
            # Step 1: Scrape new listings
            new_jobs = await self.scraper.fetch_new_jobs()
            
            if not new_jobs:
                logger.info("No new jobs found")
                return
            
            # Step 2: Filter by criteria
            suitable_jobs = []
            for job in new_jobs:
                # Check if already processed
                if job['id'] in self.processed_jobs:
                    continue
                    
                # Apply filters
                if self.deadline_checker.has_conflict(job['deadline']):
                    logger.info(f"❌ Job {job['title']} conflicts with existing deadlines")
                    continue
                    
                if job['pay_rate'] < self.get_min_pay_threshold():
                    continue
                    
                suitable_jobs.append(job)
                self.processed_jobs.add(job['id'])
            
            # Step 3: Send notifications for suitable jobs
            if suitable_jobs:
                await self.notifier.send_alerts(suitable_jobs)
                logger.info(f"📱 Sent {len(suitable_jobs)} job alerts")
                
        except Exception as e:
            logger.error(f"Error in monitor cycle: {e}")
    
    def get_min_pay_threshold(self):
        # Could be configurable from settings or AI analysis
        return 25.0  # $25/hour minimum
    
    def start(self):
        """Start the monitoring system"""
        self.scheduler.add_job(
            self.monitor_jobs,
            'interval',
            seconds=30,
            id='job_monitor'
        )
        self.scheduler.start()
        logger.info("✅ Job monitor started - scanning every 30 seconds")
        
        # Run once immediately
        asyncio.create_task(self.monitor_jobs())