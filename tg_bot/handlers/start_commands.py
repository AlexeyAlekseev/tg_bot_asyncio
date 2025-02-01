from aiogram import types, Router
from aiogram.filters import Command

router = Router()


@router.message(Command('start'))
async def start_handler(message: types.Message):
    await message.answer("Привет! Я Telegram-бот на aiogram.")

@router.message(Command('help'))
async def help_handler(message: types.Message):
    await message.answer("Я могу отвечать на команды /start, /help, /register.")
