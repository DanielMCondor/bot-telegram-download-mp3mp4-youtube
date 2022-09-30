import re, os, sys, errno
from pytube import YouTube
from pytube.exceptions import VideoUnavailable, RegexMatchError
from telebot import asyncio_filters
from telebot.async_telebot import AsyncTeleBot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, Message, BotCommand
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_storage import StateMemoryStorage

from shared.config import Config
from shared.functions import *

# TODO: 09/30/22 create directory if not exits
try:
    os.mkdir("./{}".format(Config.PATH))
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

bot = AsyncTeleBot(Config.TOKEN, state_storage=StateMemoryStorage())

class MyStates(StatesGroup):
    salir = State()
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
    markup.add("mp3", "mp4", "salir")

    await bot.send_message(message.chat.id, "<b>[Pulsa una opción]</b>", reply_markup=markup, parse_mode="html")
    await bot.set_state(message.from_user.id, MyStates.uri, message.chat.id)

# TODO: states
@bot.message_handler(state=MyStates.uri)
async def get_uri(message: Message):
    if message.text == "salir":
        markup = ReplyKeyboardRemove()
        await bot.send_message(message.chat.id, "saliste del menú", reply_markup=markup)
        await bot.delete_state(message.from_user.id, message.chat.id)
    else:
        msg = "Ingrese la url del video que quieres descargar"
        markup = ForceReply()
        await bot.send_message(message.chat.id, msg, reply_markup=markup)
        if message.text == "mp3": my_state = MyStates.mp3
        elif message.text == "mp4": my_state = MyStates.mp4
        else: my_state = MyStates.salir
        await bot.set_state(message.from_user.id, my_state, message.chat.id)

# TODO: download mp3 - YouTube
@bot.message_handler(state=MyStates.mp3)
async def download_mp3(message: Message):
    try:
        markup = ReplyKeyboardRemove()
        print("execute mp3 ...")
        url = message.text
        if is_url_invalid(url=url): return
        delete = await bot.send_message(message.chat.id, "Descargando archivo ....")
        yt = YouTube(url=url, on_progress_callback=on_progress_callback)
        video = yt.streams.filter(only_audio=True).first()
        filename = remove_special_char(video.default_filename)
        out_file = video.download(output_path=Config.PATH, filename=filename)
        base, _ = os.path.splitext(out_file)
        new_file = f"{base}.mp3"
        os.rename(out_file, new_file)
        my_path = "{}/{}".format(Config.PATH, filename.replace("mp4", "mp3"))
        print("my_path: ", my_path)
        await bot.send_chat_action(message.chat.id, "upload_audio")
        await bot.send_audio(message.chat.id, audio=open(my_path, 'rb'), timeout=300, caption=filename.replace("mp4", "mp3"))
        await bot.delete_message(message.chat.id, delete.id)
        await bot.send_message(message.chat.id, "la operación fue éxitosa ....", reply_markup=markup)
        delete = "rm "+my_path
        os.system(delete)
    except VideoUnavailable:
        await bot.reply_to(message, "Error: La url del video no esta disponible ...")
    except RegexMatchError:
        await bot.reply_to(message, "Error: La url ingresada no es válida ...")
    finally:
        await bot.delete_state(message.from_user.id, message.chat.id)

# TODO: download mp4 - YouTube
@bot.message_handler(state=MyStates.mp4)
async def download_mp4(message: Message):
    try:
        markup = ReplyKeyboardRemove()
        print("execute mp4 ...")
        url = message.text
        if is_url_invalid(url=url): return
        delete = await bot.send_message(message.chat.id, "Descargando archivo ....")
        yt = YouTube(url=url, on_progress_callback=on_progress_callback)
        video = yt.streams.get_highest_resolution()
        filename = remove_special_char(video.default_filename)
        video.download(output_path=Config.PATH, filename=filename)
        my_path = "{}/{}".format(Config.PATH, filename)
        await bot.send_chat_action(message.chat.id, "upload_video")
        await bot.send_video(message.chat.id, video=open(my_path, 'rb'), timeout=300, caption=filename)
        await bot.delete_message(message.chat.id, delete.id)
        await bot.send_message(message.chat.id, "la operación fue éxitosa ....", reply_markup=markup)
        delete = "rm " + my_path
        os.system(delete)
    except VideoUnavailable:
        await bot.reply_to(message, "Error: La url del video no esta disponible ...")
    except RegexMatchError:
        await bot.reply_to(message, "Error: La url ingresada no es válida ...")
    finally:
        await bot.delete_state(message.from_user.id, message.chat.id)

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

# TODO: callback - progress bar - YouTube
def on_progress_callback(video, chunck, bytes_remaining):
    filesize = video.filesize
    current = ((filesize - bytes_remaining) / filesize)
    percent = ('{0:.1f}').format(current*100)
    progress = int(50*current)
    status = '█' * progress + '-' * (50 - progress)
    sys.stdout.write(' ↳ {download} |{bar}| {percent}%\r'.format(download="Descargando ...", bar=status, percent=percent))
    sys.stdout.flush()

async def main():
    await bot.set_my_commands([
        BotCommand("/start", "Da la bienvenida"),
        BotCommand("/help", "Brinda ayuda sobre los comandos"),
        BotCommand("/menu", "Muestra el menú del bot")
    ])
    await bot.polling(non_stop=True)

# TODO: register filters
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.IsDigitFilter())

# TODO: execute main
import asyncio
if __name__ == "__main__":
    try:
        print("running bot ...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Error: Interrunpiste el bot")