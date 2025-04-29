import math
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext

from src.downloader.voice_dw import VoiceDownloader
from src.handlers.markups.choose_doing import markup_choose_doing
from src.states.voice_states import VoicesStates

router = Router()

@router.message(F.text.endswith("Голосовое сообщение"))
async def start_voices(message: types.Message, state: FSMContext):
    message_text = """
Хорошо, я вас понял! Отправьте мне интересующее вас голосовое сообщение, а я с ним ознакомлюсь!  

Внимание! Голосовое сообщение должно быть не менее одной минуты
    """
    await message.answer(message_text)
    await state.set_state(VoicesStates.wait_voice)


@router.message(F.voice, VoicesStates.wait_voice)
async def download_voices(message: types.Message, state: FSMContext, bot: Bot):
    # проверка, что гс не менее 1 мин
    if message.voice.duration < 60:
        message_text = "К сожалению ваше сообщение меньше 1 минуты. Попробуйте отправить сообщение еще раз"
        await message.answer(message_text)
        await state.set_state(VoicesStates.wait_voice)
        return

    # скачиваем гс
    downloader = VoiceDownloader(bot)
    file_path = await downloader.download_source("src/data/cash/voices", message.voice.file_id)
    # сохраняем путь до гс
    await state.update_data({"voice_path": file_path})

    tokens = math.ceil(message.voice.duration / 60)

    message_text = """
Замечательный выбор!

Что мне сделать с этим аудио?     
    """
    await message.answer(message_text, reply_markup=markup_choose_doing(tokens))


@router.message(VoicesStates.wait_voice)
async def download_voices(message: types.Message, state: FSMContext):
    message_text = """
Извините, я не могу обработать такой тип сообщений

Я могу помочь только с:
    - Ссылки на YouTube
    - Голосовые сообщения
    - Видеосообщения
    
Попробуйте еще отправить голосовое сообщение!    
    """
    await message.answer(message_text)
    await state.set_state(VoicesStates.wait_voice)
