from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from datetime import datetime
import os

from bot.keyboards import (
    get_main_menu_keyboard,
    get_format_keyboard,
    get_paper_type_keyboard,
    get_confirm_keyboard,
    get_contact_keyboard
)
from bot.states import OrderStates
from bot.logger import log_user_event, LogTypesEnum
from bot.services.google_api_service import google_api

router = Router()

# --- Прайс-лист ---
PRICE_LIST = {
    "10x15": 20,
    "15x21": 40,
    "Фото на документы": 100
}

def calculate_price(format_: str, option: str) -> int:
    base_price = PRICE_LIST.get(format_, 0)
    # Можно добавить наценку за опции, если нужно
    return base_price

def generate_order_id(user_id: int) -> str:
    return f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

async def save_photo(message: Message, photo_file_id: str, order_id: str):
    file = await message.bot.get_file(photo_file_id)
    file_path = file.file_path
    os.makedirs("images", exist_ok=True)
    destination = f"images/{order_id}.jpg"
    await message.bot.download_file(file_path, destination)
    return destination

# --- Главное меню ---

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Добро пожаловать в центр типографии!\nВыберите действие:",
        reply_markup=get_main_menu_keyboard()
    )

@router.message(F.text == "Информация о центре")
async def info_handler(message: Message):
    await message.answer(
        " FastEdition – современная сеть копировальных центров с быстрым и качественным исполнением "'\n'
        "🚀 Скорость и точность– мы ценим ваше время, поэтому выполняем заказы оперативно без потери качества."'\n'  
        "🖨️ Широкий спектр услуг:"'\n'  
        "- Печать визиток, буклетов, листовок"'\n'  
        "- Изготовление брошюр, каталогов, журналов"'\n'  
        "- Создание стильных календарей и плакатов"'\n'  
        "- Печать на фотобумаге, самоклеящейся пленке"'\n'  
        "- Послепечатная обработка (ламинирование, биговка, фальцовка, фольгирование)"  
        "- Широкоформатная печать"'\n'
        "- Изготовление виниловых магнитов"'\n'
        "- Изготовление наклеек, стикерпаков"'\n'
        "- Плоттерная резка"'\n'
        "- Печать, копирование, сканирование"'\n'
        "- Наружная реклама"'\n'
        "- Фотопечать"'\n'
        "- Фото на документы"'\n'
        "- Брошюровка, твердый переплет"'\n'
        "- печати и штампы"'\n'


        "💡 Современное оборудование – работаем на профессиональной технике для безупречного результата."'\n'  

        "🎨 Индивидуальный подход – поможем с дизайном или доработаем ваши макеты."'\n'  

        "📦 Доставка не предусмотрена, только самовывоз."'\n' 

        "Выбирайте FastEdition – где каждая деталь создается с заботой о вашем успехе!"'\n'  

        "📞 Свяжитесь с нами: +7 915 134 46 44 (телеграмм, ватсап) @fastedition (телеграм)"'\n'

    )

@router.message(F.text == "Наши услуги")
async def services_handler(message: Message):
    # services = await google_api.get_services_list()  # Если реализовано получение из таблицы
    services = "1. Фото 10x15 — 20₽\n2. Фото 15x21 — 40₽\n3. Фото на документы — 100₽"
    await message.answer(f"Наши услуги:\n{services}")

# --- Процесс заказа ---

@router.message(F.text == "Заказать оформление")
async def start_order(message: Message, state: FSMContext):
    await state.set_state(OrderStates.choosing_format)
    await message.answer(
        "Выберите формат фотографии:",
        reply_markup=get_format_keyboard()
    )

@router.message(OrderStates.choosing_format, F.text)
async def choose_format(message: Message, state: FSMContext):
    format_ = message.text
    if format_ not in PRICE_LIST:
        await message.answer("Пожалуйста, выберите формат из списка.", reply_markup=get_format_keyboard())
        return
    await state.update_data(format=format_)
    await state.set_state(OrderStates.choosing_options)
    await message.answer(
        "Выберите тип бумаги:",
        reply_markup=get_paper_type_keyboard()
    )

@router.message(OrderStates.choosing_options, F.text)
async def choose_options(message: Message, state: FSMContext):
    option = message.text
    if option not in ["Глянцевая", "Матовая", "Без разницы"]:
        await message.answer("Пожалуйста, выберите тип бумаги из списка.", reply_markup=get_paper_type_keyboard())
        return
    await state.update_data(option=option)
    await state.set_state(OrderStates.uploading_image)
    await message.answer(
        "Пожалуйста, отправьте фотографию (JPG/PNG, до 20 МБ):",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(OrderStates.uploading_image, F.photo)
async def upload_image(message: Message, state: FSMContext):
    photo = message.photo[-1]
    if photo.file_size > 20 * 1024 * 1024:
        await message.answer("Файл слишком большой. Максимальный размер — 20 МБ.")
        return
    await state.update_data(photo_file_id=photo.file_id)
    await state.set_state(OrderStates.preview_and_confirm)
    data = await state.get_data()
    price = calculate_price(data.get("format"), data.get("option"))
    await message.answer_photo(
        photo.file_id,
        caption=f"Вот предпросмотр вашего фото.\nСтоимость: {price}₽\n\nПодтвердите заказ?",
        reply_markup=get_confirm_keyboard()
    )

@router.message(OrderStates.preview_and_confirm, F.text == "✅ Подтвердить")
async def confirm_order(message: Message, state: FSMContext):
    await state.set_state(OrderStates.waiting_for_contact)
    await message.answer(
        "Пожалуйста, отправьте ваш номер телефона:",
        reply_markup=get_contact_keyboard()
    )

@router.message(OrderStates.preview_and_confirm, F.text == "❌ Отмена")
@router.message(OrderStates.choosing_format, F.text == "❌ Отмена")
@router.message(OrderStates.choosing_options, F.text == "❌ Отмена")
@router.message(OrderStates.uploading_image, F.text == "❌ Отмена")
@router.message(OrderStates.waiting_for_contact, F.text == "❌ Отмена")
async def cancel_order(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Заказ отменён.", reply_markup=get_main_menu_keyboard())

@router.message(OrderStates.waiting_for_contact, F.contact)
async def receive_contact(message: Message, state: FSMContext):
    data = await state.get_data()
    contact = message.contact.phone_number
    order_id = generate_order_id(message.from_user.id)
    price = calculate_price(data.get("format"), data.get("option"))
    date = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Сохраняем фото
    await save_photo(message, data["photo_file_id"], order_id)

    # Сохраняем заказ в Google Sheets
    values = [[order_id, contact, data.get("format"), price, date]]
    await google_api.append_sheet_data("Заказы", values)

    await state.clear()
    await message.answer(
        f"Спасибо! Ваш заказ принят.\n\n"
        f"Номер заказа: {order_id}\n"
        f"Формат: {data.get('format')}\n"
        f"Стоимость: {price}₽\n"
        f"Мы свяжемся с вами для подтверждения.",
        reply_markup=get_main_menu_keyboard()
    )
    log_user_event(LogTypesEnum.INFO, message.from_user.id, f"Оформлен заказ {order_id}")

@router.message(OrderStates.waiting_for_contact)
async def contact_error(message: Message):
    await message.answer("Пожалуйста, используйте кнопку для отправки номера телефона.", reply_markup=get_contact_keyboard())

@router.message()
async def unknown_message(message: Message):
    await message.answer("Пожалуйста, используйте кнопки меню.", reply_markup=get_main_menu_keyboard())