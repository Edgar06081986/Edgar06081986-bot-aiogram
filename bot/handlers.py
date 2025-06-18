from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message,FSInputFile, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext
from datetime import datetime
from bot.services.google_drive_service import google_drive
import os
from bot.config import Config

from bot.keyboards import (
    get_main_menu_keyboard,
    get_format_keyboard,
    get_paper_type_keyboard,
    get_confirm_keyboard,
    get_contact_keyboard,
    get_vizitki_format_keyboard,
    get_listovki_format_keyboard,
    get_wide_format_keyboard,
    get_cancel_keyboard,
    
)
from bot.states import OrderStates
from bot.logger import log_user_event, LogTypesEnum
from bot.services.google_api_service import google_api
import os
from PIL import Image, ImageDraw
import io

async def save_photo_with_crop_line(message, photo_file_id, order_id):
    file = await message.bot.get_file(photo_file_id)
    file_path = file.file_path
    os.makedirs("images", exist_ok=True)
    destination = f"images/{order_id}.jpg"
    buf = io.BytesIO()
    await message.bot.download_file(file_path, buf)
    buf.seek(0)
    image = Image.open(buf).convert("RGB")
    draw = ImageDraw.Draw(image)
    width, height = image.size
    margin = 10
    line_width = 3
    draw.rectangle(
        [margin, margin, width - margin, height - margin],
        outline="red",
        width=line_width
    )
    image.save(destination, "JPEG")
    return destination

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
    services = """
1. Печать визиток 
Создаем стильные и качественные визитки на мелованной, дизайнерской или плотной бумаге. Доступна полноцветная печать, цифровая,офсет фольгирование. Визитки любой формы, делаем контурную резку и ламинацию. 

2. Печать буклетов  
Изготовление рекламных буклетов любого формата и формы с фальцовкой (сгибом). Глянцевая или матовая ламинация для защиты и презентабельного вида. 

3. Печать листовок  
Яркие листовки на любой бумаге (от 130 - 150г). Подходят для промоакций, рекламы и мероприятий. Любой формы и размера.

4. Изготовление брошюр  
Печать брошюр с мягким переплетом (на скрепке или пружине). Идеально для каталогов, презентаций и инструкций.

5. Печать каталогов и журналов  
Профессиональная печать многостраничных изданий с обложкой из плотного картона.

6. Создание стильных календарей  
Перекидные, карманные и настольные календари с индивидуальным дизайном. Печать на мелованной бумаге или плотном картоне.

7. Печать плакатов  
Яркие постеры форматов А3, А2, А1 и больше. Подходят для интерьера, рекламы и мероприятий.



8. Печать на самоклеящейся пленке  и бумажной самоклейке
Наклейки для рекламы, декора, маркировки. Доступны разные виды пленки (матовая, глянцевая, прозрачная) и бумажная самоклейка.

9. Послепечатная обработка  
- Ламинирование – защита от влаги и повреждений (матовая/глянцевая пленка).
- Биговка – подготовка сгибов для буклетов и открыток.
- Фальцовка – аккуратные сгибы многостраничных изделий.
- Фольгирование – нанесение золотой, серебряной или цветной фольги для премиального вида.

10. Широкоформатная печать  
Печать чертежей, баннеров, постеров, стендов и интерьерной графики больших форматов.

11. Изготовление виниловых магнитов  
Яркие магниты на холодильник с вашим дизайном. Глянцевая или матовая поверхность, стойкие краски.

12. Изготовление наклеек и стикерпаков  
Наклейки разных форм и размеров. Возможна плоттерная резка по контуру для сложных форм.

13. Плоттерная резка  
Точная вырубка наклеек, трафаретов, элементов декора из пленки, картона, оракала и других материалов.

14. Печать, копирование, сканирование  
Черно-белая и цветная печать документов, увеличение/уменьшение масштаба, высококачественное сканирование, сканирование архивных документов.

15. Наружная реклама  
- Печать баннеров, растяжек, вывесок.
- Изготовление мобильных стендов и табличек.
- Печать на пленке

16. Фотопечать  
Печать фото в высоком разрешении на глянцевой, матовой. 

17. Фото на документы  
Срочное изготовление фото на паспорт, водительские права, визу и другие документы.

18. Брошюровка и твердый переплет  
- Мягкий переплет (на скобе, пружине или термоклее).
- Твердый переплет на металлический канал.

19. Изготовление печатей и штампов  
- Печати для ИП и ООО.
- Факсимиле.
- Автоматическая и ручная оснастки.

20. Разработка и корректировка макетов
-Восстановление фотографий
- Создание логотипов
- Корректировка макетов
- Работа с текстом
"""
    await message.answer(f"Наши услуги:\n{services}")

# --- Процесс заказа ---

@router.message(F.text == "Заказать оформление")
async def start_order(message: Message, state: FSMContext):
    await state.set_state(OrderStates.choosing_format)
    await message.answer(
        "Выбор формата:",
        reply_markup=get_format_keyboard()
    )

# @router.message(OrderStates.choosing_format, F.text)
# async def choose_format(message: Message, state: FSMContext):
#     format_ = message.text
#     if format_ not in ["Листовки", "Визитки", "Широкоформатная печать", "Журналы,Брошюры"]:
#         await message.answer("Пожалуйста, выберите формат из списка.", reply_markup=get_format_keyboard())
#         return
#     await state.update_data(format=format_)
#     await state.set_state(OrderStates.choosing_options)
   
    
@router.message(OrderStates.choosing_format, F.text == "Листовки")
async def choose_listovki(message: Message, state: FSMContext):
    await message.answer(
        """
        Цветовая палитра CMYK,300dpi
        Бумага (130-150г.)
        """
        )
    
    await message.answer(
        "Выберите формат листовки:",
        reply_markup=get_listovki_format_keyboard()
    )


@router.message(OrderStates.choosing_format, F.text == "Визитки")
async def choose_vizitki(message: Message, state: FSMContext):
    await message.answer(
        "5мм безопасного поля с каждой стороны, цветовая палитра CMYK, 300dpi"
    )
    await message.answer(
        "Выберите формат визитки:",
        reply_markup=get_vizitki_format_keyboard()
    )
    

@router.message(OrderStates.choosing_format, F.text == "Широкоформатная печать")
async def choose_wide_format(message: Message, state: FSMContext):
    
    await message.answer(
        "ℹ️ Нестандартные размеры (по требованию клиента)"
    )
    await message.answer(
        "Выберите формат широкоформатной печати:",
        reply_markup=get_wide_format_keyboard()
    )

@router.message(OrderStates.choosing_format, F.text == "Журналы,Брошюры")
async def choose_journals(message: Message, state: FSMContext):
    await state.update_data(format="Журналы,Брошюры")
    await state.set_state(OrderStates.choosing_options)
    await message.answer(
        "Выберите тип бумаги для журналов или брошюр:",
        reply_markup=get_paper_type_keyboard()
    )


# Обработка выбора формата для всех категорий
@router.message(OrderStates.choosing_format, F.text.in_([
    "A7 (109х78 мм)", "A6 (152х109 мм)", "A5 (214х148 мм)", "A4 (301х214 мм)",
    "Стандартные визитки (94x54 мм)", "Евровизитки (89x59 мм)",
    "A2 (420x594 мм)", "A1 (594x841 мм)", "A0 (841x1189 мм)",
]))
async def choose_any_format(message: Message, state: FSMContext):
    await state.update_data(format=message.text)
    await state.set_state(OrderStates.choosing_options)
    await message.answer(
        "Выберите тип бумаги:",
        reply_markup=get_paper_type_keyboard()
    )


@router.message(OrderStates.choosing_options, F.text.in_(["Глянцевая", "Матовая", "Без разницы"]))
async def choose_paper_type(message: Message, state: FSMContext):
    await state.update_data(option=message.text)
    await state.set_state(OrderStates.uploading_image)
    await message.answer(
        "Пожалуйста, отправьте изображение для печати.",
        reply_markup=get_cancel_keyboard()
    )



@router.message(OrderStates.uploading_image, F.photo)
async def upload_image(message: Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(photo_file_id=photo.file_id)
    await state.set_state(OrderStates.preview_and_confirm)
    data = await state.get_data()
    price = calculate_price(data.get("format"), data.get("option"))
    order_id = generate_order_id(message.from_user.id)
    processed_path = await save_photo_with_crop_line(message, photo.file_id, order_id)
    await message.answer_photo(
    FSInputFile(processed_path),
    caption=f"Вот предпросмотр вашего фото с линией обрезки.\nСтоимость: {price}₽\n\nПодтвердите заказ?",
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
     # Ссылка на фото в Google Drive

    # Сохраняем фото локально
    local_path = await save_photo(message, data["photo_file_id"], order_id)
    
    # Загружаем фото на Google Drive
    image_link = google_drive.upload_file(
        file_path=local_path,
        file_name=f"{order_id}.jpg",
        folder_id=Config.GOOGLE_FOLDER_IMAGES_ID
    )

    # Удаляем локальный файл
    os.remove(local_path)

    # Сохраняем заказ в Google Sheets
    values = [[order_id, contact, data.get("format"), price, date,image_link]]
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