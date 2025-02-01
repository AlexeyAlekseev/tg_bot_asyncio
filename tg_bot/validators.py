from http import HTTPStatus

import aiohttp
from aiogram import types

from tg_bot.config import BASE_API_URL
from tg_bot.exception import ServerError


async def check_user_registration(telegram_id: str,
                                  message: types.Message) -> bool:
    """
    Проверяет, зарегистрирован ли пользователь с данным Telegram ID,
    и отправляет результаты проверки пользователю.

    Args:
        telegram_id (str): Идентификатор пользователя Telegram.
        message (types.Message): Сообщение пользователя для отправки ответа.

    Raises:
        None: Сообщения отправляются напрямую пользователю.

    Returns:
        bool: True, если пользователь уже зарегистрирован, False — если нет.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'{BASE_API_URL}/user/telegram_signed_up/{telegram_id}'
            ) as resp:
                if resp.status != HTTPStatus.OK:
                    raise ServerError(f'Ошибка сервера, статус: {resp.status}')

                response_data = await resp.json()

                if response_data:
                    await message.answer(
                        'Вы уже зарегистрированы в системе. '
                        'Пожалуйста, авторизуйтесь.'
                    )
                    return True
                return False

    except ServerError as e:
        await message.answer(
            f'Ошибка при проверке регистрации: {str(e)}. '
            'Попробуйте позже.'
        )
        return True
    except Exception as e:
        await message.answer(
            f'Произошла непредвиденная ошибка: {str(e)}. '
            'Попробуйте позже.'
        )
        return True