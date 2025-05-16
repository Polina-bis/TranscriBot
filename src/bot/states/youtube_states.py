from aiogram.fsm.state import State, StatesGroup

class YoutubeStates(StatesGroup):
    wait_link = State()
    wait_doing = State()