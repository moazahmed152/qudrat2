# handlers/training_handler.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.database import save_student_progress

# === بيانات تدريب تجريبية ===
TRAINING_QUESTIONS = [
    {
        "id": "t1",
        "text": "5 + 7 = ؟",
        "choices": ["10", "11", "12", "13"],
        "answer": 2  # 0-based => "12"
    },
    {
        "id": "t2",
        "text": "8 × 3 = ؟",
        "choices": ["24", "21", "18", "26"],
        "answer": 0  # => "24"
    }
]

# === القائمة الرئيسية للتدريب ===
async def training_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📘 تدريب الباب 1", callback_data="training:start:0")],
        [InlineKeyboardButton("🏠 الرئيسية", callback_data="main:menu")]
    ])
    await query.edit_message_text("🏋️ اختار التدريب:", reply_markup=kb)

# === عرض سؤال معين ===
async def training_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split(":")
    idx = int(parts[-1])
    if idx < len(TRAINING_QUESTIONS):
        q = TRAINING_QUESTIONS[idx]
        kb = [[InlineKeyboardButton(ch, callback_data=f"train_ans:{idx}:{i}")]
              for i, ch in enumerate(q["choices"])]
        await query.edit_message_text(
            f"❓ تدريب {idx+1}/{len(TRAINING_QUESTIONS)}\n{q['text']}",
            reply_markup=InlineKeyboardMarkup(kb)
        )
    else:
        # انتهى التدريب
        answers = context.user_data.get("train_answers", {})
        correct = sum(1 for i, q in enumerate(TRAINING_QUESTIONS) if answers.get(i) == q["answer"])
        percent = int((correct/len(TRAINING_QUESTIONS))*100)

        # حفظ في قاعدة البيانات
        save_student_progress(query.from_user.id, "training", {
            "score": correct,
            "total": len(TRAINING_QUESTIONS),
            "percent": percent
        })

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 أعد التدريب", callback_data="training:start:0")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="main:menu")]
        ])
        await query.edit_message_text(
            f"✅ خلصت التدريب!\nالنتيجة: {correct}/{len(TRAINING_QUESTIONS)}\nالنسبة: {percent}%",
            reply_markup=kb
        )

# === استقبال إجابات التدريب ===
async def training_answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, idx, choice = query.data.split(":")
    idx, choice = int(idx), int(choice)

    context.user_data.setdefault("train_answers", {})
    context.user_data["train_answers"][idx] = choice

    # التالي
    next_idx = idx + 1
    fake_cb = f"training:start:{next_idx}"
    query.data = fake_cb  # نغيّر البيانات ونرجّعها للـ start
    await training_start_handler(update, context)
