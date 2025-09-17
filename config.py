
# config.py
import os

# اقرأ التوكن من الـ Environment Variables بتاعت Railway
TELEGRAM_BOT_TOKEN = os.getenv("TOKEN")

valid_keys = ["a", "XYZ789", "TESTKEY"]
DB_FILE = "students.json"
FEEDBACK_FILE = "feedback.json"
CONTENT_DIR = "content"
FOUNDATION_FILE = f"{CONTENT_DIR}/foundation.json"
TRAINING_FILE  = f"{CONTENT_DIR}/training.json"
TESTS_FILE     = f"{CONTENT_DIR}/tests.json"
