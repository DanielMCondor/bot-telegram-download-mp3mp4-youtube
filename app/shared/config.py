from decouple import config

class Config:
    TOKEN = config("TOKEN")
    PATH = "download"