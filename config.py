# -*- coding: utf-8 -*-
"""
ไฟล์ตั้งค่าระบบ
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# โหลดไฟล์ .env
load_dotenv()

# ข้อมูลพื้นฐาน
APP_NAME = os.getenv("APP_NAME", "ผู้เชี่ยวชาญถั่วซิกฟี")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# เส้นทางไฟล์
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backups"

# สร้างโฟลเดอร์หากไม่มี
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

# ตั้งค่างาน
SCHEDULE_TIMES = {
    "report": os.getenv("SCHEDULE_REPORT_TIME", "09:00"),
    "backup": os.getenv("SCHEDULE_BACKUP_TIME", "12:00"),
    "check": os.getenv("SCHEDULE_CHECK_TIME", "15:00"),
    "cleanup": os.getenv("SCHEDULE_CLEANUP_TIME", "18:00"),
}

# การแจ้งเตือน
NOTIFY_ON_ERROR = os.getenv("NOTIFY_ON_ERROR", "true").lower() == "true"
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "")
