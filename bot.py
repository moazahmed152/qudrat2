# bot.py — كل البوت في ملف واحد ✨
# ملاحظات سريعة:
# - لازم تضيف متغير البيئة TOKEN في Railway/BotFather token.
# - الملف هيُنشئ students.json تلقائياً لتخزين بيانات الطلاب والتقدم.

import os
import json
import random
import logging
from datetime import datetime, timedelta, time

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# 🔧 الإعدادات (Config)
# =========================
TELEGRAM_BOT_TOKEN = os.getenv("TOKEN")  # ضع التوكن في متغير بيئة باسم TOKEN
DEFAULT_VALID_KEYS = {"ABC123", "XYZ789"}  # مفاتيح منتج مسموح بها
STUDENTS_FILE = "students.json"

# رسائل تحفيزية قصيرة
POSITIVE_EMOJI = ["✨", "🌟", "💪", "🚀", "🙌", "🔥", "🧠", "🏆"]
POSITIVE_TEXTS = [
    "الله ينور! 😍",
    "تمام كده 👌",
    "شُغلك نظيف! 💯",
    "ممتاز يا بطل! 🏅",
    "جميل جدًا، كمل! 🚀",
]

# وقت التذكير اليومي (UTC)
DAILY_REMINDER_UTC = time(hour=18, minute=0)  # 18:00 UTC

# =========================
# 🗄️ تخزين بسيط (JSON)
# =========================
def _load_students() -> dict:
    try:
        with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception:
        return {}

def _save_students(data: dict) -> None:
    with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _ensure_user(user_id: int) -> dict:
    data = _load_students()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "name": "",
            "key_valid": False,
            "progress": {},  # مفاتيح مثل: chapter1:lesson1:rule1:example3 -> "done"
            "last_active": datetime.utcnow().isoformat(),
            "stats": {
                "homework_best": "",
                "training_best": "",
            },
        }
        _save_students(data)
    return data

def _set_last_active(user_id: int):
    data = _load_students()
    uid = str(user_id)
    if uid in data:
        data[uid]["last_active"] = datetime.utcnow().isoformat()
        _save_students(data)

def save_progress(user_id: int, key: str, value: str = "done"):
    data = _load_students()
    uid = str(user_id)
    if uid not in data:
        _ensure_user(user_id)
        data = _load_students()
    progress = data[uid].get("progress", {})
    progress[key] = value
    data[uid]["progress"] = progress
    _save_students(data)

def get_progress(user_id: int) -> dict:
    data = _load_students()
    return data.get(str(user_id), {}).get("progress", {})

def set_user_registered(user_id: int, name: str):
    data = _load_students()
    uid = str(user_id)
    _ = _ensure_user(user_id)
    data = _load_students()
    data[uid]["name"] = name
    data[uid]["key_valid"] = True
    _save_students(data)

def is_registered(user_id: int) -> bool:
    data = _load_students()
    return data.get(str(user_id), {}).get("key_valid", False)

def store_best(user_id: int, kind: str, score_str: str):  # kind in {"homework","training"}
    data = _load_students()
    uid = str(user_id)
    student = data.get(uid, {})
    stats = student.get("stats", {})
    best_key = f"{kind}_best"
    # خزن آخر نتيجة (ولو عايز: قارن بالأفضل)
    stats[best_key] = score_str
    student["stats"] = stats
    data[uid] = student
    _save_students(data)

# =========================
# 🧱 المحتوى (Foundation/Training) — بيانات عينة
# =========================
# بنية: CHAPTERS -> قائمة أبواب، كل باب فيه دروس وقواعد وأمثلة وفيديو وواجب وتدريب
CHAPTERS = [
    {
        "id": "chapter1",
        "title": "📘 الباب الأول",
        "lessons": [
            {
                "id": "lesson1",
                "title": "📖 الدرس الأول",
                "rules": [
                    {
                        "id": "rule1",
                        "title": "قاعدة الجمع / Addition Rule",
                        "summary": "الجمع يعني ضم رقمين للحصول على ناتج واحد. | Addition: combine two numbers to get a sum.",
                        "explanation_video": "https://example.com/rule1-explain",  # 🔗 ضع لينك Bunny هنا
                        "examples_videos": [
                            # 🔗 ضع لينكات الأمثلة (بحد أقصى 10 لو تحب)
                            "https://example.com/example1",
                            "https://example.com/example2",
                            "https://example.com/example3",
                            "https://example.com/example4",
                        ],
                        "homework": [  # أسئلة واجب (MCQ)
                            {
                                "id": "hw1",
                                "q": "2 + 2 = ?",
                                "options": ["3", "4", "5"],
                                "answer": 1,
                                "explanation": "٢+٢=٤ | Sum is 4. فيديو: https://example.com/hw1-explain"
                            },
                            {
                                "id": "hw2",
                                "q": "5 + 3 = ?",
                                "options": ["7", "8", "9"],
                                "answer": 1,
                                "explanation": "٥+٣=٨ | Sum is 8. فيديو: https://example.com/hw2-explain"
                            },
                        ],
                        "training_questions": [  # أسئلة تدريب (MCQ)
                            {
                                "id": "t1",
                                "q": "10 + 5 = ?",
                                "options": ["14", "15", "16"],
                                "answer": 1,
                                "explanation": "١٠+٥=١٥ | Sum is 15. فيديو: https://example.com/t1-explain"
                            },
                            {
                                "id": "t2",
                                "q": "20 - 7 = ?",
                                "options": ["12", "13", "14"],
                                "answer": 1,
                                "explanation": "٢٠-٧=١٣ | Result is 13. فيديو: https://example.com/t2-explain"
                            },
                        ],
                    }
                ],
            },
        ],
    },
    # تقدر تزود أبواب/دروس/قواعد بنفس البنية
]

# احصاء أمثلة القاعدة (نستخدمه لحساب النسبة وإظهار ✅)
def _examples_count(rule: dict) -> int:
    vids = rule.get("examples_videos") or []
    return max(1, len(vids))

# =========================
# 🎛️ الكيبوردات (Inline فقط)
# =========================
def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📘 تأسيس", callback_data="foundation")],
        [InlineKeyboardButton("📝 تدريب", callback_data="training")],
        [InlineKeyboardButton("📊 إحصائياتي", callback_data="stats")],
        [InlineKeyboardButton("🔀 سؤال عشوائي", callback_data="random_q")],
    ])

def chapters_kb(mode="foundation") -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(f"📂 {ch['title']}", callback_data=f"{mode}:chapter:{ch['id']}")] for ch in CHAPTERS]
    rows.append([InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)

def lessons_kb(chapter_id: str, mode="foundation") -> InlineKeyboardMarkup:
    ch = next((c for c in CHAPTERS if c["id"] == chapter_id), None)
    rows = []
    if ch:
        for l in ch["lessons"]:
            rows.append([InlineKeyboardButton(f"📖 {l['title']}", callback_data=f"{mode}:lesson:{chapter_id}:{l['id']}")])
    rows.append([InlineKeyboardButton("⬅️ رجوع", callback_data=f"{mode}:back")])
    return InlineKeyboardMarkup(rows)

def rules_kb(chapter_id: str, lesson_id: str, mode="foundation") -> InlineKeyboardMarkup:
    ch = next((c for c in CHAPTERS if c["id"] == chapter_id), None)
    rows = []
    if ch:
        lesson = next((l for l in ch["lessons"] if l["id"] == lesson_id), None)
        if lesson:
            for r in lesson["rules"]:
                label = f"📑 {r['title']}"
                cb = f"{mode}:rule:{chapter_id}:{lesson_id}:{r['id']}"
                rows.append([InlineKeyboardButton(label, callback_data=cb)])
    rows.append([InlineKeyboardButton("⬅️ رجوع", callback_data=f"{mode}:lesson_back:{chapter_id}")])
    return InlineKeyboardMarkup(rows)

def rule_content_kb(user_id: int, chapter_id: str, lesson_id: str, rule_id: str, mode="foundation") -> InlineKeyboardMarkup:
    # نحدّث الأمثلة المكتملة بعلامة ✅ + واجب ✅ إن اكتمل
    progress = get_progress(user_id)
    ch = next((c for c in CHAPTERS if c["id"] == chapter_id), None)
    lesson = next((l for l in ch["lessons"] if l["id"] == lesson_id), None) if ch else None
    rule = next((r for r in lesson["rules"] if r["id"] == rule_id), None) if lesson else None
    n = _examples_count(rule) if rule else 10
    rows = [[InlineKeyboardButton("🎥 شرح القاعدة", callback_data=f"{mode}:explain:{chapter_id}:{lesson_id}:{rule_id}")]]
    for i in range(1, n + 1):
        k = f"{chapter_id}:{lesson_id}:{rule_id}:example{i}"
        label = f"✅ مثال {i}" if progress.get(k) == "done" else f"📝 مثال {i}"
        rows.append([InlineKeyboardButton(label, callback_data=f"{mode}:example:{chapter_id}:{lesson_id}:{rule_id}:{i}")])
    # واجب
    hw_key = f"{chapter_id}:{lesson_id}:{rule_id}:homework"
    hw_label = "✅ واجب" if progress.get(hw_key) == "done" else "📒 واجب"
    rows.append([InlineKeyboardButton(hw_label, callback_data=f"{mode}:homework:{chapter_id}:{lesson_id}:{rule_id}")])
    rows.append([InlineKeyboardButton("⬅️ رجوع", callback_data=f"{mode}:lesson_back:{chapter_id}")])
    return InlineKeyboardMarkup(rows)

def example_feedback_kb(mode: str, chapter_id: str, lesson_id: str, rule_id: str, idx: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ فهمت", callback_data=f"{mode}:got:{chapter_id}:{lesson_id}:{rule_id}:{idx}"),
            InlineKeyboardButton("🔄 إعادة", callback_data=f"{mode}:redo:{chapter_id}:{lesson_id}:{rule_id}:{idx}"),
        ]
    ])

def mcq_kb(prefix: str, qid: str, options: list) -> InlineKeyboardMarkup:
    # prefix = "hwans" أو "trans"
    rows = [[InlineKeyboardButton(opt, callback_data=f"{prefix}:{qid}:{i}")] for i, opt in enumerate(options)]
    return InlineKeyboardMarkup(rows)

# =========================
# 🧮 أدوات مساعدة (نسبة / بادجات / محفزات)
# =========================
def _rand_emoji() -> str:
    return random.choice(POSITIVE_EMOJI)

def _rand_text() -> str:
    return random.choice(POSITIVE_TEXTS)

def _calc_total_items() -> int:
    # إجمالي العناصر التي يمكن للطالب إنجازها (أمثلة + واجبات)
    total = 0
    for ch in CHAPTERS:
        for l in ch["lessons"]:
            for r in l["rules"]:
                total += _examples_count(r) + 1  # +1 للواجب
    return max(1, total)

def _calc_user_done(user_id: int) -> int:
    pr = get_progress(user_id)
    return sum(1 for v in pr.values() if v == "done")

def _progress_pct(user_id: int) -> int:
    total = _calc_total_items()
    done = _calc_user_done(user_id)
    return int((done / total) * 100)

def _badge_for_pct(p: int) -> str:
    if p >= 90: return "🏅 ذهبي"
    if p >= 70: return "🥈 فضي"
    if p >= 50: return "🥉 برونزي"
    return "📘 مبتدئ"

# =========================
# 🚦 التدفق العام (Handlers)
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ensure_user(update.effective_user.id)
    _set_last_active(update.effective_user.id)

    if not is_registered(update.effective_user.id):
        await update.message.reply_text("🔑 من فضلك أدخل مفتاح الدخول (Product Key):")
        return

    await update.message.reply_text("👋 أهلاً بك! اختر من القائمة:", reply_markup=main_menu_kb())

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ensure_user(update.effective_user.id)
    _set_last_active(update.effective_user.id)

    uid = update.effective_user.id
    txt = (update.message.text or "").strip()

    # لو مش مسجل → اعتبر الرسالة مفتاح
    if not is_registered(uid):
        if txt in DEFAULT_VALID_KEYS:
            set_user_registered(uid, update.effective_user.full_name or "طالب")
            await update.message.reply_text(f"✅ مفتاح صحيح! {_rand_emoji()}\nمرحبًا {update.effective_user.full_name}.",
                                            reply_markup=main_menu_kb())
        else:
            await update.message.reply_text("❌ مفتاح غير صحيح. حاول مرة تانية.")
        return

    # أوامر نصية إضافية بسيطة
    if txt.lower() in {"menu", "main", "الرئيسية"}:
        await update.message.reply_text("🏠 القائمة الرئيسية:", reply_markup=main_menu_kb())
        return

    await update.message.reply_text("استخدم الأزرار الظاهرة 👇", reply_markup=main_menu_kb())

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ensure_user(update.effective_user.id)
    _set_last_active(update.effective_user.id)

    uid = update.effective_user.id
    pct = _progress_pct(uid)
    badge = _badge_for_pct(pct)
    pr = get_progress(uid)
    total_done = _calc_user_done(uid)
    total_all = _calc_total_items()
    await update.message.reply_text(
        f"📊 تقدمك:\n"
        f"• المكتمل: {total_done}/{total_all}\n"
        f"• النسبة: {pct}%\n"
        f"• الشارة: {badge}\n"
        f"• عناصر منجزة: {len(pr)}\n"
    )

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _ensure_user(query.from_user.id)
    _set_last_active(query.from_user.id)

    data = query.data
    uid = query.from_user.id

    # الرئيسية
    if data == "main_menu":
        await query.edit_message_text("🏠 القائمة الرئيسية:", reply_markup=main_menu_kb())
        return

    # ————— التأسيس —————
    if data == "foundation":
        await query.edit_message_text("📘 اختر الباب:", reply_markup=chapters_kb(mode="foundation"))
        return

    if data.startswith("foundation:back"):
        await query.edit_message_text("📘 اختر الباب:", reply_markup=chapters_kb(mode="foundation"))
        return

    if data.startswith("foundation:chapter:"):
        _, _, chapter_id = data.split(":")
        await query.edit_message_text("📖 اختر الدرس:", reply_markup=lessons_kb(chapter_id, mode="foundation"))
        return

    if data.startswith("foundation:lesson:"):
        _, _, chapter_id, lesson_id = data.split(":")
        await query.edit_message_text("📑 اختر القاعدة:", reply_markup=rules_kb(chapter_id, lesson_id, mode="foundation"))
        return

    if data.startswith("foundation:lesson_back:"):
        _, _, chapter_id = data.split(":")
        await query.edit_message_text("📖 اختر الدرس:", reply_markup=lessons_kb(chapter_id, mode="foundation"))
        return

    if data.startswith("foundation:rule:"):
        _, _, chapter_id, lesson_id, rule_id = data.split(":")
        await query.edit_message_text("📦 محتوى القاعدة:",
                                      reply_markup=rule_content_kb(uid, chapter_id, lesson_id, rule_id, mode="foundation"))
        return

    if data.startswith("foundation:explain:"):
        _, _, chapter_id, lesson_id, rule_id = data.split(":")
        # جِيب فيديو الشرح من البيانات
        ch = next((c for c in CHAPTERS if c["id"] == chapter_id), None)
        lesson = next((l for l in ch["lessons"] if l["id"] == lesson_id), None) if ch else None
        rule = next((r for r in lesson["rules"] if r["id"] == rule_id), None) if lesson else None
        url = rule.get("explanation_video", "لا يوجد فيديو شرح حالياً") if rule else "لا يوجد فيديو شرح"
        await query.message.reply_text(f"🎥 فيديو الشرح:\n{url}")
        return

    if data.startswith("foundation:example:"):
        _, _, chapter_id, lesson_id, rule_id, idx = data.split(":")
        idx = int(idx)
        ch = next((c for c in CHAPTERS if c["id"] == chapter_id), None)
        lesson = next((l for l in ch["lessons"] if l["id"] == lesson_id), None) if ch else None
        rule = next((r for r in lesson["rules"] if r["id"] == rule_id), None) if lesson else None
        vids = rule.get("examples_videos") or []
        if 1 <= idx <= len(vids):
            await query.message.reply_text(f"📺 مثال {idx}:\n{vids[idx-1]}")
        else:
            await query.message.reply_text(f"📺 مثال {idx}:\n(أضف لينك الفيديو في البيانات)")
        await query.message.reply_text(
            "هل فهمت المثال؟",
            reply_markup=example_feedback_kb("foundation", chapter_id, lesson_id, rule_id, idx)
        )
        return

    if data.startswith("foundation:got:"):
        _, _, chapter_id, lesson_id, rule_id, idx = data.split(":")
        save_progress(uid, f"{chapter_id}:{lesson_id}:{rule_id}:example{idx}", "done")
        # رجّع قائمة القاعدة محدثة
        await query.message.reply_text(
            f"{_rand_text()} {_rand_emoji()}",
            reply_markup=rule_content_kb(uid, chapter_id, lesson_id, rule_id, mode="foundation")
        )
        return

    if data.startswith("foundation:redo:"):
        _, _, chapter_id, lesson_id, rule_id, idx = data.split(":")
        await query.message.reply_text(f"🔁 إعادة مشاهدة مثال {idx}\n(أعد فتح فيديو المثال من القائمة)")
        return

    if data.startswith("foundation:homework:"):
        _, _, chapter_id, lesson_id, rule_id = data.split(":")
        # جهز أسئلة الواجب في user_data
        ch = next((c for c in CHAPTERS if c["id"] == chapter_id), None)
        lesson = next((l for l in ch["lessons"] if l["id"] == lesson_id), None) if ch else None
        rule = next((r for r in lesson["rules"] if r["id"] == rule_id), None) if lesson else None
        qs = rule.get("homework") or []
        if not qs:
            await query.edit_message_text("لا يوجد واجب حالياً.")
            return
        context.user_data["hw_ctx"] = {
            "chapter_id": chapter_id,
            "lesson_id": lesson_id,
            "rule_id": rule_id,
            "idx": 0,
            "score": 0,
            "qs": qs,
        }
        q = qs[0]
        await query.edit_message_text(f"📝 {q['q']}", reply_markup=mcq_kb("hwans", q["id"], q["options"]))
        return

    # ————— التدريب —————
    if data == "training":
        await query.edit_message_text("📘 اختر الباب للتدريب:", reply_markup=chapters_kb(mode="training"))
        return

    if data.startswith("training:back"):
        await query.edit_message_text("📘 اختر الباب للتدريب:", reply_markup=chapters_kb(mode="training"))
        return

    if data.startswith("training:chapter:"):
        _, _, chapter_id = data.split(":")
        await query.edit_message_text("📖 اختر الدرس:", reply_markup=lessons_kb(chapter_id, mode="training"))
        return

    if data.startswith("training:lesson:"):
        _, _, chapter_id, lesson_id = data.split(":")
        await query.edit_message_text("📑 اختر القاعدة:", reply_markup=rules_kb(chapter_id, lesson_id, mode="training"))
        return

    if data.startswith("training:lesson_back:"):
        _, _, chapter_id = data.split(":")
        await query.edit_message_text("📖 اختر الدرس:", reply_markup=lessons_kb(chapter_id, mode="training"))
        return

    if data.startswith("training:rule:"):
        _, _, chapter_id, lesson_id, rule_id = data.split(":")
        # جهز أسئلة التدريب
        ch = next((c for c in CHAPTERS if c["id"] == chapter_id), None)
        lesson = next((l for l in ch["lessons"] if l["id"] == lesson_id), None) if ch else None
        rule = next((r for r in lesson["rules"] if r["id"] == rule_id), None) if lesson else None
        qs = rule.get("training_questions") or []
        if not qs:
            await query.edit_message_text("لا يوجد تدريب لهذه القاعدة حالياً.")
            return
        context.user_data["tr_ctx"] = {
            "chapter_id": chapter_id,
            "lesson_id": lesson_id,
            "rule_id": rule_id,
            "idx": 0,
            "score": 0,
            "qs": qs,
        }
        q = qs[0]
        await query.edit_message_text(f"📝 {q['q']}", reply_markup=mcq_kb("trans", q["id"], q["options"]))
        return

    # ————— سؤال عشوائي —————
    if data == "random_q":
        # التقط سؤال عشوائي من كل التدريب المتاح
        pool = []
        for ch in CHAPTERS:
            for l in ch["lessons"]:
                for r in l["rules"]:
                    for qq in r.get("training_questions") or []:
                        pool.append((ch["id"], l["id"], r["id"], qq))
        if not pool:
            await query.edit_message_text("لا توجد أسئلة حالياً.")
            return
        ch_id, l_id, r_id, qq = random.choice(pool)
        context.user_data["rnd_ctx"] = {
            "chapter_id": ch_id, "lesson_id": l_id, "rule_id": r_id, "q": qq
        }
        await query.edit_message_text(f"🎲 {qq['q']}", reply_markup=mcq_kb("rndans", qq["id"], qq["options"]))
        return

    # ————— إحصائياتي (زر من القائمة) —————
    if data == "stats":
        pct = _progress_pct(uid)
        badge = _badge_for_pct(pct)
        pr = get_progress(uid)
        total_done = _calc_user_done(uid)
        total_all = _calc_total_items()
        await query.edit_message_text(
            f"📊 تقدمك:\n"
            f"• المكتمل: {total_done}/{total_all}\n"
            f"• النسبة: {pct}%\n"
            f"• الشارة: {badge}\n"
            f"• عناصر منجزة: {len(pr)}\n",
            reply_markup=main_menu_kb()
        )
        return

    # لو وصلنا هنا وما اتعرفناش على الحدث
    await query.edit_message_text("⚠️ اختيار غير معروف.", reply_markup=main_menu_kb())

# =========================
# 🧩 إجابات MCQ (واجب/تدريب/عشوائي)
# =========================
async def mcq_answer_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _set_last_active(query.from_user.id)
    data = query.data
    uid = query.from_user.id

    # ——— واجب ———
    if data.startswith("hwans:"):
        _, qid, i = data.split(":")
        i = int(i)
        hw = context.user_data.get("hw_ctx")
        if not hw:
            await query.edit_message_text("انتهى الواجب أو لم يبدأ.")
            return

        idx = hw["idx"]
        qs = hw["qs"]
        if idx >= len(qs):
            await query.edit_message_text("انتهى الواجب.")
            return
        q = qs[idx]
        correct = (i == q["answer"])
        if correct:
            hw["score"] += 1
            await query.edit_message_text(f"{_rand_text()} {_rand_emoji()} ✅")
        else:
            await query.edit_message_text(f"❌ إجابة غير صحيحة.\n📺 الشرح: {q.get('explanation','')}")

        # التالي
        idx += 1
        hw["idx"] = idx
        context.user_data["hw_ctx"] = hw

        if idx < len(qs):
            nq = qs[idx]
            await query.message.reply_text(f"📝 {nq['q']}", reply_markup=mcq_kb("hwans", nq["id"], nq["options"]))
        else:
            score = hw["score"]
            total = len(qs)
            pct = round((score / total) * 100)
            store_best(uid, "homework", f"{score}/{total}")
            # علّم الواجب كمكتمل
            save_progress(uid, f"{hw['chapter_id']}:{hw['lesson_id']}:{hw['rule_id']}:homework", "done")

            if pct >= 80:
                lvl = "🎉 ممتاز! مستواك عالي جدًا"
            elif pct >= 50:
                lvl = "👍 جيد، محتاج مراجعة بسيطة"
            else:
                lvl = "⚠️ محتاج تراجع القاعدة دي تاني"

            await query.message.reply_text(
                f"📊 خلصت الواجب!\nنتيجتك: {score}/{total} ({pct}%)\n{lvl}\n{_rand_emoji()}",
                reply_markup=rule_content_kb(uid, hw["chapter_id"], hw["lesson_id"], hw["rule_id"], mode="foundation"),
            )
        return

    # ——— تدريب ———
    if data.startswith("trans:"):
        _, qid, i = data.split(":")
        i = int(i)
        tr = context.user_data.get("tr_ctx")
        if not tr:
            await query.edit_message_text("انتهى التدريب أو لم يبدأ.")
            return

        idx = tr["idx"]
        qs = tr["qs"]
        if idx >= len(qs):
            await query.edit_message_text("انتهى التدريب.")
            return
        q = qs[idx]
        correct = (i == q["answer"])
        if correct:
            tr["score"] += 1
            await query.edit_message_text(f"{_rand_text()} {_rand_emoji()} ✅")
        else:
            await query.edit_message_text(f"❌ إجابة غير صحيحة.\n📺 الشرح: {q.get('explanation','')}")

        idx += 1
        tr["idx"] = idx
        context.user_data["tr_ctx"] = tr

        if idx < len(qs):
            nq = qs[idx]
            await query.message.reply_text(f"📝 {nq['q']}", reply_markup=mcq_kb("trans", nq["id"], nq["options"]))
        else:
            score = tr["score"]
            total = len(qs)
            pct = round((score / total) * 100)
            store_best(uid, "training", f"{score}/{total}")

            if pct >= 80:
                lvl = "🎉 ممتاز! متفوق جدًا"
            elif pct >= 50:
                lvl = "👍 جيد، محتاج مراجعة بسيطة"
            else:
                lvl = "⚠️ محتاج تذاكر أكتر"

            # بعد التدريب نرجع للقائمة الرئيسية
            await query.message.reply_text(
                f"📊 خلصت التدريب!\nنتيجتك: {score}/{total} ({pct}%)\n{lvl}\n{_rand_emoji()}",
                reply_markup=main_menu_kb(),
            )
        return

    # ——— سؤال عشوائي ———
    if data.startswith("rndans:"):
        _, qid, i = data.split(":")
        i = int(i)
        rnd = context.user_data.get("rnd_ctx")
        if not rnd:
            await query.edit_message_text("السؤال العشوائي غير جاهز.")
            return
        q = rnd["q"]
        correct = (i == q["answer"])
        if correct:
            await query.edit_message_text(f"{_rand_text()} {_rand_emoji()} ✅")
        else:
            await query.edit_message_text(f"❌ إجابة غير صحيحة.\n📺 الشرح: {q.get('explanation','')}")

        await query.message.reply_text("🎯 اختر من القائمة:", reply_markup=main_menu_kb())
        context.user_data.pop("rnd_ctx", None)
        return

    await query.edit_message_text("⚠️ اختيار غير معروف.", reply_markup=main_menu_kb())

# =========================
# ⏰ تذكير يومي تلقائي
# =========================
async def daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    data = _load_students()
    if not data:
        return
    now = datetime.utcnow()
    for uid, info in data.items():
        last = info.get("last_active")
        try:
            last_dt = datetime.fromisoformat(last) if last else now
        except Exception:
            last_dt = now
        if now - last_dt >= timedelta(hours=24):
            try:
                await context.bot.send_message(
                    chat_id=int(uid),
                    text="📚 تذكير لطيف: كمل درس النهارده؛ خطوة صغيرة كل يوم تفرّق كتير! 🌟"
                )
            except Exception:
                continue

# =========================
# 🚀 تشغيل البوت
# =========================
def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TOKEN env var not set")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(CallbackQueryHandler(callback_router, pattern="^(foundation|training|stats|random_q|main_menu|)"))
    # كل باقي الكولباك (explain/example/got/redo/homework/…)
    app.add_handler(CallbackQueryHandler(callback_router, pattern="^(foundation:|training:)"))
    # إجابات MCQ (واجب/تدريب/عشوائي)
    app.add_handler(CallbackQueryHandler(mcq_answer_router, pattern="^(hwans:|trans:|rndans:)"))

    # JobQueue للتذكير اليومي
    app.job_queue.run_daily(daily_reminder, time=DAILY_REMINDER_UTC)

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
