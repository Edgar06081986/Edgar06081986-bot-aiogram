from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

def get_main_menu_keyboard():
    buttons = [
        [KeyboardButton(text="Информация о центре")],
        [KeyboardButton(text="Наши услуги")],
        [KeyboardButton(text="Заказать оформление")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_format_keyboard():
    buttons = [
        [KeyboardButton(text="10x15"), KeyboardButton(text="15x21")],
        [KeyboardButton(text="Фото на документы")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_paper_type_keyboard():
    buttons = [
        [KeyboardButton(text="Глянцевая"), KeyboardButton(text="Матовая")],
        [KeyboardButton(text="Без разницы")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_confirm_keyboard():
    buttons = [
        [KeyboardButton(text="✅ Подтвердить")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_contact_keyboard():
    buttons = [
        [KeyboardButton(text="Поделиться контактом", request_contact=True)],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_cancel_keyboard():
    buttons = [
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)