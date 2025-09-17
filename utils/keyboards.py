
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("💬 Feedback", callback_data="feedback:menu")],
        [InlineKeyboardButton("🏗️ تأسيس", callback_data="foundation:menu")],
        [InlineKeyboardButton("🏋️ تدريب", callback_data="training:menu")],
        [InlineKeyboardButton("📊 اختبارات", callback_data="tests:menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_main_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main:menu")]])

def doors_kb(section_prefix: str, content: dict):
    rows = []
    for door_id, door in content.get("doors", {}).items():
        title = door.get("title", f"باب {door_id}")
        rows.append([InlineKeyboardButton(f"🚪 الباب {door_id} — {title}", callback_data=f"{section_prefix}:door:{door_id}")])
    rows.append([InlineKeyboardButton("🏠 العودة", callback_data="main:menu")])
    return InlineKeyboardMarkup(rows)

def lessons_kb(section_prefix: str, door_id: str, door: dict):
    rows = []
    for lesson_id, lesson in door.get("lessons", {}).items():
        title = lesson.get("title", f"درس {lesson_id}")
        rows.append([InlineKeyboardButton(f"📘 الدرس {lesson_id}: {title}", callback_data=f"{section_prefix}:door:{door_id}:lesson:{lesson_id}")])
    rows.append([InlineKeyboardButton("⬅️ رجوع للأبواب", callback_data=f"{section_prefix}:menu")])
    rows.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main:menu")])
    return InlineKeyboardMarkup(rows)

def rules_kb(section_prefix: str, door_id: str, lesson_id: str, lesson: dict):
    rows = []
    for rule_id, rule in lesson.get("rules", {}).items():
        title = rule.get("title", f"قاعدة {rule_id}")
        rows.append([InlineKeyboardButton(f"🔎 القاعدة {rule_id}: {title}", callback_data=f"{section_prefix}:door:{door_id}:lesson:{lesson_id}:rule:{rule_id}")])
    rows.append([InlineKeyboardButton("⬅️ رجوع للدروس", callback_data=f"{section_prefix}:door:{door_id}")])
    rows.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main:menu")])
    return InlineKeyboardMarkup(rows)

def start_questions_kb(section_prefix: str, d: str, l: str, r: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ ابدأ الأسئلة", callback_data=f"{section_prefix}:startq:door:{d}:lesson:{l}:rule:{r}:0")],
        [InlineKeyboardButton("⬅️ رجوع للدروس", callback_data=f"{section_prefix}:door:{d}")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main:menu")],
    ])

def choices_kb(qid: str, choices: list):
    rows = []
    for i, ch in enumerate(choices, start=1):
        rows.append([InlineKeyboardButton(f"{i}. {ch}", callback_data=f"ans:{qid}:{i}")])
    rows.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main:menu")])
    return InlineKeyboardMarkup(rows)

def results_kb(section_prefix: str, d: str, l: str, r: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 أعد المحاولة", callback_data=f"{section_prefix}:startq:door:{d}:lesson:{l}:rule:{r}:0")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main:menu")],
    ])
