from aiogram.fsm.state import StatesGroup, State

class OrderStates(StatesGroup):
    choosing_format = State()
    choosing_tirazh = State()
    choosing_side = State()
    choosing_options = State()
    uploading_image = State()
    preview_and_confirm = State()
    waiting_for_contact = State()