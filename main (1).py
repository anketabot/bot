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
DATABASE_URL = os.getenv("DATABASE_URL", "")

# 4 ta kanal
CHANNELS = {
    "ch1": {
        "id": os.getenv("CH1_ID", "@sovchirr"),
        "link": os.getenv("CH1_LINK", "https://t.me/sovchirr"),
        "name": os.getenv("CH1_NAME", "@sovchirr"),
    },
    "ch2": {
        "id": os.getenv("CH2_ID", ""),
        "link": os.getenv("CH2_LINK", ""),
        "name": os.getenv("CH2_NAME", ""),
    },
    "ch3": {
        "id": os.getenv("CH3_ID", ""),
        "link": os.getenv("CH3_LINK", ""),
        "name": os.getenv("CH3_NAME", ""),
    },
    "ch4": {
        "id": os.getenv("CH4_ID", ""),
        "link": os.getenv("CH4_LINK", ""),
        "name": os.getenv("CH4_NAME", ""),
    },
}

# === RASM FILE_ID LARI ===
KUYOV_IMAGES = {
    "kuyov_1": os.getenv("KUYOV_IMG1", ""),
    "kuyov_2": os.getenv("KUYOV_IMG2", ""),
}
KELIN_IMAGES = {
    "kelin_1": os.getenv("KELIN_IMG1", ""),
    "kelin_2": os.getenv("KELIN_IMG2", ""),
    "kelin_3": os.getenv("KELIN_IMG3", ""),
}
KUYOV2_IMAGE = os.getenv("KUYOV2_IMG", "")

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
        "mos": ["arslon", "egizak", "oqotar"],
        "qiyin": ["qisqichbaqa", "chayon", "baliq"]
    },
    "buzoq": {
        "mos": ["sunbula", "qisqichbaqa", "togʻ echkisi"],
        "qiyin": ["egizak", "oʻqotar", "qovgʻa"]
    },
    "egizak": {
        "mos": ["qoy", "tarozi", "qovga"],
        "qiyin": ["buzoq", "chayon", "togʻ echkisi"]
    },
    "qisqichbaqa": {
        "mos": ["buzoq", "baliq", "chayon"],
        "qiyin": ["qoy", "egizak", "oqotar"]
    },
    "arslon": {
        "mos": ["qoy", "egizak", "tarozi"],
        "qiyin": ["buzoq", "tog_echkisi", "baliq"]
    },
    "sunbula": {
        "mos": ["buzoq", "togʻ echkisi", "chayon"],
        "qiyin": ["egizak", "arslon", "oʻqotar"]
    },
    "tarozi": {
        "mos": ["egizak", "arslon", "qovgʻa"],
        "qiyin": ["chayon", "qisqichbaqa", "togʻ echkisi"]
    },
    "chayon": {
        "mos": ["qisqichbaqa", "baliq", "buzoq"],
        "qiyin": ["egizak", "qoʻy", "tarozi"]
    },
    "oqotar": {
        "mos": ["qoʻy", "arslon", "qovga"],
        "qiyin": ["buzoq", "qisqichbaqa", "togʻ echkisi"]
    },
    "tog_echkisi": {
        "mos": ["buzoq", "sunbula", "chayon"],
        "qiyin": ["egizak", "tarozi", "oʻqotar"]
    },
    "qovga": {
        "mos": ["oʻqotar", "egizak", "tarozi"],
        "qiyin": ["buzoq", "chayon", "qisqichbaqa"]
    },
    "baliq": {
        "mos": ["buzoq", "qisqichbaqa", "chayon"],
        "qiyin": ["qoy", "egizak", "arslon"]
    }
}

EDUCATION_OPTIONS = [
    "o'rta", "o'rta-maxsus", "oliy (bakalavr)", "oliy (magistr)",
    "Toʻliqsiz oliy", "O'quvchi", "Magistrant", "Yo'q"
]

MARITAL_STATUS_OPTIONS = [
    "bo'ydoq", "oilali", "ajrimda", "turmushga chiqmagan",
    "qonuniy ajrashgan", "beva", "boshqa..."
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
    channel_selection = State()

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
                contact TEXT,
                channel_id TEXT,
                channel_name TEXT
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS posted_channels (
                id SERIAL PRIMARY KEY,
                announcement_id INTEGER REFERENCES announcements(id) ON DELETE CASCADE,
                channel_id TEXT,
                channel_name TEXT,
                message_id INTEGER,
                posted_at TIMESTAMP DEFAULT NOW()
            )
        """)
        await conn.execute("""
            ALTER TABLE announcements 
            ADD COLUMN IF NOT EXISTS channel_id TEXT,
            ADD COLUMN IF NOT EXISTS channel_name TEXT
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS announcement_counter (
                id SERIAL PRIMARY KEY,
                current_number INTEGER DEFAULT 0
            )
        """)
        await conn.execute("""
            INSERT INTO announcement_counter (id, current_number) VALUES (1, 0)
            ON CONFLICT (id) DO NOTHING
        """)
    finally:
        await conn.close()

async def get_next_announcement_number() -> int:
    conn = await get_db()
    try:
        row = await conn.fetchrow(
            "UPDATE announcement_counter SET current_number = current_number + 1 WHERE id = 1 RETURNING current_number"
        )
        return row["current_number"]
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

async def get_user_announcements(user_id: int):
    conn = await get_db()
    try:
        rows = await conn.fetch(
            "SELECT * FROM announcements WHERE user_id = $1 AND name_age IS NOT NULL AND status != 'deleted' ORDER BY created_at DESC", 
            user_id
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()
        

async def update_announcement_status(ann_id: int, status: str, message_id: int = None, channel_id: str = None, channel_name: str = None):
    conn = await get_db()
    try:
        if message_id is not None and channel_id:
            await conn.execute(
                "UPDATE announcements SET status = $1, posted_at = NOW(), message_id = $2, channel_id = $3, channel_name = $4 WHERE id = $5",
                status, message_id, channel_id, channel_name, ann_id
            )
        else:
            await conn.execute(
                "UPDATE announcements SET status = $1 WHERE id = $2",
                status, ann_id
            )
    finally:
        await conn.close()

async def add_posted_channel(ann_id: int, channel_id: str, channel_name: str, message_id: int):
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO posted_channels (announcement_id, channel_id, channel_name, message_id) VALUES ($1, $2, $3, $4)",
            ann_id, channel_id, channel_name, message_id
        )
    finally:
        await conn.close()

async def get_posted_channels(ann_id: int):
    conn = await get_db()
    try:
        rows = await conn.fetch(
            "SELECT * FROM posted_channels WHERE announcement_id = $1",
            ann_id
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()

async def delete_posted_channels(ann_id: int):
    conn = await get_db()
    try:
        await conn.execute(
            "DELETE FROM posted_channels WHERE announcement_id = $1",
            ann_id
        )
    finally:
        await conn.close()

# ============================================================
# UTILS
# ============================================================
def get_zodiac_display(zodiac_key: str) -> str:
    name, symbol = ZODIAC_SIGNS.get(zodiac_key, (zodiac_key, ""))
    return f"{name} {symbol}"

def get_zodiac_lowercase(zodiac_key: str) -> str:
    name, _ = ZODIAC_SIGNS.get(zodiac_key, (zodiac_key, ""))
    return name.lower()

def get_compatibility_text(zodiac_key: str) -> tuple:
    data = ZODIAC_COMPATIBILITY.get(zodiac_key, {})
    mos_list = data.get("mos", [])[:3]
    qiyin_list = data.get("qiyin", [])
    mos_text = ", ".join([get_zodiac_lowercase(z) for z in mos_list]) if mos_list else "Mavjud emas"
    qiyin_text = ", ".join([get_zodiac_lowercase(z) for z in qiyin_list]) if qiyin_list else "Mavjud emas"
    return mos_text, qiyin_text

def format_announcement(data: dict, ann_number: int = None, channel_key: str = "ch1") -> str:
    ann_type = data.get("announcement_type") or ""
    num_str = f" №{ann_number}" if ann_number else ""

    if "kuyov" in ann_type:
        if "2" in ann_type:
            header = f"E'LON{num_str} KUYOV 2-RO'ZG'ORGA"
        else:
            header = f"E'LON{num_str} KUYOV NOMZODI"
    else:
        header = f"E'LON{num_str} KELIN NOMZODI"

    zodiac = data.get("zodiac", "")
    mos, qiyin = get_compatibility_text(zodiac)

    ch_info = CHANNELS.get(channel_key, CHANNELS["ch1"])
    ch_name = ch_info.get("name", "@sovchirr")

    # BARCHA MATN QIYA (italic) ichida
    text = f"<i><b>{header}</b>\n"
    text += f"<b>Ismi va yoshi:</b> {data.get('name_age', '---')}\n"
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
    text += "<b>💍 JUFTIDA IZLAYOTGAN SIFATLAR:</b>\n"
    text += f"<b>Yosh chegarasi:</b> {data.get('partner_age', '---')}\n"
    text += f"<b>Millati:</b> {data.get('partner_nationality', '---')}\n"
    text += f"<b>Ko'rinishi:</b> {data.get('partner_body', '---')}\n"
    text += f"<b>Ma'lumoti:</b> {data.get('partner_education', '---')}\n"
    text += f"<b>Qaysi hududdan qidiryapsiz:</b> {data.get('partner_residence', '---')}\n"
    text += f"<b>Talablaringiz:</b> {data.get('partner_other', '---')}\n"
    text += f"<b>Aloqa uchun:</b> {data.get('contact', '---')}\n"
    text += f"<b>Anketa to'ldirish: @AnketaYozing_bot</b>\n"
    text += f"<b>OBUNA BO'LISH</b> {ch_name}</i>"
    return text
    

def is_valid_file_id(file_id: str) -> bool:
    return bool(file_id and file_id.strip() and not file_id.startswith("YOUR_FILE_ID"))

# ============================================================
# KEYBOARDS
# ============================================================
def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Yangi e'lon berish", callback_data="new_announcement")],
        [InlineKeyboardButton(text="📋 Mening e'lonlarim", callback_data="my_announcements")],
    ])

def announcement_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤵 Kuyov nomzodi", callback_data="type_kuyov")],
        [InlineKeyboardButton(text="👰 Kelin nomzodi", callback_data="type_kelin")],
        [InlineKeyboardButton(text="🤵 Kuyov nomzodi (2-ro'zg'or)", callback_data="type_kuyov2")],
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
        [InlineKeyboardButton(text="✅ Kanallarga yuborish", callback_data="confirm_yes")],
        [InlineKeyboardButton(text="🔄 Qayta to'ldirish", callback_data="confirm_restart")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])

def cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])

def skip_keyboard(prefix: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ O'tkazib yuborish", callback_data=f"{prefix}_skip")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])

def channel_selection_keyboard(selected=None):
    if selected is None:
        selected = []
    buttons = []
    for ch_key, ch_info in CHANNELS.items():
        ch_name = ch_info.get("name", "")
        if not ch_name:
            continue
        mark = "✅" if ch_key in selected else "☑️"
        buttons.append([InlineKeyboardButton(text=f"{mark} {ch_name}", callback_data=f"chsel_{ch_key}")])
    buttons.append([
        InlineKeyboardButton(text="🚀 Yuborish", callback_data="chsel_confirm"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

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
        "Sovchilar kanalining rasmiy botiga xush kelibsiz!\n\n"
        "Bu bot orqali siz o'zingiz haqingizda e'lon berishingiz mumkin.\n\n"
        "E'lon berish uchun quyidagi tugmani bosing:"
    )
    await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")

@router.message(Command("file_id"))
async def cmd_file_id(message: Message):
    if message.photo:
        file_id = message.photo[-1].file_id
        await message.answer(f"<b>Rasm file_id:</b>\n<code>{file_id}</code>\n\nBu kodni .env faylga qo'ying.", parse_mode="HTML")
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
            "<i>Masalan: Umid(a), 28 yosh</i>",
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

    await state.set_state(AnnouncementState.name_age)
    await bot.send_message(
        callback.from_user.id,
        "<b>1/17</b> - Ismingiz va yoshingizni kiriting.\n"
        "<i>Masalan: Umid(a), 28 yosh</i>",
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
        "<b>2/17</b> - Millatingizni kiriting:\n"
        "<i>Masalan: o'zbek...</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.nationality)
async def process_nationality(message: Message, state: FSMContext):
    await state.update_data(nationality=message.text)
    await state.set_state(AnnouncementState.height_weight)
    await message.answer(
        "<b>3/17</b> - Bo'yingiz va vazningizni kiriting.\n"
        "<i>Masalan: 175 sm/70 kg</i>",
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
    parts = callback.data.split("_")
    idx = int(parts[1])
    gender = parts[2] if len(parts) > 2 else "male"
    options = MARITAL_STATUS_MALE if gender == "male" else MARITAL_STATUS_FEMALE

    await state.update_data(marital_status=options[idx])
    await state.set_state(AnnouncementState.children)
    await callback.message.edit_text(
        "<b>6/17</b> - Farzandlaringiz haqida ma'lumot kiriting:\n"
        "<i>Masalan: bor, yo'q, bir o'g'il, bir qiz,..</i>",
        reply_markup=skip_keyboard("children"),
        parse_mode="HTML"
    )

@router.callback_query(AnnouncementState.children, F.data == "children_skip")
async def skip_children(callback: CallbackQuery, state: FSMContext):
    await state.update_data(children="Yo'q")
    await state.set_state(AnnouncementState.residence)
    await callback.message.edit_text(
        "<b>7/17</b> - Yashash joyingizni kiriting:\n"
        "<i>Masalan: ... viloyati ... tumani/shahri</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.children)
async def process_children(message: Message, state: FSMContext):
    await state.update_data(children=message.text)
    await state.set_state(AnnouncementState.residence)
    await message.answer(
        "<b>7/17</b> - Yashash joyingizni kiriting:\n"
        "<i>Masalan: ... viloyati ... tumani/shahri</i>",
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
        "<b>11/17</b> - Fe'l-atvoringizni qisqacha yozing:\n"
        "<i>Masalan: jiddiy, kamgap,...</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.behavior)
async def process_behavior(message: Message, state: FSMContext):
    await state.update_data(behavior=message.text)
    await state.set_state(AnnouncementState.partner_age)
    await message.answer(
        "<b>12/17</b> - Juftingiz uchun yosh chegarasini kiriting:\n"
        "<i>Masalan: 18-25 yosh, taqdir,...</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.partner_age)
async def process_partner_age(message: Message, state: FSMContext):
    await state.update_data(partner_age=message.text)
    await state.set_state(AnnouncementState.partner_nationality)
    await message.answer(
        "<b>13/17</b> - Juftingiz millatini kiriting:\n"
        "<i>Masalan: o'zbek, muhim emas, taqdir,...</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.partner_nationality)
async def process_partner_nationality(message: Message, state: FSMContext):
    await state.update_data(partner_nationality=message.text)
    await state.set_state(AnnouncementState.partner_body)
    await message.answer(
        "<b>14/17</b> - Juftingiz ko'rinishini kiriting:\n"
        "<i>Masalan: taqdir, kelishgan, bo'yi...</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.partner_body)
async def process_partner_body(message: Message, state: FSMContext):
    await state.update_data(partner_body=message.text)
    await state.set_state(AnnouncementState.partner_education)
    await message.answer(
        "<b>15/17</b> - Juftingiz ma'lumoti:\n"
        "<i>Masalan: oliy, o'qimishli, muhim emas,...</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.partner_education)
async def process_partner_education(message: Message, state: FSMContext):
    await state.update_data(partner_education=message.text)
    await state.set_state(AnnouncementState.partner_residence)
    await message.answer(
        "<b>16/17</b> - Juftingizni qaysi hududdan qidiryapsiz:\n"
        "<i>Masalan: Toshkent shahri, ...</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.partner_residence)
async def process_partner_residence(message: Message, state: FSMContext):
    await state.update_data(partner_residence=message.text)
    await state.set_state(AnnouncementState.partner_other)
    await message.answer(
        "<b>17/17</b> - Juftingizga talablaringiz (200 belgidan oshmasin):\n"
        "<i>Masalan: diniy, xarakteri yaxshi,..</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.partner_other)
async def process_partner_other(message: Message, state: FSMContext):
    if len(message.text) > 200:
        await message.answer(
            "<b>❌ 200 belgidan ko'p! Talablaringizni qisqartiring:</b>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML"
        )
        return
    await state.update_data(partner_other=message.text)
    await state.set_state(AnnouncementState.contact)
    await message.answer(
        "<b>Nomzod bilan bog'lanish:</b>\n"
        "<i>Masalan: @sovchirr, +99877...</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AnnouncementState.contact)
async def process_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()
    ann_id = data.get("ann_id")
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
async def confirm_announcement(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AnnouncementState.channel_selection)
    await state.update_data(selected_channels=[])
    await callback.message.edit_text(
        "<b>Qaysi kanallarga yuborishni tanlang:</b>",
        reply_markup=channel_selection_keyboard([]),
        parse_mode="HTML"
    )

@router.callback_query(AnnouncementState.channel_selection, F.data == "chsel_confirm")
async def process_channel_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    selected = data.get("selected_channels", [])
    if not selected:
        await callback.answer("Kamida bitta kanal tanlang!", show_alert=True)
        return

    ann_id = data.get("ann_id")
    ann_data = await get_announcement(ann_id)

    ann_number = await get_next_announcement_number()

    photo_file_id = ann_data.get("photo_file_id", "")
    success_channels = []
    failed_channels = []

    for ch_key in selected:
        ch_info = CHANNELS.get(ch_key, {})
        ch_id = ch_info.get("id", "")
        ch_name = ch_info.get("name", "")

        if not ch_id or not ch_name:
            continue

        text = format_announcement(ann_data, ann_number, ch_key)

        try:
            if is_valid_file_id(photo_file_id):
                msg = await bot.send_photo(
                    ch_id,
                    photo=photo_file_id,
                    caption=text,
                    parse_mode="HTML"
                )
            else:
                msg = await bot.send_message(ch_id, text, parse_mode="HTML")

            success_channels.append(ch_name)
            await add_posted_channel(ann_id, ch_id, ch_name, msg.message_id)

            if len(success_channels) == 1:
                await update_announcement_status(ann_id, "approved", msg.message_id, ch_id, ch_name)

        except Exception as e:
            failed_channels.append(f"{ch_name}: {str(e)}")

    await state.clear()

    if success_channels:
        success_text = "<b>✅ E'loningiz quyidagi kanallarga yuborildi:</b>\n"
        for ch in success_channels:
            success_text += f"• {ch}\n"

        if failed_channels:
            success_text += "\n<b>❌ Quyidagi kanallarga yuborilmadi:</b>\n"
            for fail in failed_channels:
                success_text += f"• {fail}\n"

        success_text += f"\n<b>E'lon raqami:</b> №{ann_number}"

        await callback.message.edit_text(success_text, parse_mode="HTML")
    else:
        await callback.message.edit_text(
            "<b>❌ E'lonni hech qaysi kanalga yuborib bo'lmadi.</b>\n\n"
            "Iltimos, admin bilan bog'laning.",
            parse_mode="HTML"
        )

@router.callback_query(AnnouncementState.channel_selection, F.data.startswith("chsel_"))
async def toggle_channel_selection(callback: CallbackQuery, state: FSMContext):
    ch_key = callback.data.replace("chsel_", "")
    data = await state.get_data()
    selected = list(data.get("selected_channels", []))
    if ch_key in selected:
        selected.remove(ch_key)
    else:
        selected.append(ch_key)
    await state.update_data(selected_channels=selected)
    await callback.message.edit_reply_markup(reply_markup=channel_selection_keyboard(selected))
    await callback.answer()

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


# ============================================================
# MENING E'LONLARIM
# ============================================================
async def _show_single_announcement(callback_or_message, bot: Bot, ann: dict, from_list: bool = True):
    ann_number = ann.get("id")

    channel_key = "ch1"
    for ch_key, ch_info in CHANNELS.items():
        if ch_info.get("name") == ann.get("channel_name"):
            channel_key = ch_key
            break

    text = format_announcement(ann, ann_number, channel_key)
    text = f"<b>📋 E'lon #{ann['id']}</b>\n\n{text}"

    photo_file_id = ann.get("photo_file_id", "")

    kb = []
    status = ann.get("status", "pending")
    if status == "approved":
        kb.append([InlineKeyboardButton(text="🗑 E'lonni o'chirish", callback_data=f"delann_{ann['id']}")])

    if from_list:
        kb.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="my_announcements")])
    else:
        kb.append([InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_main")])

    markup = InlineKeyboardMarkup(inline_keyboard=kb)

    if is_valid_file_id(photo_file_id):
        try:
            if hasattr(callback_or_message, 'message'):
                try:
                    await callback_or_message.message.delete()
                except Exception:
                    pass
                await bot.send_photo(
                    chat_id=callback_or_message.from_user.id,
                    photo=photo_file_id,
                    caption=text,
                    reply_markup=markup,
                    parse_mode="HTML"
                )
            else:
                try:
                    await callback_or_message.delete()
                except Exception:
                    pass
                await bot.send_photo(
                    chat_id=callback_or_message.chat.id,
                    photo=photo_file_id,
                    caption=text,
                    reply_markup=markup,
                    parse_mode="HTML"
                )
            return
        except Exception:
            pass

    try:
        if hasattr(callback_or_message, 'message'):
            await callback_or_message.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
        else:
            await callback_or_message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        if hasattr(callback_or_message, 'message'):
            await bot.send_message(
                chat_id=callback_or_message.from_user.id,
                text=text,
                reply_markup=markup,
                parse_mode="HTML"
            )
        else:
            await bot.send_message(
                chat_id=callback_or_message.chat.id,
                text=text,
                reply_markup=markup,
                parse_mode="HTML"
            )


@router.callback_query(F.data == "my_announcements")
async def my_announcements(callback: CallbackQuery, bot: Bot):
    anns = await get_user_announcements(callback.from_user.id)
    if not anns:
        await callback.message.edit_text(
            "<b>Sizda hali e'lonlar yo'q.</b>",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
        return

    if len(anns) == 1:
        ann = anns[0]
        await _show_single_announcement(callback, bot, ann, from_list=False)
        return

    text = "<b>📋 Sizning e'lonlaringiz:</b>\n\nBatafsil ko'rish uchun tanlang:"
    kb = []
    for ann in anns:
        name = ann.get('name_age', '---')
        kb.append([InlineKeyboardButton(
            text=f"📄 E'lon #{ann['id']} - {name}",
            callback_data=f"view_ann_{ann['id']}"
        )])

    kb.append([InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_main")])

    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="HTML")
    except Exception:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await bot.send_message(
            chat_id=callback.from_user.id,
            text=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("view_ann_"))
async def view_announcement(callback: CallbackQuery, bot: Bot):
    ann_id = int(callback.data.replace("view_ann_", ""))
    ann = await get_announcement(ann_id)

    if not ann or ann.get("user_id") != callback.from_user.id:
        await callback.answer("Bu e'lon topilmadi!", show_alert=True)
        return

    await _show_single_announcement(callback, bot, ann, from_list=True)


@router.callback_query(F.data.startswith("delann_"))
async def delete_announcement(callback: CallbackQuery, bot: Bot):
    ann_id = int(callback.data.replace("delann_", ""))
    ann = await get_announcement(ann_id)
    if not ann or ann.get("user_id") != callback.from_user.id:
        await callback.answer("Bu e'lon sizga tegishli emas!", show_alert=True)
        return

    if ann.get("status") != "approved":
        await callback.answer("Bu e'lon allaqachon o'chirilgan!", show_alert=True)
        return

    posted_channels = await get_posted_channels(ann_id)
    deleted_count = 0

    for pc in posted_channels:
        try:
            if pc.get("message_id") and pc.get("channel_id"):
                await bot.delete_message(pc["channel_id"], pc["message_id"])
                deleted_count += 1
        except Exception:
            pass

    try:
        if ann.get("message_id") and ann.get("channel_id"):
            await bot.delete_message(ann["channel_id"], ann["message_id"])
    except Exception:
        pass

    await update_announcement_status(ann_id, "deleted")
    await delete_posted_channels(ann_id)

    await callback.answer(f"E'lon {deleted_count} ta kanaldan o'chirildi!")
    await my_announcements(callback, bot)


@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            "<b>Asosiy menyu:</b>",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(
            "<b>Asosiy menyu:</b>",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )

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
