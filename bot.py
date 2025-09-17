
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, valid_keys
from utils.keyboards import main_menu_keyboard
from utils.database import ensure_student, set_student_key, get_student
import handlers.foundation_handler as fh
import handlers.training_handler as th
import handlers.tests_handler as tst
import handlers.feedback_handler as fb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ensure_student(user.id)
    student = get_student(user.id)
    if not student or not student.get("key"):
        await update.message.reply_text("🔑 ادخل الـ Product Key (مرة واحدة فقط):")
        context.user_data["awaiting_key"] = True
        return
    await update.message.reply_text("👋 أهلاً بيك! اختار من القائمة:", reply_markup=main_menu_keyboard())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_key"):
        key = (update.message.text or "").strip()
        if key in valid_keys:
            set_student_key(update.effective_user.id, key)
            context.user_data["awaiting_key"] = False
            await update.message.reply_text("✅ تم التفعيل!")
            await update.message.reply_text("👋 أهلاً بيك! اختار من القائمة:", reply_markup=main_menu_keyboard())
        else:
            await update.message.reply_text("❌ الكود غير صحيح. حاول تاني.")
        return
    await fb.handle_feedback_message(update, context)

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "main:menu":
        await q.edit_message_text("👋 أهلاً بيك! اختار من القائمة:", reply_markup=main_menu_keyboard()); return

    # Foundation
    if data.startswith("foundation:menu"):
        await fh.foundation_menu(update, context); return
    if data.startswith("foundation:door:") and "lesson" not in data:
        await fh.foundation_door(update, context); return
    if data.startswith("foundation:door:") and "lesson" in data and "rule" not in data:
        await fh.foundation_lesson(update, context); return
    if data.startswith("foundation:door:") and "rule" in data and "startq" not in data:
        await fh.foundation_rule(update, context); return
    if data.startswith("foundation:startq:"):
        await fh.foundation_startq(update, context); return

    # Training
    if data.startswith("training:menu"):
        await th.training_menu(update, context); return
    if data.startswith("training:door:") and "lesson" not in data:
        await th.training_door(update, context); return
    if data.startswith("training:door:") and "lesson" in data and "rule" not in data:
        await th.training_lesson(update, context); return
    if data.startswith("training:door:") and "rule" in data and "startq" not in data:
        await th.training_rule(update, context); return
    if data.startswith("training:startq:"):
        await th.training_startq(update, context); return

    # Tests
    if data.startswith("tests:menu"):
        await tst.tests_menu(update, context); return
    if data.startswith("tests:door:") and "lesson" not in data:
        await tst.tests_door(update, context); return
    if data.startswith("tests:door:") and "lesson" in data and "rule" not in data:
        await tst.tests_lesson(update, context); return
    if data.startswith("tests:door:") and "rule" in data and "startq" not in data:
        await tst.tests_rule(update, context); return
    if data.startswith("tests:startq:"):
        await tst.tests_startq(update, context); return

    # Answers
    if data.startswith("ans:foundation:"):
        await fh.foundation_answer(update, context); return
    if data.startswith("ans:training:"):
        await th.training_answer(update, context); return
    if data.startswith("ans:tests:"):
        await tst.tests_answer(update, context); return

    await q.edit_message_text("🔄 لم أفهم الأمر، رجعتك للقائمة.", reply_markup=main_menu_keyboard())

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(callback_router))
    logger.info("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
