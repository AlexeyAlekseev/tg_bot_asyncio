import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboard import keyboard, get_tags_keyboard, choise_enter_tags
from test_data import tag_list

TOKEN = "TOKEN_HERE"


class UploadFileState(StatesGroup):
    waiting_for_file = State()
    choosing_admin_tags = State()
    entering_user_tags = State()


class BotHandler:
    def __init__(self):
        self.bot = Bot(token=TOKEN)
        self.dp = Dispatcher()
        self.user_tags = {}

        """
            Конструктор класса, инициализирует объект бота и диспетчера.
            Также регистрируются все хэндлеры,
            которые обрабатывают разные типы сообщений и запросов.
        """
        self.dp.message.register(self.start, Command("start"))
        self.dp.message.register(self.ask_for_file, F.text == "📎 Отправить файл")               # Запрашивает у пользователя файл для загрузки.
        self.dp.message.register(self.handle_file, F.document, UploadFileState.waiting_for_file) # Обрабатывает файл, предлагая пользователю выбрать админские теги.
        self.dp.callback_query.register(self.admin_tag_callback, F.data.startswith("tag_admin_"))# Обрабатывает выбор админских тегов, добавляя или удаляя их из списка.
        self.dp.callback_query.register(self.skip_user_tags, F.data == "skip_user_tags")        # Добавляем обработчик пропуска
        self.dp.callback_query.register(self.choose_user_tags, F.data == "choose_user_tags")    # Оставляем обработчик выбора
        self.dp.message.register(self.enter_user_tag, UploadFileState.entering_user_tags)
        self.dp.callback_query.register(self.choose_user_tags, F.data == "choose_user_tags")     # Запрашивает у пользователя ввод пользовательских тегов.
        self.dp.message.register(self.enter_user_tag, UploadFileState.entering_user_tags)        # Обрабатывает ввод пользовательских тегов.
        self.dp.callback_query.register(self.confirm_file, F.data == "confirm_file")             # Подтверждает загрузку файла и отправляет
                                                                                                 # его обратно пользователю с прикрепленными тегами.

    @staticmethod
    def get_admin_tags():
        return [tag["name"] for tag in tag_list[0]]

    @staticmethod
    def get_user_tags():
        return [tag["name"] for tag in tag_list[1]]

    async def start(self, message: Message, state: FSMContext):
        """Запуск бота, сброс состояния."""
        await state.clear()
        self.user_tags[message.from_user.id] = {"admin": [], "user": []}
        await message.answer("Привет! Отправь мне файл, нажав кнопку ниже 👇", reply_markup=keyboard)
        await state.set_state(UploadFileState.waiting_for_file)

    async def ask_for_file(self, message: Message, state: FSMContext):
        """Просит пользователя отправить файл."""
        await message.answer("Прикрепи файл 📎")
        await state.set_state(UploadFileState.waiting_for_file)

    async def handle_file(self, message: Message, state: FSMContext):
        """Обрабатывает полученный файл и предлагает выбрать админские теги."""
        await state.update_data(file_id=message.document.file_id)
        await message.answer("Файл получен! Теперь выбери админские теги:",
                             reply_markup=get_tags_keyboard(self.get_admin_tags(), "admin", []))
        await state.set_state(UploadFileState.choosing_admin_tags)

    async def admin_tag_callback(self, callback: CallbackQuery, state: FSMContext):
        """Обрабатывает выбор админских тегов."""
        tag_slug = callback.data.replace("tag_admin_", "")
        user_id = callback.from_user.id

        if user_id not in self.user_tags:
            self.user_tags[user_id] = {"admin": [],
                                       "user": []}  # Инициализация

        if tag_slug in self.user_tags[user_id]["admin"]:
            self.user_tags[user_id]["admin"].remove(tag_slug)
        else:
            self.user_tags[user_id]["admin"].append(tag_slug)

        await callback.message.edit_reply_markup(
            reply_markup=get_tags_keyboard(
                self.get_admin_tags(), "admin",
                self.user_tags[user_id]["admin"]
            )
        )

        if self.user_tags[user_id]["admin"]:
            await callback.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        get_tags_keyboard(self.get_admin_tags(), "admin", self.user_tags[user_id]["admin"]).inline_keyboard[0],
                        [InlineKeyboardButton(text="➡ Ввести пользовательские теги", callback_data="choose_user_tags")]
                    ]
                )
            )

    async def skip_user_tags(self, callback: CallbackQuery, state: FSMContext):
        """Пропускает ввод пользовательских тегов и сразу подтверждает файл."""
        user_id = callback.from_user.id
        self.user_tags[user_id][
            "user"] = []  # Очищаем пользовательские теги (чтобы не было старых данных)
        await self.confirm_file(callback, state)

    async def choose_user_tags(self, callback: CallbackQuery,
                               state: FSMContext):
        """Просит пользователя ввести пользовательские теги или пропустить шаг."""
        await callback.message.edit_text(
            "Введите пользовательские теги (через запятую) или нажмите 'Пропустить'.",
            reply_markup=choise_enter_tags
        )
        await state.set_state(UploadFileState.entering_user_tags)

    async def enter_user_tag(self, message: Message, state: FSMContext):
        """Обрабатывает ввод пользовательских тегов."""
        user_id = message.from_user.id
        user_input = message.text.strip()

        # Разделяем введённые теги и добавляем их в список
        user_tags = [tag.strip() for tag in user_input.split(",") if
                     tag.strip()]

        if not user_tags:
            await message.answer(
                "Вы не ввели ни одного тега. Попробуйте снова.")
            return

        # Сохраняем теги
        self.user_tags[user_id]["user"].extend(user_tags)
        await state.update_data(
            user_tags=self.user_tags[user_id]["user"])  # Обновляем state

        await message.answer(f"Теги добавлены: {', '.join(user_tags)}")

        # Кнопка подтверждения
        await message.answer(
            "Теперь подтвердите загрузку файла:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Подтвердить",
                                          callback_data="confirm_file")]
                ]
            )
        )

    @staticmethod
    def prepare_data_for_sending(file_id: str, file_data: bytes,
                                 admin_tags: list, user_tags: list) -> dict:
        """
        Подготавливает данные для отправки на API бекенда.
        :param file_id: ID файла, который был загружен
        :param file_data: Данные файла в байтах
        :param admin_tags: Список админских тегов
        :param user_tags: Список пользовательских тегов
        :return: Словарь с подготовленными данными
        """
        data = {
            "file_id": file_id,
            "file_data": file_data,  # Файл будет передан в байтовом формате
            "admin_tags": admin_tags,
            "user_tags": user_tags
        }
        return data

    async def confirm_file(self, callback: CallbackQuery, state: FSMContext):
        """Подтверждает файл и отправляет его обратно пользователю с тегами."""
        user_id = callback.from_user.id
        data = await state.get_data()
        file_id = data.get("file_id")

        if not file_id:
            await callback.message.answer("Ошибка: файл не найден.")
            return

        admin_tags_text = ", ".join(self.user_tags[user_id]["admin"]) if self.user_tags[user_id]["admin"] else None
        user_tags_text = ", ".join(self.user_tags[user_id]["user"]) if self.user_tags[user_id]["user"] else None

        # Получаем файл через метод bot.get_file
        file = await self.bot.get_file(file_id)
        file_path = file.file_path  # Путь к файлу на сервере Telegram
        # Скачиваем содержимое файла
        file_data = await self.bot.download_file(file_path)
        # Подготавливаем данные для отправки на сервер
        prepared_data = self.prepare_data_for_sending(file_id, file_data, self.user_tags[user_id]["admin"], self.user_tags[user_id]["user"])
        print(type(prepared_data['file_data']))  # Выводим подготовленные данные (для отладки)

        await self.bot.send_document(
            callback.message.chat.id, file_id,
            caption=f"Файл загружен с тегами:\n\nАдминские: {admin_tags_text}\nПользовательские: {user_tags_text}"
        )
        await state.clear()
        await callback.message.answer("Файл успешно загружен!", reply_markup=keyboard)

    async def run(self):
        """Запуск бота."""
        await self.dp.start_polling(self.bot)


if __name__ == "__main__":
    bot_handler = BotHandler()
    asyncio.run(bot_handler.run())
