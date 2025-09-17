
import json, os, time
from typing import Dict, Any
from config import DB_FILE, FEEDBACK_FILE

def _read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_students() -> Dict[str, Any]:
    return _read_json(DB_FILE, {"data": {}})

def save_students(data: Dict[str, Any]):
    _write_json(DB_FILE, data)

def ensure_student(uid: int):
    data = load_students()
    sid = str(uid)
    if sid not in data["data"]:
        data["data"][sid] = {"key": None, "progress": {}, "history": []}
        save_students(data)
    return data["data"][sid]

def set_student_key(uid: int, key: str):
    data = load_students()
    sid = str(uid)
    data["data"].setdefault(sid, {"key": None, "progress": {}, "history": []})
    data["data"][sid]["key"] = key
    save_students(data)

def get_student(uid: int):
    return load_students()["data"].get(str(uid))

def add_attempt(uid: int, section: str, path: str, score: int, total: int, percent: int):
    data = load_students()
    sid = str(uid)
    st = data["data"].setdefault(sid, {"key": None, "progress": {}, "history": []})
    st["history"].append({
        "ts": int(time.time()),
        "section": section,
        "path": path,
        "score": score,
        "total": total,
        "percent": percent
    })
    cur = st["progress"].get(section, {"best_percent": 0})
    if percent > cur.get("best_percent", 0):
        cur["best_percent"] = percent
    st["progress"][section] = cur
    save_students(data)

def get_section_badge(uid: int, section: str) -> int:
    st = get_student(uid) or {}
    prog = st.get("progress", {}).get(section, {})
    return int(prog.get("best_percent", 0))

def append_feedback(uid: int, text: str):
    fb = _read_json(FEEDBACK_FILE, {"items": []})
    fb["items"].append({"uid": uid, "text": text, "ts": int(time.time())})
    _write_json(FEEDBACK_FILE, fb)
