# handlers/foundation_handler.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.keyboards import back_to_main_kb
from utils.database import save_student_progress

# === بيانات الأسئلة (تقدر تزود أسئلة بنفس الشكل) ===
QUESTIONS = [
    {
        "id": "q1",
        "text": "√49 = ؟",
        "choices": ["6", "7", "8", "9"],
        "answer": 1  # 0-based index => "7"
    },
    {
        "id": "q2",
        "text": "√81 = ؟",
        "choices": ["7", "8", "9", "10"],
        "answer": 2  # => "9"
    }
]

# === القائمة الرئيسية للتأسيس ===
async def foundation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📘 الدرس 1", callback_data="foundation:lesson1")],
        [InlineKeyboardButton("🏠 الرئيسية", callback_data="main:menu")]
    ])
    await query.edit_message_text("📘 اختار الدرس:", reply_markup=kb)

# === فتح الدرس وعرض زرار الأسئلة ===
async def foundation_door_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ ابدأ الأسئلة", callback_data="foundation:start:0")],
        [InlineKeyboardButton("🏠 الرئيسية", callback_data="main:menu")]
    ])
    await query.edit_message_text("📘 الدرس 1: الجذور والقوى\n\nشرح: الجذر التربيعي لعدد موجب هو العدد الذي مربعُه يعطي العدد.\n\nمثال: √49 = 7\n\n📌 اضغط ابدأ الأسئلة للتجربة:", reply_markup=kb)

# === عرض سؤال معين ===
async def foundation_start_questions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split(":")
    idx = int(parts[-1])  # رقم السؤال الحالي
    if idx < len(QUESTIONS):
        q = QUESTIONS[idx]
        kb = [[InlineKeyboardButton(ch, callback_data=f"ans:{idx}:{i}")]
              for i, ch in enumerate(q["choices"])]
        await query.edit_message_text(
            f"❓ سؤال {idx+1}/{len(QUESTIONS)}\n{q['text']}",
            reply_markup=InlineKeyboardMarkup(kb)
        )
    else:
        # خلص الامتحان
        answers = context.user_data.get("answers", {})
        correct = sum(1 for i, q in enumerate(QUESTIONS) if answers.get(i) == q["answer"])
        percent = int((correct/len(QUESTIONS))*100)

        # حفظ التقدّم
        save_student_progress(query.from_user.id, "foundation", {
            "score": correct,
            "total": len(QUESTIONS),
            "percent": percent
        })

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 أعد المحاولة", callback_data="foundation:start:0")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="main:menu")]
        ])
        await query.edit_message_text(
            f"✅ خلصت!\nالنتيجة: {correct}/{len(QUESTIONS)}\nالنسبة: {percent}%",
            reply_markup=kb
        )

# === استقبال الإجابة والانتقال للسؤال التالي ===
async def foundation_answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, idx, choice = query.data.split(":")
    idx, choice = int(idx), int(choice)

    context.user_data.setdefault("answers", {})
    context.user_data["answers"][idx] = choice

    # التالي
    next_idx = idx + 1
    await foundation_start_questions_handler(update, context)
