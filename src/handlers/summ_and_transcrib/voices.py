import math
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.downloader.voice_dw import VoiceDownloader
from src.handlers.markups.choose_doing import markup_choose_doing
from src.handlers.summ_and_transcrib.message_text import voice_texts, create_answer_not_enough_tokens, \
    create_answer_message_in_queue
from src.states.voice_states import VoicesStates

router = Router()

@router.message(F.text.endswith("Голосовое сообщение"))
async def start_voices(message: types.Message, state: FSMContext):
    await message.answer(voice_texts["start_voices"])
    await state.set_state(VoicesStates.wait_voice)


@router.message(F.voice, VoicesStates.wait_voice)
async def download_voices(message: types.Message, state: FSMContext, bot: Bot):
    # проверка, что гс не менее 1 мин
    if message.voice.duration < 60:
        await message.answer(voice_texts["too_long"])
        await state.set_state(VoicesStates.wait_voice)
        return

    # скачиваем гс
    downloader = VoiceDownloader(bot)
    file_path = await downloader.download_source("src/data/cash/voices", message.voice.file_id)
    # сохраняем путь до гс
    await state.update_data({"voice_path": file_path})

    tokens = math.ceil(message.voice.duration / 60)
    await state.update_data({"tokens": tokens})

    await message.answer(voice_texts["choose_doing"], reply_markup=markup_choose_doing(tokens))
    await state.set_state(VoicesStates.wait_doing)


@router.message(VoicesStates.wait_voice)
async def download_voices(message: types.Message, state: FSMContext):
    markup = InlineKeyboardBuilder()
    chancel = types.InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel"
    )
    markup.add(chancel)

    await message.answer(voice_texts["wrong_media"], reply_markup=markup.as_markup())
    await state.set_state(VoicesStates.wait_voice)


@router.callback_query(F.data.in_({"transcribe", "summ"}) , VoicesStates.wait_doing)
async def process_voices(callback: types.CallbackQuery, state: FSMContext):
    # TODO запрос на оставшееся кол во токенов у пользователя
    current_tokens = 120
    data = await state.get_data()
    tokens = data["tokens"]

    # не хватает токенов
    if callback.message.text == "transcribe":
        if current_tokens < tokens:
            text = create_answer_not_enough_tokens(current_tokens, tokens)
            await callback.message.answer(text)
            await state.clear()
            return
    elif callback.message.text == "summ":
        if current_tokens < 2 * tokens:
            text = create_answer_not_enough_tokens(current_tokens, 2 * tokens)
            await callback.message.answer(text)
            await state.clear()
            return

    # TODO видео засовываем в очередь
    position = 2
    text = create_answer_message_in_queue(position)
    await callback.message.answer(text) # сообщение об ожидании в очереди

    # TODO обработка гс:
    #     здесь хотелось бы универсальную функцию где указываешь что хочешь сделать
    #     и ссылку на файл источник и она сует в очередь и выплелывает путь файла результата
    result_file = "src/data/cash/youtube/transcrib/c5Nh4g8zwyo"
    with open(result_file, 'r', encoding='utf-8') as file:
        result = file.read()
        if len(text) <= 4096: # проверка вместится ли результат в сообщение
            await callback.message.answer(result)
        else:
            # Отправляем файл, если текст слишком длинный
            file = FSInputFile(result_file)
            await callback.message.answer_document(file, caption=voice_texts["long_answer"])


@router.callback_query(F.text == "cancel", VoicesStates.wait_doing)
async def cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()