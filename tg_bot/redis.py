import aioredis
from aiogram import Dispatcher

from tg_bot.config import logger, REDIS_URL


async def on_startup(dp: Dispatcher):
    """
    Функция запуска, инициализируем подключения к Redis перед стартом бота.
    """
    redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    dp['redis'] = redis
    logger.info('Подключение к Redis успешно!')


async def on_shutdown(dp: Dispatcher):
    """
    Функция завершения, закрываем подключения к Redis при остановке бота.
    """
    redis = dp.get('redis')
    if redis:
        await redis.close()
        logger.info('Соединение с Redis закрыто.')