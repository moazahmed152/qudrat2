
from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import back_to_main_kb
from utils.database import append_feedback

async def feedback_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["awaiting_feedback"] = True
    await q.edit_message_text("💬 ابعت ملاحظتك أو اقتراحك برسالة الآن وسيتم حفظها.", reply_markup=back_to_main_kb())

async def handle_feedback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_feedback"):
        text = (update.message.text or "").strip()
        if not text:
            await update.message.reply_text("❗ اكتب ملاحظة نصية من فضلك.")
            return
        append_feedback(update.effective_user.id, text)
        context.user_data["awaiting_feedback"] = False
        await update.message.reply_text("✅ تم حفظ الملاحظة. شكرًا لك!")
    else:
        await update.message.reply_text("استخدم /start للرجوع للقائمة الرئيسية.")
