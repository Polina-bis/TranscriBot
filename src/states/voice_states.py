from aiogram.fsm.state import State, StatesGroup

class VoicesStates(StatesGroup):
    wait_voice = State()