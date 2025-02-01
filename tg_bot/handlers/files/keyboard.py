from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup


keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📎 Отправить файл")]],
    resize_keyboard=True  # Клавиатура адаптируется под экран
)


def get_tags_keyboard(tags: list, tag_type: str, selected_tags: list):
    """Создает клавиатуру с тегами."""
    buttons = [
        InlineKeyboardButton(
            text=f"✅ {tag}" if tag in selected_tags else tag,
            callback_data=f"tag_{tag_type}_{tag}"
        ) for tag in tags
    ]

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


# Клавиатура подтверждения
confirm_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_file")]]
)

choise_enter_tags = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏ Ввести теги",
                                  callback_data="enter_user_tags")],
            [InlineKeyboardButton(text="➡ Пропустить",
                                  callback_data="skip_user_tags")]
        ])