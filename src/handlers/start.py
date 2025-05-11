from aiogram import types, Router
from aiogram.filters import Command

router = Router()

@router.message(Command('start'))
async def start(message: types.Message):
    # TODO создаем пользователя
    user_id = message.from_user.id

    kb = [
        [types.KeyboardButton(text="Видео на Ютуб")],
        [types.KeyboardButton(text="Голосовое сообщение")],
        [types.KeyboardButton(text="Видеосообщение")],
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
Доступно токенов: 120 (это ~120 минут аудио)
    """

    await message.answer(text=message_text, reply_markup=keyboard)