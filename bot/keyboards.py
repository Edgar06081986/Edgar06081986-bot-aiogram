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
        [KeyboardButton(text="Листовки"), KeyboardButton(text="Визитки")],
        [KeyboardButton(text="Широкоформатная печать")],
        [KeyboardButton(text="Журналы,Брошюры")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_listovki_format_keyboard():
    buttons = [
        [KeyboardButton(text="A7 (109х78 мм)")],
        [KeyboardButton(text="A6 (152х109 мм)")],
        [KeyboardButton(text="A5 (214х148 мм)")],
        [KeyboardButton(text="A4 (301х214 мм)")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)



def get_wide_format_keyboard():
    buttons = [
        [KeyboardButton(text="A2 (420x594 мм)")],
        [KeyboardButton(text="A1 (594x841 мм)")],
        [KeyboardButton(text="A0 (841x1189 мм)")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_vizitki_format_keyboard():
    buttons = [
        [KeyboardButton(text="Стандартные визитки (94x54 мм)")],
        [KeyboardButton(text="Евровизитки (89x59 мм)")],
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