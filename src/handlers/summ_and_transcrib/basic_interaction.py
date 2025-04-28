from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(F.text.endswith("Видеосообщение"))
async def start_recommendations(message: types.Message, state: FSMContext):
    pass