from aiogram import Bot, types, Dispatcher
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove

bot = Bot('1661866696:AAFi8P_OLIstQ2RGmoZFBkXVSZivYMoJIzk')  # основа
#bot = Bot('5207851764:AAGIWwh7EX5t-nJX6xjoT41vuaRH-gkw-Lg')  # тест бот

dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("Опа, спасибо что Вы так долго меня ждали, я скоро обновлюсь и стану еще лучше))")
    await bot.send_message(339512152, f'{message.chat.id} {message.from_user.first_name}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)