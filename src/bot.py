from asyncio import run
from aiogram import Bot, Dispatcher

from handlers import start
from src.handlers.settings import settings
from src.handlers.summ_and_transcrib import voices, circles, youtube

"""
Заметка Полине:
создаем роутеры в тех файлах где мы работаем и вызываем роутер файла здесь
все функции-хендлеры, которые будут в этом файле с роутером, автоматически встраиваются в бот

Бот по ссылке: https://t.me/transri_bot
"""

TOKEN = "7457335914:AAGhfck6-tKL0pmeOsSxwLNxBHkEUU8oypo"
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(start.router)
    dp.include_router(settings.router)
    dp.include_router(voices.router)
    dp.include_router(circles.router)
    dp.include_router(youtube.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    run(main())