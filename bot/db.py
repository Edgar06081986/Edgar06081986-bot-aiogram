# import aiosqlite
# from bot.config import Config
# from bot.logger import log_system_event, LogTypesEnum


# class Database:
#     _instance = None
    

#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#             cls._instance.connection = None
#         return cls._instance
    

#     async def connect(self):
#         if self.connection is None:
#             try:
#                 self.connection = await aiosqlite.connect(Config.DB_URL)
#                 log_system_event(LogTypesEnum.INFO, "Database connection established")
#             except Exception as e:
#                 log_system_event(LogTypesEnum.ERROR, f"Database connection error: {str(e)}")
#                 raise
    

#     async def close(self):
#         if self.connection is not None:
#             await self.connection.close()
#             self.connection = None
#             log_system_event(LogTypesEnum.INFO, "Database connection closed")
    

#     async def init_db(self):
#         try:
#             await self.connect()
#             await self.connection.execute('''
#                 CREATE TABLE IF NOT EXISTS users (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     telegram_id INTEGER UNIQUE,
#                     username TEXT
#                 )
#             ''')
#             await self.connection.commit()
#             log_system_event(LogTypesEnum.INFO, "Database initialized successfully")
#         except Exception as e:
#             log_system_event(LogTypesEnum.ERROR, f"Error initializing database: {str(e)}")
#             raise
    

#     async def get_user(self, telegram_id: int):
#         try:
#             async with self.connection.execute(
#                 'SELECT * FROM users WHERE telegram_id = ?', 
#                 (telegram_id,)
#             ) as cursor:
#                 return await cursor.fetchone()
#         except Exception as e:
#             log_system_event(LogTypesEnum.ERROR, f"Error getting user: {str(e)}")
#             raise


# db = Database()