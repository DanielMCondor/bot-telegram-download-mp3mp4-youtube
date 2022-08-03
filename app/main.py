from telebot import asyncio_filters
from telebot.async_telebot import AsyncTeleBot
from telebot.types import ReplyKeyboardMarkup, ForceReply, Message
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_storage import StateMemoryStorage

from shared.config import Config
from shared.functions import *

bot = AsyncTeleBot(Config.TOKEN, state_storage=StateMemoryStorage())

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
    print("mp3: ", message.text)
    """
    State 2. Will process when user's state is MyStates.surname.
    """
    await bot.send_message(message.chat.id, "What is your age?")
    # await bot.set_state(message.from_user.id, MyStates.age, message.chat.id)
    # async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
    #     data['surname'] = message.text

@bot.message_handler(state=MyStates.mp4)
async def download_mp4(message: Message):
    print("mp4: ", message.text)

# TODO: test message
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)


# TODO: register filters
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.IsDigitFilter())

# TODO: execute main
import asyncio
if __name__ == "__main__":
    try:
        print("running bot ...")
        asyncio.run(bot.polling())
    except KeyboardInterrupt:
        print("Error: Interrunpiste el bot")