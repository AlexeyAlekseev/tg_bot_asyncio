import asyncio

from aiogram import Bot, Dispatcher

from tg_bot.commands import bot_commands
from tg_bot.config import TOKEN, logger
from tg_bot.handlers import start_commands
from tg_bot.handlers.user.auth import router as auth_router
from tg_bot.handlers.user.registration import router as registration_router
from tg_bot.middleware import RedisMiddleware
from tg_bot.redis import on_startup, on_shutdown


async def set_bot_commands(bot: Bot):
    """
    Установка стандартных команд для бота.
    """
    await bot.set_my_commands(bot_commands)


async def main():
    """Основной цикл бота."""

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.update.middleware(RedisMiddleware())

    dp.include_router(start_commands.router)
    dp.include_router(registration_router)
    dp.include_router(auth_router)

    try:
        await on_startup(dp)
        await set_bot_commands(bot)

        logger.info('Бот запущен...')
        await dp.start_polling(bot)

    finally:
        await on_shutdown(dp)
        logger.info('Бот остановлен')


if __name__ == '__main__':
    asyncio.run(main())
