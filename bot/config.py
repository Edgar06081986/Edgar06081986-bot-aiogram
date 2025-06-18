import os
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


if os.path.exists(os.path.join(BASE_DIR, '.env.local')):
    load_dotenv(os.path.join(BASE_DIR, '.env.local'))
else:
    load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    # DB_URL = os.getenv('DB_URL', 'example.db')
    LOG_ROTATE_DAYS = int(os.getenv('LOG_ROTATE_DAYS', 1))


 # --- Добавьте эти строки ---
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', './google-credentials.json')
    GOOGLE_SHEETS_FILE_ID = os.getenv('GOOGLE_SHEETS_FILE_ID', 'ваш_ID_таблицы')
    GOOGLE_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    GOOGLE_FOLDER_IMAGES_ID = os.getenv('GOOGLE_FOLDER_IMAGES_ID', 'ваш_ID_папки_с_изображениями')