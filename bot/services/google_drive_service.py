from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
from bot.config import Config

class GoogleDriveService:
    def __init__(self):
        self._initialized = False
        self.service = None

    def initialize(self):
        if not self._initialized:
            scopes = ['https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                Config.GOOGLE_CREDENTIALS_PATH, scopes)
            self.service = build('drive', 'v3', credentials=creds)
            self._initialized = True

    def upload_file(self, file_path, file_name, folder_id):
        self.initialize()
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        # Делаем файл публичным
        self.service.permissions().create(
            fileId=file.get('id'),
            body={'role': 'reader', 'type': 'anyone'},
        ).execute()
        # Получаем публичную ссылку
        file_id = file.get('id')
        public_url = f"https://drive.google.com/uc?id={file_id}"
        
        return public_url

google_drive = GoogleDriveService()