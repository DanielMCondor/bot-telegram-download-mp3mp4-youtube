from decouple import config

class Config:
    TOKEN = config("TOKEN")
    PATH = config("DIR_DOWNLOAD")
    CHAT_ID = 637733694