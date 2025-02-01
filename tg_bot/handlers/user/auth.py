from http import HTTPStatus

import aiohttp
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime, timezone

from tg_bot.states.user import LoginStates
from tg_bot.config import BASE_API_URL, logger
from tg_bot.utils import is_valid_token

router = Router()

@router.message(Command('login'))
async def start_login(message: types.Message, state: FSMContext, redis):
    """
    Обработчик для команды /login.
    Устанавливает состояние ожидания логина.
    """
    if await is_valid_token(redis, message):
        await message.answer('Вы успешно вошли!')
        return

    await message.answer("Введите ваш e-mail:")
    await state.update_data(stage="waiting_for_username")  # Сохраняем этап
    await state.set_state(LoginStates.waiting_for_username)

@router.message(LoginStates.waiting_for_username)
async def enter_password(message: types.Message, state: FSMContext):
    """Сохраняет логин пользователя и запрашивает ввод пароля."""
    await state.update_data(username=message.text)
    await message.answer('Введите ваш пароль:')
    await state.set_state(LoginStates.waiting_for_password)


@router.message(LoginStates.waiting_for_password)
async def login_user(message: types.Message, state: FSMContext, redis):
    """
    Обработчик для авторизации пользователя.
    Получает логин/пароль, отправляет запрос к API и сохраняет токен с TTL
    в Redis.
    """
    user_data = await state.get_data()
    username = user_data.get('username')
    password = message.text

    login_url = f'{BASE_API_URL}/auth/jwt/login'

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                    login_url,
                    data={'username': username, 'password': password},
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded'}
            ) as response:
                if response.status == HTTPStatus.OK:
                    response_data = await response.json()
                    access_token = response_data.get('access_token')
                    expiry_date = response_data.get('expiry_date')

                    if not access_token or not expiry_date:
                        logger.error(
                            'API ответил без токена или даты истечения')
                        await message.answer(
                            'Ошибка на сервере. Попробуйте позже.')
                        return

                    expiry_datetime = datetime.fromisoformat(
                        expiry_date.replace('Z', '+00:00'))
                    current_datetime = datetime.now(timezone.utc)
                    ttl = (expiry_datetime - current_datetime).total_seconds()

                    if ttl <= 0:
                        logger.error('Получен токен с истекшим временем жизни')
                        await message.answer(
                            'Ошибка на сервере. Попробуйте позже.')
                        return

                    telegram_id = str(message.from_user.id)
                    await redis.set(f'jwt:{telegram_id}', access_token,
                                    ex=int(ttl))

                    await message.answer('Вы успешно вошли!')

                else:
                    error_message = await response.text()
                    logger.warning(f'Ошибка аутентификации: {error_message}')
                    await message.answer(
                        'Ошибка аутентификации. Проверьте логин/пароль.')
        except Exception as e:
            logger.error(f'Ошибка при отправке запроса: {e}')
            await message.answer(
                'Произошла ошибка подключения к серверу. Попробуйте позже.')
