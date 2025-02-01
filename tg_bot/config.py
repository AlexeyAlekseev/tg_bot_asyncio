import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('tg_bot')


TOKEN = os.getenv('TG_TOKEN')
if not TOKEN:
    raise ValueError('Отсутствует переменная окружения TG_TOKEN')

BASE_API_URL = os.getenv('BASE_API_URL',
                         'http://localhost:8000')

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')