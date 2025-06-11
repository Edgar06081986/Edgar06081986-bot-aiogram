from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.logger import log_system_event, LogTypesEnum


class Scheduler:
    _instance = None
    

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.scheduler = AsyncIOScheduler()
        return cls._instance
    

    async def start(self):
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                log_system_event(LogTypesEnum.INFO, "Scheduler started")
        except Exception as e:
            log_system_event(LogTypesEnum.ERROR, f"Error starting scheduler: {str(e)}")
            raise
    

    def add_job(self, func, trigger, **kwargs):
        self.scheduler.add_job(func, trigger, **kwargs)
    
    
    async def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            log_system_event(LogTypesEnum.INFO, "Scheduler stopped")


scheduler = Scheduler()