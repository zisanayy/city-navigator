# app/jobs.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from run_scrapers import scrape_all

scheduler: BackgroundScheduler | None = None

def start_scheduler():
    global scheduler
    if scheduler and scheduler.running:
        return scheduler

    scheduler = BackgroundScheduler(timezone="Europe/Warsaw")

    # Her gün saat 03:00'te çalışsın (gece sunucu müsaitken)
    scheduler.add_job(scrape_all, CronTrigger(hour=3, minute=0), id="daily_scrape", replace_existing=True)

    # Uygulama açıldığında bir kez de hemen çalışsın (opsiyonel)
    scheduler.add_job(scrape_all, trigger="date", run_date=datetime.now(), id="on_start", replace_existing=True)

    scheduler.start()
    return scheduler

def shutdown_scheduler():
    if scheduler:
        scheduler.shutdown(wait=False)
