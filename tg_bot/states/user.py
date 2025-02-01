from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    """
    Класс для управления состояниями регистрации.

    Используется для отслеживания и переключения между различными состояниями
    в процессе регистрации пользователя.
    """
    waiting_for_email = State()
    waiting_for_password = State()
    waiting_for_username = State()


class LoginStates(StatesGroup):
    """
    Класс для управления состояниями авторизации.

    Используется для отслеживания состояний процесса логина пользователя,
    таких как ожидание ввода пароля.
    """
    waiting_for_username = State()
    waiting_for_password = State()