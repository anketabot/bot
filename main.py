#!/usr/bin/env python3
"""
@sovchirr - Telegram E'lon Bot
Single-file aiogram 3.x implementation
PostgreSQL + Railway + Rasm bilan e'lon
"""

import os
import asyncio
import asyncpg
from datetime import datetime
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramAPIError

# ============================================================
# CONFIG
# ============================================================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
CHANNEL_ID = os.getenv("CHANNEL_ID", "@sovchirr")
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/sovchirr")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:ksUmAcMyjgW**************************@tramway.proxy.rlwy.net:25886/railway")


KUYOV_IMAGES = {
    "kuyov_1": "AgACAgIAAxkBAANpafW0GS8joU1koM1fcZwyOgKLd_gAApITaxuDW7FLrZRTmWK70xQBAAMCAAN4AAM7BA",  # 1-variant
    "kuyov_2": "AgACAgIAAxkBAANrafW0Nt-944ACisItLE23a7KhockAApMTaxuDW7FLvVAq2wxPu7ABAAMCAAN4AAM7BA",  # 2-variant
}
KELIN_IMAGES = {
    "kelin_1": "AgACAgIAAxkBAANhafWz3mW99BCFhjT6-Lg_ZQimGzYAAo4TaxuDW7FL9wnSEedKwrEBAAMCAAN5AAM7BA",
    "kelin_2": "AgACAgIAAxkBAANjafWz8agqAnSX7Yq6zPt81vlGYmQAAo8TaxuDW7FLVrCKqNtxKaIBAAMCAAN5AAM7BA",
    "kelin_3": "AgACAgIAAxkBAANlafWz-wR1nHjrZ0SYd_inQX3MqdEAApATaxuDW7FLEE4DH6pkNHkBAAMCAAN4AAM7BA",
}
KUYOV2_IMAGE = "AgACAgIAAxkBAANnafW0D0VKI1z0rMQ1mpAjm791whsAApETaxuDW7FLPPbcNASW-d8BAAMCAAN4AAM7BA"  # 2-ro'zg'or uchun default
KELIN2_IMAGE = "AgACAgIAAxkBAANnafW0D0VKI1z0rMQ1mpAjm791whsAApETaxuDW7FLPPbcNASW-d8BAAMCAAN4AAM7BA"  # 2-ro'zg'or uchun default

ZODIAC_SIGNS = {
    "qoy": ("Qo'y", "♈"),
    "buzoq": ("Buzoq", "♉"),
    "egizak": ("Egizak", "♊"),
    "qisqichbaqa": ("Qisqichbaqa", "♋"),
    "arslon": ("Arslon", "♌"),
    "sunbula": ("Sunbula", "♍"),
    "tarozi": ("Tarozi", "♎"),
    "chayon": ("Chayon", "♏"),
    "oqotar": ("O'qotar", "♐"),
    "tog_echkisi": ("Tog' echkisi", "♑"),
    "qovga": ("Qovg'a", "♒"),
    "baliq": ("Baliq", "♓"),
}

ZODIAC_COMPATIBILITY = {
    "qoy": {
        "mos": ["arslon", "sunbula", "qoy", "tarozi", "qovga", "egizak", "oqotar"],
        "qiyin": ["qisqichbaqa", "chayon", "baliq"]
    },
    "buzoq": {
        "mos": ["buzoq", "qisqichbaqa", "tog_echkisi", "baliq", "chayon"],
        "qiyin": ["egizak", "oqotar", "qovga", "buzoq", "chayon", "tog_echkisi"]
    },
    "egizak": {
        "mos": ["qoy", "egizak", "oqotar", "buzoq", "chayon", "baliq"],
        "qiyin": ["qisqichbaqa", "chayon", "baliq", "egizak", "qo'y", "arslon"]
    },
    "qisqichbaqa": {
        "mos": ["buzoq", "tog_echkisi", "baliq", "chayon", "qisqichbaqa"],
        "qiyin": ["qoy", "egizak", "oqotar", "chayon", "qisqichbaqa", "tarozi"]
    },
    "arslon": {
        "mos": ["qoy", "egizak", "tarozi", "arslon", "oqotar", "qovga"],
        "qiyin": ["tog_echkisi", "baliq", "buzoq", "qisqichbaqa", "chayon"]
    },
    "sunbula": {
        "mos": ["qoy", "buzoq", "tog_echkisi", "sunbula", "qisqichbaqa", "baliq"],
        "qiyin": ["egizak", "oqotar", "qovga", "arslon", "chayon"]
    },
    "tarozi": {
        "mos": ["qoy", "egizak", "tarozi", "qovga", "oqotar", "arslon"],
        "qiyin": ["buzoq", "qisqichbaqa", "tog_echkisi", "chayon", "baliq"]
    },
    "chayon": {
        "mos": ["buzoq", "qisqichbaqa", "tog_echkisi", "chayon", "baliq"],
        "qiyin": ["qoy", "egizak", "oqotar", "arslon", "tarozi", "qovga"]
    },
    "oqotar": {
        "mos": ["qoy", "egizak", "arslon", "tarozi", "oqotar", "qovga"],
        "qiyin": ["buzoq", "qisqichbaqa", "tog_echkisi", "sunbula", "chayon"]
    },
    "tog_echkisi": {
        "mos": ["buzoq", "sunbula", "qisqichbaqa", "tog_echkisi", "baliq"],
        "qiyin": ["qoy", "egizak", "arslon", "tarozi", "oqotar", "qovga"]
    },
    "qovga": {
        "mos": ["qoy", "tarozi", "arslon", "oqotar", "qovga", "egizak"],
        "qiyin": ["buzoq", "sunbula", "tog_echkisi", "chayon", "baliq"]
    },
    "baliq": {
        "mos": ["buzoq", "qisqichbaqa", "chayon", "tog_echkisi", "baliq", "sunbula"],
        "qiyin": ["qoy", "egizak", "arslon", "tarozi", "oqotar", "qovga"]
    }
}

EDUCATION_OPTIONS = [
    "o'rta", "o'rta-maxsus", "oliy (bakalavr)", "oliy (magistr)",
    "Talaba", "O'quvchi", "Magistrant", "Yo'q"
]

MARITAL_STATUS_OPTIONS = [
    "bo'ydoq", "turmushga chiqmagan", "oilali", "qonuniy ajrashgan",
    "ajrimda", "beva", "boshqa..."
]

# ============================================================
# STATES
# ============================================================
class AnnouncementState(StatesGroup):
    announcement_type = State()
    photo_selection = State()
    name_age = State()
    nationality = State()
    height_weight = State()
    education = State()
    marital_status = State()
    children = State()
    residence = State()
    work = State()
    second_marriage = State()
    zodiac = State()
    behavior = State()
    partner_age = State()
    partner_nationality = State()
    partner_body = State()
    partner_education = State()
    partner_residence = State()
    partner_other = State()
    contact = State()
    preview = State()

# ============================================================
# DATABASE (PostgreSQL)
# ============================================================
async def get_db():
    return await asyncpg.connect(DATABASE_URL)

async def init_db():
    conn = await get_db()
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                joined_at TIMESTAMP DEFAULT NOW(),
                is_admin INTEGER DEFAULT 0
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                username TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT NOW(),
                posted_at TIMESTAMP,
                message_id INTEGER,
                photo_file_id TEXT,
                announcement_type TEXT,
                name_age TEXT,
                nationality TEXT,
                height_weight TEXT,
                education TEXT,
                marital_status TEXT,
                children TEXT,
                residence TEXT,
                work TEXT,
                second_marriage TEXT,
                zodiac TEXT,
                behavior TEXT,
                partner_age TEXT,
                partner_nationality TEXT,
                partner_body TEXT,
                partner_education TEXT,
                partner_residence TEXT,
                partner_other TEXT,
                contact TEXT
            )
        """)
    finally:
        await conn.close()

async def add_user(user_id: int, username: str, full_name: str):
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO users (user_id, username, full_name) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO NOTHING",
            user_id, username, full_name
        )
    finally:
        await conn.close()

async def create_announcement(user_id: int, username: str) -> int:
    conn = await get_db()
    try:
        row = await conn.fetchrow(
            "INSERT INTO announcements (user_id, username) VALUES ($1, $2) RETURNING id",
            user_id, username
        )
        return row["id"]
    finally:
        await conn.close()

async def update_announcement(ann_id: int, field: str, value: str):
    conn = await get_db()
    try:
        await conn.execute(
            f"UPDATE announcements SET {field} = $1 WHERE id = $2",
            value, ann_id
        )
    finally:
        await conn.close()

async def get_announcement(ann_id: int):
    conn = await get_db()
    try:
        row = await conn.fetchrow("SELECT * FROM announcements WHERE id = $1", ann_id)
        return dict(row) if row else None
    finally:
        await conn.close()

async def get_pending_announcements():
    conn = await get_db()
    try:
        rows = await conn.fetch("SELECT * FROM announcements WHERE status = 'pending' ORDER BY created_at DESC")
        return [dict(row) for row in rows]
    finally:
        await conn.close()

async def update_announcement_status(ann_id: int, status: str, message_id: int = None):
    conn = await get_db()
    try:
        if message_id:
            await conn.execute(
                "UPDATE announcements SET status = $1, posted_at = NOW(), message_id = $2 WHERE id = $3",
                status, message_id, ann_id
            )
        else:
            await conn.execute(
                "UPDATE announcements SET status = $1 WHERE id = $2",
                status, ann_id
            )
    finally:
        await conn.close()

async def get_user_announcements(user_id: int):
    conn = await get_db()
    try:
        rows = await conn.fetch(
            "SELECT * FROM announcements WHERE user_id = $1 ORDER BY created_at DESC", user_id
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()

# ============================================================
# UTILS
# ============================================================
def get_zodiac_display(zodiac_key: str) -> str:
    name, symbol = ZODIAC_SIGNS.get(zodiac_key, (zodiac_key, ""))
    return f"{name} {symbol}"

def get_compatibility_text(zodiac_key: str) -> tuple:
    data = ZODIAC_COMPATIBILITY.get(zodiac_key, {})
    mos_list = data.get("mos", [])[:3]  # Faqat 3 ta eng mos
    qiyin_list = data.get("qiyin", [])
    mos_text = ", ".join([get_zodiac_display(z) for z in mos_list]) if mos_list else "Mavjud emas"
    qiyin_text = ", ".join([get_zodiac_display(z) for z in qiyin_list]) if qiyin_list else "Mavjud emas"
    return mos_text, qiyin_text

def format_announcement(data: dict) -> str:
    ann_type = data.get("announcement_type", "")
    if "kuyov" in ann_type:
        header = "E'LON | KUYOV NOMZODI:"
    else:
        header = "E'LON | KELIN NOMZODI:"

    zodiac = data.get("zodiac", "")
    mos, qiyin = get_compatibility_text(zodiac)

    text = f"<b>{header}</b>\n\n"
    text += f"<b>Ismi:</b> {data.get('name_age', '---')}\n"
    text += f"<b>Millati:</b> {data.get('nationality', '---')}\n"
    text += f"<b>Bo'yi va vazni:</b> {data.get('height_weight', '---')}\n"
    text += f"<b>Ma'lumoti:</b> {data.get('education', '---')}\n"
    text += f"<b>Turmush holati:</b> {data.get('marital_status', '---')}\n"
    text += f"<b>Farzandi:</b> {data.get('children', '---')}\n"
    text += f"<b>Yashash joyi:</b> {data.get('residence', '---')}\n"
    text += f"<b>Ish joyi (kasbi):</b> {data.get('work', '---')}\n"
    if data.get("second_marriage"):
        text += f"<b>Ikkinchi ro'zg'orga:</b> {data.get('second_marriage')}\n"
    text += f"<b>Burji:</b> {get_zodiac_display(zodiac)}\n"
    text += f"<b>Eng mos burjlar:</b> {mos}\n"
    text += f"<b>Qiyin moslashadigan burjlar:</b> {qiyin}\n"
    text += f"<b>Fe'l-atvori:</b> {data.get('behavior', '---')}\n\n"
    text += "<b>💍 JUFTIDA IZLAYOTGAN SIFATLAR:</b>\n\n"
    text += f"<b>Yosh shegarasi:</b> {data.get('partner_age', '---')}\n"
    text += f"<b>Millati:</b> {data.get('partner_nationality', '---')}\n"
    text += f"<b>Qomati:</b> {data.get('partner_body', '---')}\n"
    text += f"<b>Ma'lumoti:</b> {data.get('partner_education', '---')}\n"
    text += f"<b>Yashash joyi:</b> {data.get('partner_residence', '---')}\n"
    text += f"<b>Boshqa talablar:</b> {data.get('partner_other', '---')}\n\n"
    text += f"<b>Aloqa uchun:</b> {data.get('contact', '---')}\n\n"
    text += "<b>KANALGA OBUNA BO'LISH</b> @sovchirr"
    return text

def is_valid_file_id(file_id: str) -> bool:
    return bool(file_id and not file_id.startswith("YOUR_FILE_ID"))

# ============================================================
# KEYBOARDS
# ============================================================
def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Yangi e'lon berish", callback_data="new_announcement")],
        [InlineKeyboardButton(text="📋 Mening e'lonlarim", callback_data="my_announcements")],
        [InlineKeyboardButton(text="📢 Kanalga o'tish", url=CHANNEL_LINK)]
    ])

def announcement_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤵 Kuyov nomzodi", callback_data="type_kuyov")],
        [InlineKeyboardButton(text="👰 Kelin nomzodi", callback_data="type_kelin")],
        [InlineKeyboardButton(text="🤵 Kuyov nomzodi (2-ro'zg'or)", callback_data="type_kuyov2")],
        [InlineKeyboardButton(text="👰 Kelin nomzodi (2-ro'zg'or)", callback_data="type_kelin2")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])

def kuyov_photo_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="photo_kuyov_1"),
         InlineKeyboardButton(text="2", callback_data="photo_kuyov_2")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])

def kelin_photo_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="photo_kelin_1"),
         InlineKeyboardButton(text="2", callback_data="photo_kelin_2"),
         InlineKeyboardButton(text="3", callback_data="photo_kelin_3")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])

def education_keyboard():
    buttons = []
    row = []
    for i, edu in enumerate(EDUCATION_OPTIONS):
        row.append(InlineKeyboardButton(text=edu, callback_data=f"edu_{i}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def marital_status_keyboard():
    buttons = []
    row = []
    for i, status in enumerate(MARITAL_STATUS_OPTIONS):
        row.append(InlineKeyboardButton(text=status, callback_data=f"marital_{i}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def zodiac_keyboard():
    buttons = []
    row = []
    for key, (name, symbol) in ZODIAC_SIGNS.items():
        row.append(InlineKeyboardButton(text=f"{symbol} {name}", callback_data=f"zodiac_{key}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def yes_no_keyboard(prefix: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ha", callback_data=f"{prefix}_yes"),
         InlineKeyboardButton(text="Yo'q", callback_data=f"{prefix}_no")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])

def preview_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Kanalga yuborish", callback_data="confirm_yes")],
        [InlineKeyboardButton(text="🔄 Qayta to'ldirish", callback_data="confirm_restart")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])

def cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])

# ============================================================
# HANDLERS
# ============================================================
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await add_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or ""
    )
    text = (
        "<b>Assalomu alaykum!</b> 👋\n\n"
        "<b>@sovchirr</b> kanalining rasmiy botiga xush kelibsiz!\n\n"
        "Bu bot orqali siz o'zingiz haqingizda e'lon berishingiz mumkin.\n\n"
        "E'lon berish uchun quyidagi tugmani bosing:"
    )
    await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")

@router.message(Command("file_id"))
async def cmd_file_id(message: Message):
    if message.photo:
        file_id = message.photo[-1].file_id
        await message.answer(f"<b>Rasm file_id:</b>\n<code>{file_id}</code>\n\nBu kodni main.py dagi rasm o'zgaruvchilariga qo'ying.", parse_mode="HTML")
    else:
        await message.answer("Rasm yuboring, men uning file_id sini beraman.")

@router.callback_query(F.data == "new_announcement")
async def new_announcement(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "<b>E'lon turini tanlang:</b>",
        reply_markup=announcement_type_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("type_"))
async def process_type(callback: CallbackQuery, state: FSMContext, bot: Bot):
    ann_type = callback.data.replace("type_", "")
    ann_id = await create_announcement(callback.from_user.id, callback.from_user.username or "")
    await state.update_data(ann_id=ann_id, announcement_type=ann_type)

    if ann_type == "kuyov":
        await state.set_state(AnnouncementState.photo_selection)
        await callback.message.delete()

        photo_ids = [KUYOV_IMAGES["kuyov_1"], KUYOV_IMAGES["kuyov_2"]]
        sent_msg_ids = []
        for i, pid in enumerate(photo_ids, 1):
            if is_valid_file_id(pid):
                msg = await bot.send_photo(
                    callback.from_user.id,
                    photo=pid,
                    caption=f"<b>Rasm {i}</b>",
                    parse_mode="HTML"
                )
                sent_msg_ids.append(msg.message_id)

        if not sent_msg_ids:
            await bot.send_message(
                callback.from_user.id,
                "<b>⚠️ Rasmlar hali sozlanmagan.</b> Admin bilan bog'laning.",
                reply_markup=main_menu_keyboard(),
                parse_mode="HTML"
            )
            await state.clear()
            return

        await state.update_data(photo_msg_ids=sent_msg_ids)
        await bot.send_message(
            callback.from_user.id,
            "<b>Yuqoridagi rasmlardan birini tanlang:</b>",
            reply_markup=kuyov_photo_keyboard(),
            parse_mode="HTML"
        )

    elif ann_type == "kelin":
        await state.set_state(AnnouncementState.photo_selection)
        await callback.message.delete()

        photo_ids = [KELIN_IMAGES["kelin_1"], KELIN_IMAGES["kelin_2"], KELIN_IMAGES["kelin_3"]]
        sent_msg_ids = []
        for i, pid in enumerate(photo_ids, 1):
            if is_valid_file_id(pid):
                msg = await bot.send_photo(
                    callback.from_user.id,
                    photo=pid,
                    caption=f"<b>Rasm {i}</b>",
                    parse_mode="HTML"
                )
                sent_msg_ids.append(msg.message_id)

        if not sent_msg_ids:
            await bot.send_message(
                callback.from_user.id,
                "<b>⚠️ Rasmlar hali sozlanmagan.</b> Admin bilan bog'laning.",
                reply_markup=main_menu_keyboard(),
                parse_mode="HTML"
            )
            await state.clear()
            return

        await state.update_data(photo_msg_ids=sent_msg_ids)
        await bot.send_message(
            callback.from_user.id,
            "<b>Yuqoridagi rasmlardan birini tanlang:</b>",
            reply_markup=kelin_photo_keyboard(),
            parse_mode="HTML"
        )

    elif ann_type == "kuyov2":
        await state.update_data(photo_file_id=KUYOV2_IMAGE)
        await state.set_state(AnnouncementState.name_age)
        await callback.message.edit_text(
            "<b>1/17</b> - Ismingiz va yoshingizni kiriting.\n"
            "<i>Masalan: Muzaffar, 28 yosh</i>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML"
        )
    elif ann_type == "kelin2":
        await state.update_data(photo_file_id=KELIN2_IMAGE)
        await state.set_state(AnnouncementState.name_age)
        await callback.message.edit_text(
            "<b>1/17</b> - Ismingiz va yoshingizni kiriting.\n"
            "<i>Masalan: Dilnoza, 28 yosh</i>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(AnnouncementState.photo_selection, F.data.startswith("photo_"))
async def process_photo_selection(callback: CallbackQuery, state: FSMContext, bot: Bot):
    photo_key = callback.data.replace("photo_", "")
    file_id = None

    if photo_key == "kuyov_1":
        file_id = KUYOV_IMAGES["kuyov_1"]
    elif photo_key == "kuyov_2":
        file_id = KUYOV_IMAGES["kuyov_2"]
    elif photo_key == "kelin_1":
        file_id = KELIN_IMAGES["kelin_1"]
    elif photo_key == "kelin_2":
        file_id = KELIN_IMAGES["kelin_2"]
    elif photo_key == "kelin_3":
        file_id = KELIN_IMAGES["kelin_3"]

    await state.update_data(photo_file_id=file_id)

    # Delete photo messages
    data = await state.get_data()
    msg_ids = data.get("photo_msg_ids", [])
    for msg_id in msg_ids:
        try:
            await bot.delete_message(callback.from_user.id, msg_id)
        except Exception:
            pass

    # Delete selection message
    try:
        await callback.message.delete()
    except Exception:
        pass

    await state.set_state(AnnouncementState.name_age)
    await bot.send_message(
        callback.from_user.id,
        "<b>1/17</b> - Ismingiz va yoshingizni kiriting.\n"
        "<i>Masalan: Muzaffar, 28 yosh</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(AnnouncementState.photo_selection, F.data == "cancel")
async def cancel_photo_selection(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg_ids = data.get("photo_msg_ids", [])
    for msg_id in msg_ids:
        try:
            await bot.delete_message(callback.from_user.id, msg_id)
        except Exception:
            pass
    try:
        await callback.message.delete()
    except Exception:
        pass
    await state.clear()
    await bot.send_message(
        callback.from_user.id,
        "<b>❌ Bekor qilindi.</b>",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.name_age)
async def process_name_age(message: Message, state: FSMContext):
    await state.update_data(name_age=message.text)
    await state.set_state(AnnouncementState.nationality)
    await message.answer(
        "<b>2/17</b> - Millatingizni kiriting:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.nationality)
async def process_nationality(message: Message, state: FSMContext):
    await state.update_data(nationality=message.text)
    await state.set_state(AnnouncementState.height_weight)
    await message.answer(
        "<b>3/17</b> - Bo'yingiz va vazningizni kiriting.\n"
        "<i>Masalan: 185 sm/90 kg</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.height_weight)
async def process_height_weight(message: Message, state: FSMContext):
    await state.update_data(height_weight=message.text)
    await state.set_state(AnnouncementState.education)
    await message.answer(
        "<b>4/17</b> - Ma'lumotingizni tanlang:",
        reply_markup=education_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(AnnouncementState.education, F.data.startswith("edu_"))
async def process_education(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.replace("edu_", ""))
    await state.update_data(education=EDUCATION_OPTIONS[idx])
    await state.set_state(AnnouncementState.marital_status)
    await callback.message.edit_text(
        "<b>5/17</b> - Turmush holatingizni tanlang:",
        reply_markup=marital_status_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(AnnouncementState.marital_status, F.data.startswith("marital_"))
async def process_marital(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.replace("marital_", ""))
    await state.update_data(marital_status=MARITAL_STATUS_OPTIONS[idx])
    await state.set_state(AnnouncementState.children)
    await callback.message.edit_text(
        "<b>6/17</b> - Farzandlaringiz haqida ma'lumot kiriting:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.children)
async def process_children(message: Message, state: FSMContext):
    await state.update_data(children=message.text)
    await state.set_state(AnnouncementState.residence)
    await message.answer(
        "<b>7/17</b> - Yashash joyingizni kiriting:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.residence)
async def process_residence(message: Message, state: FSMContext):
    await state.update_data(residence=message.text)
    await state.set_state(AnnouncementState.work)
    await message.answer(
        "<b>8/17</b> - Ish joyingiz va kasbingizni kiriting:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.work)
async def process_work(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(work=message.text)
    if "kelin" in data.get("announcement_type", ""):
        await state.set_state(AnnouncementState.second_marriage)
        await message.answer(
            "<b>9/17</b> - Ikkinchi ro'zg'orga tayyormisiz?",
            reply_markup=yes_no_keyboard("second"),
            parse_mode="HTML"
        )
    else:
        await state.set_state(AnnouncementState.zodiac)
        await message.answer(
            "<b>9/17</b> - Burjingizni tanlang:",
            reply_markup=zodiac_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(AnnouncementState.second_marriage, F.data.startswith("second_"))
async def process_second_marriage(callback: CallbackQuery, state: FSMContext):
    answer = "Ha" if callback.data == "second_yes" else "Yo'q"
    await state.update_data(second_marriage=answer)
    await state.set_state(AnnouncementState.zodiac)
    await callback.message.edit_text(
        "<b>10/17</b> - Burjingizni tanlang:",
        reply_markup=zodiac_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(AnnouncementState.zodiac, F.data.startswith("zodiac_"))
async def process_zodiac(callback: CallbackQuery, state: FSMContext):
    zodiac = callback.data.replace("zodiac_", "")
    await state.update_data(zodiac=zodiac)
    await state.set_state(AnnouncementState.behavior)
    await callback.message.edit_text(
        "<b>11/17</b> - Fe'l-atvoringizni qisqacha yozing:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.behavior)
async def process_behavior(message: Message, state: FSMContext):
    await state.update_data(behavior=message.text)
    await state.set_state(AnnouncementState.partner_age)
    await message.answer(
        "<b>12/17</b> - Juftingiz uchun yosh chegarasini kiriting:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.partner_age)
async def process_partner_age(message: Message, state: FSMContext):
    await state.update_data(partner_age=message.text)
    await state.set_state(AnnouncementState.partner_nationality)
    await message.answer(
        "<b>13/17</b> - Juftingiz millatini kiriting:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.partner_nationality)
async def process_partner_nationality(message: Message, state: FSMContext):
    await state.update_data(partner_nationality=message.text)
    await state.set_state(AnnouncementState.partner_body)
    await message.answer(
        "<b>14/17</b> - Juftingiz qomatini kiriting:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.partner_body)
async def process_partner_body(message: Message, state: FSMContext):
    await state.update_data(partner_body=message.text)
    await state.set_state(AnnouncementState.partner_education)
    await message.answer(
        "<b>15/17</b> - Juftingiz ma'lumoti:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.partner_education)
async def process_partner_education(message: Message, state: FSMContext):
    await state.update_data(partner_education=message.text)
    await state.set_state(AnnouncementState.partner_residence)
    await message.answer(
        "<b>16/17</b> - Juftingiz yashash joyi:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.partner_residence)
async def process_partner_residence(message: Message, state: FSMContext):
    await state.update_data(partner_residence=message.text)
    await state.set_state(AnnouncementState.partner_other)
    await message.answer(
        "<b>17/17</b> - Boshqa talablaringiz (200 belgidan oshmasin):",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.partner_other)
async def process_partner_other(message: Message, state: FSMContext):
    if len(message.text) > 200:
        await message.answer(
            "<b>❌ 200 belgidan oshmasligi kerak!</b> Qayta kiriting:",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML"
        )
        return
    await state.update_data(partner_other=message.text)
    await state.set_state(AnnouncementState.contact)
    await message.answer(
        "Aloqa uchun Telegram username yoki telefon raqam:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.contact)
async def process_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()
    ann_id = data.get("ann_id")
    # Only save fields that exist in DB table
    db_fields = [
        "announcement_type", "photo_file_id", "name_age", "nationality",
        "height_weight", "education", "marital_status", "children",
        "residence", "work", "second_marriage", "zodiac", "behavior",
        "partner_age", "partner_nationality", "partner_body",
        "partner_education", "partner_residence", "partner_other", "contact"
    ]
    for key, value in data.items():
        if key in db_fields and value is not None:
            await update_announcement(ann_id, key, str(value))
    ann_data = await get_announcement(ann_id)
    text = format_announcement(ann_data)
    await state.set_state(AnnouncementState.preview)
    await message.answer(
        "<b>E'loningiz tayyor! Tekshirib chiqing:</b>\n\n" + text,
        reply_markup=preview_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(AnnouncementState.preview, F.data == "confirm_yes")
async def confirm_announcement(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    ann_id = data.get("ann_id")
    await update_announcement_status(ann_id, "approved")
    await state.clear()
    ann_data = await get_announcement(ann_id)
    text = format_announcement(ann_data)
    photo_file_id = ann_data.get("photo_file_id", "")

    try:
        if is_valid_file_id(photo_file_id):
            msg = await bot.send_photo(
                CHANNEL_ID,
                photo=photo_file_id,
                caption=text,
                parse_mode="HTML"
            )
            await update_announcement_status(ann_id, "approved", msg.message_id)
        else:
            msg = await bot.send_message(CHANNEL_ID, text, parse_mode="HTML")
            await update_announcement_status(ann_id, "approved", msg.message_id)

        await callback.message.edit_text(
            "<b>✅ E'loningiz kanalga muvaffaqiyatli yuborildi!</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.message.edit_text(
            f"<b>❌ Xatolik yuz berdi:</b> {str(e)}\n\nIltimos, admin bilan bog'laning.",
            parse_mode="HTML"
        )

@router.callback_query(AnnouncementState.preview, F.data == "confirm_restart")
async def restart_announcement(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await new_announcement(callback, state)

@router.callback_query(F.data == "cancel")
async def cancel_process(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "<b>❌ Bekor qilindi.</b>",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "my_announcements")
async def my_announcements(callback: CallbackQuery):
    anns = await get_user_announcements(callback.from_user.id)
    if not anns:
        await callback.message.edit_text(
            "<b>Sizda hali e'lonlar yo'q.</b>",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
        return
    text = "<b>📋 Sizning e'lonlaringiz:</b>\n\n"
    for ann in anns:
        status = ann.get("status", "pending")
        status_text = {"pending": "⏳ Kutilmoqda", "approved": "✅ Kanalga yuborilgan", "rejected": "❌ Rad etilgan"}.get(status, status)
        text += f"🆔 #{ann['id']} - {status_text}\n"
    await callback.message.edit_text(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")

# ============================================================
# MAIN
# ============================================================
async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())