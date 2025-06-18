from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from typing import List
from bot.config import Config
from bot.logger import log_system_event, LogTypesEnum

class GoogleAPIService:
    def __init__(self):
        self._initialized = False
        self.service = None
        self.sheet = None

    async def initialize(self):
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            Config.GOOGLE_CREDENTIALS_PATH, scopes)
        self.service = build('sheets', 'v4', credentials=creds)
        self.sheet = self.service.spreadsheets()
        self._initialized = True

    async def append_sheet_data(self, sheet_name: str, values: List[List[str]]) -> bool:
        if not self._initialized:
            await self.initialize()
        try:
            self.sheet.values().append(
                spreadsheetId=Config.GOOGLE_SHEETS_FILE_ID,
                range=sheet_name,
                valueInputOption="USER_ENTERED",
                body={"values": values}
            ).execute()
            return True
        except Exception as e:
            log_system_event(LogTypesEnum.ERROR, f"Error appending data to {sheet_name}: {str(e)}")
            return False

google_api = GoogleAPIService()