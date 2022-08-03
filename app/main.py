import re, os
from pytube import YouTube
from pytube.exceptions import VideoUnavailable, RegexMatchError
from telebot import asyncio_filters
from telebot.async_telebot import AsyncTeleBot
from telebot.types import ReplyKeyboardMarkup, ForceReply, Message
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_storage import StateMemoryStorage

from shared.config import Config
from shared.functions import *

# , state_storage=StateMemoryStorage()
bot = AsyncTeleBot(Config.TOKEN)

class MyStates(StatesGroup):
    mp3 = State()
    mp4 = State()
    uri = State()

# TODO: welcome message
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message: Message):
    await bot.reply_to(message=message, text=message_welcome(), parse_mode="html")

# TODO: create menu
@bot.message_handler(commands=['menu'])
async def create_menu(message: Message):
    markup = ReplyKeyboardMarkup(
        one_time_keyboard=True,
        input_field_placeholder="Pulsa un bóton, para continuar ...",
        resize_keyboard=True
    )
    markup.add("mp3", "mp4")

    await bot.send_message(message.chat.id, "<b>[Pulsa una opción]</b>", reply_markup=markup, parse_mode="html")
    await bot.set_state(message.from_user.id, MyStates.uri, message.chat.id)

# TODO: States
@bot.message_handler(state=MyStates.uri)
async def get_uri(message: Message):
    markup = ForceReply()
    msg = await bot.send_message(message.chat.id, "Ingrese la url del video que quieres descargar", reply_markup=markup)
    my_state = MyStates.mp3 if message.text == "mp3" else MyStates.mp4
    await bot.set_state(message.from_user.id, my_state, message.chat.id)

# FIXME: pruebas
@bot.message_handler(state=MyStates.mp3)
async def download_mp3(message: Message):
    try:
        print("execute mp3 ...")
        url = message.text
        if is_url_invalid(url=url): return
        yt = YouTube(url=url)
        video = yt.streams.filter(only_audio=True).first()
        filename = remove_special_char(video.default_filename)
        out_file = video.download(output_path=Config.PATH, filename=filename)
        base, _ = os.path.splitext(out_file)
        new_file = f"{base}.mp3"
        os.rename(out_file, new_file)
        my_path = "{}/{}".format(Config.PATH, filename.replace("mp4", "mp3"))
        print("my_path: ", my_path)
        await bot.send_document(message.chat.id, document=open(my_path, 'rb'), timeout=300)
        delete = "rm "+my_path
        os.system(delete)
    except VideoUnavailable:
        await bot.reply_to(message, "Error: La url del video no esta disponible ...")
    except RegexMatchError:
        await bot.reply_to(message, "Error: La url ingresada no es válida ...")

@bot.message_handler(state=MyStates.mp4)
async def download_mp4(message: Message):
    try:
        print("execute mp4 ...")
        url = message.text
        if is_url_invalid(url=url): return
        yt = YouTube(url=url)
        video = yt.streams.get_highest_resolution()
        filename = remove_special_char(video.default_filename)
        video.download(output_path=Config.PATH, filename=filename)
        my_path = "{}/{}".format(Config.PATH, filename)
        await bot.send_document(message.chat.id, document=open(my_path, 'rb'), timeout=300)
        delete = "rm " + my_path
        os.system(delete)
    except VideoUnavailable:
        await bot.reply_to(message, "Error: La url del video no esta disponible ...")
    except RegexMatchError:
        await bot.reply_to(message, "Error: La url ingresada no es válida ...")

# TODO: test message
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)

# TODO: Validations
def is_url_invalid(url: str) -> bool:
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]0,61[A-Z0-9])?.)+[A-Z]2,6.?|'  # domain...
        r'localhost|'  # localhost...
        r'd1,3.d1,3.d1,3.d1,3)' # ...or ip
        r'(?::d+)?'  # optional port
        r'(?:/?|[/?]S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)

# TODO: register filters
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.IsDigitFilter())

# TODO: execute main
import asyncio
if __name__ == "__main__":
    try:
        print("running bot ...")
        asyncio.run(bot.polling(non_stop=True))
    except KeyboardInterrupt:
        print("Error: Interrunpiste el bot")