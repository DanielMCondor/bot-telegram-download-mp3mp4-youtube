from decouple import config

class Config:
    TOKEN = config("TOKEN")
    PATH = "download"
    CHAT_ID = 637733694