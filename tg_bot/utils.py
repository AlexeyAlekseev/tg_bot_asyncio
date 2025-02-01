async def is_valid_token(redis, message):
    """
    Проверяет, существует ли токен пользователя в Redis.
    Возвращает True, если токен валиден, иначе False.
    """
    telegram_id = str(message.from_user.id)
    token_key = f'jwt:{telegram_id}'

    token = await redis.get(token_key)

    return token is not None
