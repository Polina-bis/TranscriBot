from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(F.text.endswith("Личный кабинет"))
async def start_settings(message: types.Message, state: FSMContext):
    pass