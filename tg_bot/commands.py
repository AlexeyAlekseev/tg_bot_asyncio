from aiogram.types import BotCommand

bot_commands = [
    BotCommand(command='/start', description='Запустить бота'),
    BotCommand(command='/help', description='Получить справку'),
    BotCommand(command='/register', description='Зарегистрироваться'),
    BotCommand(command='/login', description='Авторизоваться'),
    BotCommand(command='/settings', description='Изменить настройки'),
]
