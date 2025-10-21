import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from app.email_service import email_service
from app.statistics_service import statistics_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_weekly_digest():
    """
    Job function to send the weekly digest email.
    This is called by the scheduler every Monday at 09:00 IST.
    """
    logger.info("Starting weekly digest email job...")
    
    try:
        stats = statistics_service.get_weekly_statistics()
        
        logger.info(f"Weekly statistics: {stats['total_assessments']} assessments, "
                   f"avg score: {stats['avg_score']:.1f}%, "
                   f"top states: {[s[0] for s in stats['top_5_states'][:3]]}")
        
        success, error = email_service.send_weekly_digest(stats)
        
        if success:
            logger.info("Weekly digest email sent successfully")
        else:
            logger.error(f"Failed to send weekly digest email: {error}")
    
    except Exception as e:
        logger.error(f"Error in weekly digest job: {str(e)}", exc_info=True)


class DigestScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.ist_timezone = timezone('Asia/Kolkata')
    
    def start(self):
        """
        Start the scheduler with the weekly digest job.
        Scheduled for every Monday at 09:00 IST.
        """
        self.scheduler.add_job(
            send_weekly_digest,
            trigger=CronTrigger(
                day_of_week='mon',
                hour=9,
                minute=0,
                timezone=self.ist_timezone
            ),
            id='weekly_digest',
            name='Send Weekly Compliance Digest',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Digest scheduler started. Weekly digest will be sent every Monday at 09:00 IST")
    
    def shutdown(self):
        """
        Shutdown the scheduler gracefully.
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Digest scheduler shut down")
    
    def trigger_now(self):
        """
        Manually trigger the weekly digest job immediately.
        Useful for testing.
        """
        logger.info("Manually triggering weekly digest job...")
        send_weekly_digest()


digest_scheduler = DigestScheduler()
