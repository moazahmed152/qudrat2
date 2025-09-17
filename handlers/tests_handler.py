
import json
from telegram import Update
from telegram.ext import ContextTypes
from config import TESTS_FILE
from utils.keyboards import doors_kb, lessons_kb, rules_kb, start_questions_kb, choices_kb, results_kb, back_to_main_kb
from utils.database import add_attempt, get_section_badge

def _load():
    with open(TESTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

async def tests_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    ct = _load()
    badge = get_section_badge(q.from_user.id, "tests")
    section_title = "التأسيس" if "tests"=="foundation" else ("التدريب" if "tests"=="training" else "الاختبارات")
    header = f"📘 قائمة {section_title} — تقدّمك: 🎖️ {badge}%"
    await q.edit_message_text(header, reply_markup=doors_kb("tests", ct))

async def tests_door(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    if len(parts) < 3:
        await q.edit_message_text("صيغة غير صحيحة.", reply_markup=back_to_main_kb()); return
    d = parts[2]
    ct = _load()
    door = ct.get("doors", {}).get(d)
    if not door:
        await q.edit_message_text("🚧 الباب غير متاح.", reply_markup=back_to_main_kb()); return
    await q.edit_message_text(f"🚪 الباب {d} — اختر درس:", reply_markup=lessons_kb("tests", d, door))

async def tests_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    if len(parts) < 5:
        await q.edit_message_text("صيغة غير صحيحة.", reply_markup=back_to_main_kb()); return
    d, l = parts[2], parts[4]
    ct = _load()
    door = ct.get("doors", {}).get(d, {})
    lesson = door.get("lessons", {}).get(l)
    if not lesson:
        await q.edit_message_text("🚧 الدرس غير متاح.", reply_markup=back_to_main_kb()); return
    await q.edit_message_text(f"📘 الدرس {l}: {lesson.get('title','')}\nاختر القاعدة:", reply_markup=rules_kb("tests", d, l, lesson))

async def tests_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    if len(parts) < 7:
        await q.edit_message_text("صيغة غير صحيحة.", reply_markup=back_to_main_kb()); return
    d, l, r = parts[2], parts[4], parts[6]
    ct = _load()
    rule = ct["doors"][d]["lessons"][l]["rules"][r]
    video = rule.get("video_url", "")
    text = (
        f"🔎 *{rule.get('title','قاعدة')}*\n\n"
        f"شرح:\n{rule.get('explanation','')}\n\n"
        f"مثال:\n{rule.get('example','')}\n\n"
        f"واجب:\n{rule.get('homework','')}"
    )
    if video:
        text += f"\n\n🎬 فيديو الشرح: {video}"
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=start_questions_kb("tests", d, l, r))

async def tests_startq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    try:
        d, l, r, idx = parts[4], parts[6], parts[8], int(parts[9])
    except Exception:
        await q.edit_message_text("صيغة الأسئلة غير صحيحة.", reply_markup=back_to_main_kb()); return
    ct = _load()
    questions = ct["doors"][d]["lessons"][l]["rules"][r].get("questions", [])
    context.user_data["path"] = f"door:{d}/lesson:{l}/rule:{r}"
    context.user_data["section"] = "tests"
    context.user_data["questions"] = questions
    context.user_data["q_idx"] = idx
    if idx < len(questions):
        qd = questions[idx]
        qtext = f"❓ سؤال {idx+1}/{len(questions)}\n{qd['text']}"
        await q.edit_message_text(qtext, reply_markup=choices_kb(f"tests:{qd['id']}", qd['choices']))
    else:
        answers = context.user_data.get("answers", {})
        total = len(questions)
        correct = 0
        for qx in questions:
            sel = int(answers.get(qx["id"], 0))
            if sel == int(qx["answer_index"]):
                correct += 1
        percent = int((correct/total)*100) if total else 0
        from utils.database import add_attempt
        add_attempt(q.from_user.id, "tests", context.user_data.get("path",""), correct, total, percent)
        context.user_data.pop("questions", None)
        context.user_data.pop("q_idx", None)
        context.user_data.pop("path", None)
        context.user_data.pop("section", None)
        context.user_data.pop("answers", None)
        res = f"✅ انتهت الأسئلة!\nالنتيجة: *{correct}* من *{total}*\nالنسبة: *{percent}%*"
        await q.edit_message_text(res, parse_mode="Markdown", reply_markup=results_kb("tests", d, l, r))

async def tests_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    if len(parts) != 3:
        await q.edit_message_text("إجابة غير مفهومة.", reply_markup=back_to_main_kb()); return
    _, qid, choice = parts
    context.user_data.setdefault("answers", {})
    rawid = qid.split(":", 1)[-1]
    context.user_data["answers"][rawid] = int(choice)
    idx = int(context.user_data.get("q_idx", 0)) + 1
    context.user_data["q_idx"] = idx
    path = context.user_data.get("path", "door:1/lesson:1/rule:1")
    parts2 = path.replace("/", ":").split(":")
    d, l, r = parts2[1], parts2[3], parts2[5]
    ct = _load()
    questions = ct["doors"][d]["lessons"][l]["rules"][r].get("questions", [])
    if idx < len(questions):
        qd = questions[idx]
        qtext = f"❓ سؤال {idx+1}/{len(questions)}\n{qd['text']}"
        await q.edit_message_text(qtext, reply_markup=choices_kb(f"tests:{qd['id']}", qd['choices']))
    else:
        answers = context.user_data.get("answers", {})
        total = len(questions)
        correct = 0
        for qx in questions:
            sel = int(answers.get(qx["id"], 0))
            if sel == int(qx["answer_index"]):
                correct += 1
        percent = int((correct/total)*100) if total else 0
        from utils.database import add_attempt
        add_attempt(q.from_user.id, "tests", context.user_data.get("path",""), correct, total, percent)
        context.user_data.clear()
        res = f"✅ انتهت الأسئلة!\nالنتيجة: *{correct}* من *{total}*\nالنسبة: *{percent}%*"
        await q.edit_message_text(res, parse_mode="Markdown", reply_markup=results_kb("tests", d, l, r))
