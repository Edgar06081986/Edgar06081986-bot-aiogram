from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message,FSInputFile, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from datetime import datetime
import os
from bot.config import Config

from bot.keyboards import (
    get_main_menu_keyboard,
    get_format_keyboard,
    get_paper_type_keyboard,
    get_confirm_keyboard,
    get_contact_keyboard,
    get_vizitki_format_keyboard,
    get_vizitki_tirazh_keyboard,
    get_side_vizitki_keyboard,
    get_listovki_format_keyboard,
    get_wide_format_keyboard,
    get_cancel_keyboard,
    get_listovki_side_keyboard,
    get_listovki_tirazh_keyboard,
    get_vizitki_tirazh_keyboard,
    get_side_vizitki_keyboard,
    get_wide_tirazh_keyboard,
    get_journals_side_keyboard,
    get_journals_format_keyboard,
    get_journals_tirazh_keyboard
        
)


from bot.states import OrderStates
from bot.logger import log_user_event, LogTypesEnum
from bot.services.google_api_service import google_api
from bot.services.google_drive_service import google_drive
import os
from PIL import Image, ImageDraw
import io
import logging


# Размеры в мм: (дообрезной_ширина, дообрезной_высота, безопасная_ширина, безопасная_высота)
LISTOVKI_SIZES = {
    "A7":  (109, 78, 105, 74),
    "A6":  (152, 109, 148, 105),
    "A5":  (214, 148, 210, 148),
    "A4":  (301, 214, 297, 210),
}

VIZITKI_SIZES ={ 
    "Стандартные визитки": (94, 54, 90, 50),
    "Евровизитки": (89, 59, 85, 55),
}

WIDE_SIZES = {
    "A2": (602,428, 594,420),
    "A1": (849,602, 841,594),
    "A0": (1197,849,1189,841 ),
}

JOURNAL_SIZES = {
    "A7":  (109, 78, 105, 74),
    "A6":  (152, 109, 148, 105),
    "A5":  (214, 148, 210, 148),
    "A4":  (301, 214, 297, 210),
}

import PIL

# ...existing code...

async def save_photo_with_crop_line(message, photo_file_id, order_id, format_short=None):
    file = await message.bot.get_file(photo_file_id)
    file_path = file.file_path
    os.makedirs("images", exist_ok=True)
    destination = f"images/{order_id}.jpg"
    buf = io.BytesIO()
    await message.bot.download_file(file_path, buf)
    buf.seek(0)

    # --- Получаем размеры для выбранного формата ---
    if format_short in LISTOVKI_SIZES:
        bleed_w_mm, bleed_h_mm, safe_w_mm, safe_h_mm = LISTOVKI_SIZES[format_short]
    elif format_short in VIZITKI_SIZES:
        bleed_w_mm, bleed_h_mm, safe_w_mm, safe_h_mm = VIZITKI_SIZES[format_short]
    elif format_short in WIDE_SIZES:
        bleed_w_mm, bleed_h_mm, safe_w_mm, safe_h_mm = WIDE_SIZES[format_short]
    elif format_short in JOURNAL_SIZES:
        bleed_w_mm, bleed_h_mm, safe_w_mm, safe_h_mm = JOURNAL_SIZES[format_short]
    else:
        image = Image.open(buf).convert("RGB")
        draw = ImageDraw.Draw(image)
        width, height = image.size
        draw.rectangle([10, 10, width-10, height-10], outline="red", width=3)
        image.save(destination, "JPEG")
        return destination

    # --- Масштабируем изображение так, чтобы оно полностью заполнило дообрезной размер ---
    original = Image.open(buf).convert("RGB")
    orig_w, orig_h = original.size

    # 1. Подбираем scale так, чтобы обе стороны <= 1280 px
    max_canvas_side = max(bleed_w_mm, bleed_h_mm)
    scale = min(1280 // max_canvas_side, 10)
    scale = max(scale, 1)  # чтобы не было нуля

    canvas_w = int(bleed_w_mm * scale)
    canvas_h = int(bleed_h_mm * scale)

    # 2. Масштабируем изображение с сохранением пропорций, чтобы оно полностью ЗАПОЛНИЛО холст (cover)
    ratio = max(canvas_w / orig_w, canvas_h / orig_h)
    new_w = int(orig_w * ratio)
    new_h = int(orig_h * ratio)
    resized = original.resize((new_w, new_h), PIL.Image.LANCZOS)

    # 3. Обрезаем по центру до нужного размера (crop)
    left = (new_w - canvas_w) // 2
    top = (new_h - canvas_h) // 2
    cropped = resized.crop((left, top, left + canvas_w, top + canvas_h))

    draw = ImageDraw.Draw(cropped)

    # 4. Масштаб для линий (1 мм = scale px)
    safe_w_px = safe_w_mm * scale
    safe_h_px = safe_h_mm * scale

    # 5. Координаты для безопасной зоны (по центру)
    safe_left = (canvas_w - safe_w_px) / 2
    safe_top = (canvas_h - safe_h_px) / 2
    safe_right = safe_left + safe_w_px
    safe_bottom = safe_top + safe_h_px

    # 6. Нарисовать дообрезную линию (синяя)
    draw.rectangle([0, 0, canvas_w-1, canvas_h-1], outline="blue", width=3)
    # 7. Нарисовать безопасную линию (красная)
    draw.rectangle([safe_left, safe_top, safe_right, safe_bottom], outline="red", width=3)

    cropped.save(destination, "JPEG")
    return destination



# --- Прайс-лист ---
PRICE_LIST = {
    "Листовки": {
        "A7": {
            "one_side": {50: 770, 100: 1100, 200: 1550, 300: 1850, 400: 2100, 500: 2400},
            "two_side": {50: 1000, 100: 1450, 200: 2000, 300: 2400, 400: 2700, 500: 3100},
        },
        "A6": {
            "one_side": {50: 1100, 100: 1560, 200: 2200, 300: 2650, 400: 2960, 500: 3400},
            "two_side": {50: 1450, 100: 2050, 200: 2800, 300: 3400, 400: 3850, 500: 4400},
        },
        "A5": {
            "one_side": {50: 1700, 100: 2350, 200: 3250, 300: 3950, 400: 4450, 500: 5100},
            "two_side": {50: 2450, 100: 3500, 200: 4900, 300: 5900, 400: 6600, 500: 7600},
        },
        "A4": {
            "one_side": {50: 2650, 100: 3750, 200: 5250, 300: 6300, 400: 7100, 500: 8100},
            "two_side": {50: 3900, 100: 5600, 200: 7850, 300: 9400, 400: 10650, 500: 12150},
        },
    },
    "Визитки": {
        "one_side,color": {  # односторонние,цветные
            50: 750,
            100: 850,
            200: 1400,
            300: 1950,
            500: 2900,
            1000: 4900,
        },
        "two_side,color": {  # двусторонние,цветные
            50: 850,
            100: 1000,
            200: 1900,
            300: 2600,
            500: 3700,
            1000: 6300,
        }
    },
    "Широкоформатная печать": {
        "black_white": {  # Черно-белая печать, бумага 80 г/м2
            "A2": {
                (1, 10): 160,
                (11, 30): 130,
                (31, 100): 110,
                (101, 9999): 90,
            },
            "A1": {
                (1, 10): 190,
                (11, 30): 160,
                (31, 100): 140,
                (101, 9999): 110,
            },
            "A0": {
                (1, 10): 270,
                (11, 30): 230,
                (31, 100): 210,
                (101, 9999): 160,
            },
        }
    },
    "Журналы, Брошюры": {
        "A7": {
            "one_side": {50: 770, 100: 1100, 200: 1550, 300: 1850, 400: 2100, 500: 2400},
            "two_side": {50: 1000, 100: 1450, 200: 2000, 300: 2400, 400: 2700, 500: 3100},
        },
        "A6": {
            "one_side": {50: 1100, 100: 1560, 200: 2200, 300: 2650, 400: 2960, 500: 3400},
            "two_side": {50: 1450, 100: 2050, 200: 2800, 300: 3400, 400: 3850, 500: 4400},
        },
        "A5": {
            "one_side": {50: 1700, 100: 2350, 200: 3250, 300: 3950, 400: 4450, 500: 5100},
            "two_side": {50: 2450, 100: 3500, 200: 4900, 300: 5900, 400: 6600, 500: 7600},
        },
        "A4": {
            "one_side": {50: 2650, 100: 3750, 200: 5250, 300: 6300, 400: 7100, 500: 8100},
            "two_side": {50: 3900, 100: 5600, 200: 7850, 300: 9400, 400: 10650, 500: 12150},
        },
    }
}


def calculate_price(format_: str, option: str, tirazh: int = 50, side: str = "one_side") -> int:
    # Для листовок
    if format_ in ["A7", "A6", "A5", "A4"]:
        # side: "one_side" или "two_side"
        try:
            return PRICE_LIST["Листовки"][format_][side][tirazh]
        except KeyError:
            return 0
    # Для визиток
    elif side in ["one_side,color", "two_side,color"]:
        try:
            return PRICE_LIST["Визитки"][side][tirazh]
        except KeyError:
            return 0
        
    # Для широкоформатной печати
    elif format_ in ["A2", "A1", "A0"]:
        try:
            for qty_range, price in PRICE_LIST["Широкоформатная печать"]["black_white"][format_].items():
                if qty_range[0] <= tirazh <= qty_range[1]:
                    return price
            return 0
        except KeyError:
            return 0
        
    # Для  журналов и брошюр
    if format_ in ["A7", "A6", "A5", "A4"]:
        # side: "one_side" или "two_side"
        try:
            return PRICE_LIST["Листовки"][format_][side][tirazh]
        except KeyError:
            return 0    

def generate_order_id(user_id: int) -> str:
    return f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

async def save_photo(message: Message, photo_file_id: str, order_id: str):
    file = await message.bot.get_file(photo_file_id)
    file_path = file.file_path
    os.makedirs("images", exist_ok=True)
    destination = f"images/{order_id}.jpg"
    await message.bot.download_file(file_path, destination)
    return destination

router = Router()

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
    # Список услуг
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

   
# --- ЛИСТОВКИ ---    
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

# 1. После выбора формата "Листовки" — спрашиваем тираж
@router.message(OrderStates.choosing_format, F.text.in_([
    "A7 (105х74 мм)", "A6 (148х105 мм)", "A5 (210х148 мм)", "A4 (297х210 мм)"
]))
async def choose_listovki_format(message: Message, state: FSMContext):
    format_short = message.text.split()[0]  # "A7", "A6" и т.д.
    await state.update_data(format=format_short)
    await state.set_state(OrderStates.choosing_tirazh)
    await message.answer(
        "Выберите тираж:",
        reply_markup=get_listovki_tirazh_keyboard()
    )

# 2. После выбора тиража — спрашиваем сторону печати
@router.message(OrderStates.choosing_tirazh, F.text.in_(["50", "100", "200", "300", "400", "500"]))
async def choose_tirazh(message: Message, state: FSMContext):
    await state.update_data(tirazh=int(message.text))
    await state.set_state(OrderStates.choosing_side)
    await message.answer(
        "Выберите тип печати:",
        reply_markup=get_listovki_side_keyboard()
    )

# 3. После выбора стороны печати — спрашиваем тип бумаги
@router.message(OrderStates.choosing_side, F.text.in_(["Односторонняя", "Двусторонняя"]))
async def choose_side(message: Message, state: FSMContext):
    side = "one_side" if message.text == "Односторонняя" else "two_side"
    await state.update_data(side=side)
    await state.set_state(OrderStates.choosing_options)
    await message.answer(
        "Выберите тип бумаги:",
        reply_markup=get_paper_type_keyboard()
    )


# --- ВИЗИТКИ ---
@router.message(OrderStates.choosing_format, F.text == "Визитки")
async def choose_vizitki(message: Message, state: FSMContext):
    
    # Дополнительно отправьте информацию о дизайнерской бумаге и услугах
    await message.answer(
        "5мм безопасного поля с каждой стороны, цветовая палитра CMYK, 300dpi"
        "💎 *Дизайнерская бумага* (надбавка за 1 лист):\n"
        "• VERONA/WILD/Лен белый/слоновая кость/шелк — 100₽\n"
        "• Хромолокс/Comet/MAJESTIC/Крафт — 160₽\n"
        "• Touche Cover — 250₽\n\n"
        "🛠️ *Дополнительные услуги*:\n"
        "• Макет визитки 'под ключ'/правка — от 500/от 350₽\n"
        "• Фольгирование одна сторона (за 100 шт.) — 650₽\n"
        "• Фольгирование две стороны (за 100 шт.) — 1300₽\n"
        "• Скругление углов/сверление 5мм (за 100 шт.) — 200₽\n"
        "• Ламинирование одна сторона (за 100 шт.) — 360₽\n"
        "• Ламинирование две стороны (за 100 шт.) — 490₽\n",
        parse_mode="Markdown"
    )
    await message.answer(
        "Выберите формат визитки:",
        reply_markup=get_vizitki_format_keyboard() 
    )
    

# 1. После выбора формата "Визитки" — спрашиваем тираж

@router.message(OrderStates.choosing_format, F.text.in_([
   "Стандартные визитки (90x50 мм)", "Евровизитки (85x55 мм)" 
]))
async def choose_vizitki_format(message: Message, state: FSMContext):
    # Берём только нужную часть до скобки
    format_short = message.text.split(" (")[0]  # "Стандартные визитки" или "Евровизитки"
    await state.update_data(format=format_short)
    await state.set_state(OrderStates.choosing_vizitki_tirazh)
    await message.answer(
        "Выберите тираж:",
        reply_markup=get_vizitki_tirazh_keyboard()
    )

# 2. После выбора тиража — спрашиваем сторону печати
@router.message(OrderStates.choosing_vizitki_tirazh, F.text.in_(["50", "100", "200", "300", "400", "500","1000"]))
async def choose_vizitki_tirazh(message: Message, state: FSMContext):
    await state.update_data(tirazh=int(message.text))
    await state.set_state(OrderStates.choosing_vizitki_side)
    await message.answer(
        "Выберите формат печати:",
        reply_markup=get_side_vizitki_keyboard()
    )

# 3. После выбора стороны печати — спрашиваем тип бумаги
@router.message(OrderStates.choosing_vizitki_side, F.text.in_(["Цветные \n односторонние", "Цветные \n двусторонние"]))
async def choose_vizitki_side(message: Message, state: FSMContext):
    side = "one_side,color" if message.text == "Цветные,односторонние" else "two_side,color"
    await state.update_data(side=side)
    await state.set_state(OrderStates.choosing_options)
    await message.answer(
        "Выберите тип бумаги:",
        reply_markup=get_paper_type_keyboard()
    )
    

# --- ШИРОКОФОРМАТНАЯ ПЕЧАТЬ ---
@router.message(OrderStates.choosing_format, F.text == "Широкоформатная печать")
async def choose_wide(message: Message, state: FSMContext):
    
    await message.answer(
        "ℹ️ Нестандартные размеры (по требованию клиента)"
    )
    await message.answer(
        "Выберите формат широкоформатной печати:",
        reply_markup=get_wide_format_keyboard()
    )


@router.message(OrderStates.choosing_format, F.text.in_([
    "A2 (420x594 мм)", "A1 (594x841 мм)", "A0 (841x1189 мм)",
]))
async def choose_wide_format(message: Message, state: FSMContext):
    format_short = message.text.split()[0]  # "A2", "A1", "A0"
    await state.update_data(format=format_short)
    await state.set_state(OrderStates.choosing_tirazh)
    await message.answer("Выберите тираж:"
        ,
        reply_markup= get_wide_tirazh_keyboard()
    )



# 2. После выбора тиража — спрашиваем сторону печати
@router.message(OrderStates.choosing_tirazh, F.text.in_(["1-10", "11-30", "31-100", "101-9999"]))
async def choose_wide_tirazh(message: Message, state: FSMContext):
    min_qty = int(message.text.split('-')[0])
    await state.update_data(tirazh=min_qty)
    await state.set_state(OrderStates.choosing_options)
    await message.answer(
        "Выберите тип бумаги:",
        reply_markup=get_paper_type_keyboard()
    )




# --- ЖУРНАЛЫ И БРОШЮРЫ ---
@router.message(OrderStates.choosing_format, F.text == "Журналы,Брошюры")
async def choose_journals(message: Message, state: FSMContext):
    await state.update_data(format="Журналы,Брошюры")
    await state.set_state(OrderStates.choosing_format)
    await message.answer(
        "Выберите формат бумаги для журналов или брошюрлистовки:",
        reply_markup=get_journals_format_keyboard()
    )

# 1. После выбора формата "Журналы и Брошюры" — спрашиваем тираж
@router.message(OrderStates.choosing_format, F.text.in_([
    "A7 (105х74 мм)", "A6 (148х105 мм)", "A5 (210х148 мм)", "A4 (297х210 мм)"
]))
async def choose_journals_format(message: Message, state: FSMContext):
    format_short = message.text.split()[0]  # "A7", "A6" и т.д.
    await state.update_data(format=format_short)
    await state.set_state(OrderStates.choosing_tirazh)
    await message.answer(
        "Выберите тираж:",
        reply_markup=get_journals_tirazh_keyboard()
    )

# 2. После выбора тиража — спрашиваем сторону печати
@router.message(OrderStates.choosing_tirazh, F.text.in_(["50", "100", "200", "300", "400", "500"]))
async def choose_journals_tirazh(message: Message, state: FSMContext):
    await state.update_data(tirazh=int(message.text))
    await state.set_state(OrderStates.choosing_side)
    await message.answer(
        "Выберите тип печати:",
        reply_markup=get_listovki_side_keyboard()
    )

# 3. После выбора стороны печати — спрашиваем тип бумаги
@router.message(OrderStates.choosing_side, F.text.in_(["Односторонняя", "Двусторонняя"]))
async def choose_journals_side(message: Message, state: FSMContext):
    side = "one_side" if message.text == "Односторонняя" else "two_side"
    await state.update_data(side=side)
    await state.set_state(OrderStates.choosing_options)
    await message.answer(
        "Выберите тип бумаги для журналов или брошюр:",
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
    price = calculate_price(
        data.get("format"),
        data.get("option"),
        tirazh=int(data.get("tirazh", 50)),  # по умолчанию 50
        side=data.get("side", "one_side")    # по умолчанию односторонняя
    )
    order_id = generate_order_id(message.from_user.id)
    processed_path = await save_photo_with_crop_line(
    message, photo.file_id, order_id, format_short=data.get("format")
)
    await message.answer_photo(
    FSInputFile(processed_path),
    caption=f"Вот предпросмотр вашего фото с безопасной линией и с линией обрезки.\nСтоимость: {price}₽\n\nПодтвердите заказ?",
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
    price = calculate_price(
        data.get("format"),
        data.get("option"),
        tirazh=int(data.get("tirazh", 50)),  # по умолчанию 50
        side=data.get("side", "one_side")    # по умолчанию односторонняя
    )
    date = datetime.now().strftime("%d.%m.%Y %H:%M")
     # Ссылка на фото в Google Drive

    # Сохраняем фото локально
    local_path = await save_photo(message, data["photo_file_id"], order_id)
    print(f"Сохраняем файл: {local_path}")  # <-- ВСТАВЬ СЮДА

    # Загружаем фото на Google Drive
    image_link = google_drive.upload_file(
        file_path=local_path,
        file_name=f"{order_id}.jpg",
        folder_id=Config.GOOGLE_FOLDER_IMAGES_ID
    )

    print(f"Удаляем файл: {local_path}")  # <-- И СЮДА


    # Удаляем локальный файл
    if os.path.exists(local_path):
        os.remove(local_path)
        print(f"Файл {local_path} удалён")
    else:
        print(f"Файл {local_path} не найден для удаления")

    # Сохраняем заказ в Google Sheets
    values = [[order_id, contact, data.get("format"), price, date,image_link]]
    await google_api.append_sheet_data("Заказы", values)

    # ОЧИСТКА ВСЕХ ВРЕМЕННЫХ ФАЙЛОВ
    import glob
    for file in glob.glob("images/*.jpg"):
        try:
            os.remove(file)
            print(f"Удалён временный файл: {file}")
        except Exception as e:
            print(f"Ошибка при удалении {file}: {e}")


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