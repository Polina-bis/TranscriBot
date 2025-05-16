from aiogram.fsm.state import State, StatesGroup

class CircleStates(StatesGroup):
    wait_circle = State()
    wait_doing = State()