from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# --- Главное меню ---
def get_main_menu_keyboard():
    buttons = [
        [KeyboardButton(text="Информация о центре")],
        [KeyboardButton(text="Наши услуги")],
        [KeyboardButton(text="Заказать оформление")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# --- Форматы ---
def get_format_keyboard():
    buttons = [
        [KeyboardButton(text="Листовки"), KeyboardButton(text="Визитки")],
        [KeyboardButton(text="Широкоформатная печать")],
        [KeyboardButton(text="Журналы,Брошюры")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# --- ЛИСТОВКИ ---
def get_listovki_format_keyboard():
    buttons = [
        [KeyboardButton(text="A7 (105х74 мм)")],
        [KeyboardButton(text="A6 (148х105 мм)")],
        [KeyboardButton(text="A5 (210х148 мм)")],
        [KeyboardButton(text="A4 (297х210 мм)")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_listovki_tirazh_keyboard():
    buttons = [
        [KeyboardButton(text="50"), KeyboardButton(text="100"), KeyboardButton(text="200")],
        [KeyboardButton(text="300"), KeyboardButton(text="400"), KeyboardButton(text="500")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_listovki_side_keyboard():
    buttons = [
        [KeyboardButton(text="Односторонняя"), KeyboardButton(text="Двусторонняя")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# --- ВИЗИТКИ ---
def get_vizitki_format_keyboard():
    buttons = [
        [KeyboardButton(text="Стандартные визитки (90x50 мм)")],
        [KeyboardButton(text="Евровизитки (85x55 мм)")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_vizitki_tirazh_keyboard():
    buttons = [
        [KeyboardButton(text="50"), KeyboardButton(text="100"), KeyboardButton(text="200")],
        [KeyboardButton(text="300"), KeyboardButton(text="400"), KeyboardButton(text="500")],
        [KeyboardButton(text="1000"), KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_side_vizitki_keyboard():
    buttons = [
        [KeyboardButton(text="Цветные \n односторонние"), KeyboardButton(text="Цветные \n двусторонние")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# --- ШИРОКОФОРМАТНАЯ ПЕЧАТЬ ---
def get_wide_format_keyboard():
    buttons = [
        [KeyboardButton(text="A2 (420x594 мм)")],
        [KeyboardButton(text="A1 (594x841 мм)")],
        [KeyboardButton(text="A0 (841x1189 мм)")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_wide_tirazh_keyboard():
    buttons = [
        [KeyboardButton(text="1-10"), KeyboardButton(text="11-30"), KeyboardButton(text="31-100")],
        [KeyboardButton(text="101-9999"),KeyboardButton(text="❌ Отмена"),]    
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# --- ЖУРНАЛЫ, БРОШЮРЫ ---
def get_journals_format_keyboard():
    buttons = [
        [KeyboardButton(text="A7 (105х74 мм)")],
        [KeyboardButton(text="A6 (148х105 мм)")],
        [KeyboardButton(text="A5 (210х148 мм)")],
        [KeyboardButton(text="A4 (297х210 мм)")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_journals_tirazh_keyboard():
    buttons = [
        [KeyboardButton(text="50"), KeyboardButton(text="100"), KeyboardButton(text="200")],
        [KeyboardButton(text="300"), KeyboardButton(text="400"), KeyboardButton(text="500")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_journals_side_keyboard():
    buttons = [
        [KeyboardButton(text="Односторонняя"), KeyboardButton(text="Двусторонняя")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# --- Общие ---
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