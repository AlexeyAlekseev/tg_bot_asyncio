import json
from http import HTTPStatus

import aiohttp
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.config import BASE_API_URL
from tg_bot.states.user import Registration
from tg_bot.validators import check_user_registration

router = Router()


@router.message(Command('register'))
async def start_registration(message: types.Message, state: FSMContext):
    """
    Проверяет состояние регистрации пользователя по Telegram ID,
    если пользователь ещё не зарегистрирован, запускает процесс
    регистрации.
    """
    telegram_id = str(message.from_user.id)

    if await check_user_registration(telegram_id, message):
        return

    await message.answer(
        'Давайте начнем процесс процесс регистрации.'
    )
    await message.answer('Введите ваш email:')
    await state.set_state(Registration.waiting_for_email)


@router.message(Registration.waiting_for_email)
async def enter_password(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод пользователем адреса электронной почты
    и переводит состояние машины состояний к ожиданию ввода пароля.
    """
    await state.update_data(email=message.text)
    await message.answer('Введите ваш пароль:')
    await state.set_state(Registration.waiting_for_password)


@router.message(Registration.waiting_for_password)
async def enter_username(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод пароля, сохраняет его в состояние и переводит FSM
    на следующий шаг для ввода username.
    """
    await state.update_data(password=message.text)
    await message.answer('Введите ваш username:')
    await state.set_state(Registration.waiting_for_username)


@router.message(Registration.waiting_for_username)
async def register_user(message: types.Message, state: FSMContext):
    """
    Регистрирует пользователя с использованием данных, собранных из состояния.

    Raises:
        Непосредственно исключения не выбрасываются, но на основе ответа
        от внешнего API возможно формирование сообщения об ошибке.

    Returns:
        None: Отправляет сообщение пользователю с результатом процесса
            регистрации.
    """
    await state.update_data(username=message.text)
    user_data = await state.get_data()

    telegram_id = str(message.from_user.id)
    email = user_data.get('email')
    password = user_data.get('password')
    username = user_data.get('username')

    registration_data = {
        'email': email,
        'password': password,
        'is_active': True,
        'is_superuser': False,
        'is_verified': False,
        'name': username,
        'telegram_id': telegram_id,
        'username': username
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f'{BASE_API_URL}/auth/register',
                                headers={'accept': 'application/json',
                                         'Content-Type': 'application/json'},
                                data=json.dumps(registration_data)) as resp:
            if resp.status == HTTPStatus.CREATED:
                response = f'Регистрация прошла успешно.'
            else:
                response_text = await resp.text()
                response = f'Ошибка регистрации: {response_text}'

    await state.clear()
    await message.answer(response)
