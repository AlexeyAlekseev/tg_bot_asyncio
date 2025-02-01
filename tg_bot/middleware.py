from aiogram.dispatcher.middlewares.base import BaseMiddleware


class RedisMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        """
        Middleware для добавления Redis в контекст данных (`data`).
        """
        dispatcher = data['dispatcher']
        data['redis'] = dispatcher.get('redis')
        return await handler(event, data)