from aiogram import types, Router
from aiogram.filters import Command

from src.db_helper.db_helper import DbHelper

router = Router()

@router.message(Command('start'))
async def start(message: types.Message):
    # создаем пользователя
    user_id = message.from_user.id
    base_param_user = {
        "user_id": user_id,
        "tokens_amount": 120,
        "notifications_status": 1,
        "transcription_language": "rus",
        "result_format": "text",
    }

    db_helper = DbHelper()
    db_helper.insert_row("users", base_param_user)

    kb = [
        [types.KeyboardButton(text="🎥 Видео на Ютуб")],
        [types.KeyboardButton(text="🎤 Голосовое сообщение")],
        [types.KeyboardButton(text="📹 Видеосообщение")],
        [types.KeyboardButton(text="👤 Личный кабинет")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, input_field_placeholder='Воспользуйтесь меню:')

    message_text = """
Привет! Я бот для транскрибации и суммаризации аудио и видео.
  
Отправь мне: 
    - Ссылку на YouTube видео  
    - Голосовое сообщение  
    - Кружочек (видеосообщение) 
    
Я преобразую аудио в текст или сделаю краткое содержание.  
В день доступно токенов: 120 (это ~120 минут аудио)
    """

    await message.answer(text=message_text, reply_markup=keyboard)