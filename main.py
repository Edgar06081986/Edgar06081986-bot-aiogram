import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers import router
from bot.config import Config
from bot.logger import log_system_event, LogTypesEnum
from bot.scheduler import scheduler
# from bot.db import db
from datetime import datetime


async def main():
    try:
        bot = Bot(token=Config.BOT_TOKEN)
        dp = Dispatcher(bot=bot, storage=MemoryStorage())
        
        # await db.init_db()
        # log_system_event(LogTypesEnum.INFO, "Database initialized")

        # Добавляем задачу в планировщик
        async def print_time():
            log_system_event(LogTypesEnum.INFO, f"Current time: {datetime.now()}")
        
        scheduler.add_job(
            print_time,
            'interval',
            minutes=1,
            next_run_time=datetime.now()
        )
        
        await scheduler.start()
        log_system_event(LogTypesEnum.INFO, "Scheduler started")

        dp.include_router(router)
        log_system_event(LogTypesEnum.INFO, "Router included")

        await bot.delete_webhook(drop_pending_updates=True)
        log_system_event(LogTypesEnum.INFO, "Starting polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except Exception as error:
        log_system_event(LogTypesEnum.ERROR, f"Bot error: {error}")
        raise

    finally:
        log_system_event(LogTypesEnum.INFO, "Shutting down the bot...")
        if hasattr(dp, '_polling') and dp._polling:
            await dp.stop_polling()
            log_system_event(LogTypesEnum.INFO, "Polling stopped")
        
        await scheduler.shutdown()
        # await db.close()
        await bot.session.close()
        
        log_system_event(LogTypesEnum.INFO, "Bot session closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_system_event(LogTypesEnum.INFO, "Bot stopped by user")
    except Exception as error:
        log_system_event(LogTypesEnum.ERROR, f"Unexpected error: {error}")
