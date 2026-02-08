#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ระบบทำงานอัตโนมัติหลัก - เวอร์ชัน 2.0 (ระบบสมบูรณ์)
"""

import schedule
import time
import logging
import threading
from datetime import datetime
from pathlib import Path

from config import APP_NAME, LOG_DIR, DATA_DIR, BACKUP_DIR, SCHEDULE_TIMES
from api import app as flask_app
from file_watcher import FileWatcher, scan_directory
from data_processor import DataProcessor
from utils import create_backup, cleanup_old_files, generate_report, check_system_health

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutomationSystem:
    """ระบบอัตโนมัติสมบูรณ์"""
    
    def __init__(self):
        self.name = APP_NAME
        self.running = True
        self.processor = DataProcessor(DATA_DIR / 'uploads', DATA_DIR / 'results')
        logger.info(f"🚀 เริ่มต้น {self.name} v2.0 (ระบบสมบูรณ์)")
    
    # ===== งานอัตโนมัติ =====
    
    def task_daily_report(self):
        """งานรายวันสรุปรายงาน"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            summary = self.processor.generate_summary()
            generate_report("รายงานประจำวัน", str(summary))
            logger.info(f"✓ สรุปรายงานประจำวัน - {timestamp}")
        except Exception as e:
            logger.error(f"ข้อผิดพลาด: {e}")
    
    def task_data_backup(self):
        """งานสำรองข้อมูล"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            create_backup(str(DATA_DIR), str(BACKUP_DIR))
            logger.info(f"✓ สำรองข้อมูล - {timestamp}")
        except Exception as e:
            logger.error(f"ข้อผิดพลาด: {e}")
    
    def task_system_check(self):
        """งานตรวจสอบระบบ"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            health = check_system_health()
            logger.info(f"✓ ตรวจสอบระบบ - {timestamp}")
        except Exception as e:
            logger.error(f"ข้อผิดพลาด: {e}")
    
    def task_cleanup(self):
        """งานล้างไฟล์ชั่วคราว"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cleanup_old_files(str(LOG_DIR), days=7)
            cleanup_old_files(str(DATA_DIR / 'uploads'), days=30)
            logger.info(f"✓ ล้างไฟล์ชั่วคราว - {timestamp}")
        except Exception as e:
            logger.error(f"ข้อผิดพลาด: {e}")
    
    def task_process_files(self):
        """งานประมวลผลไฟล์"""
        try:
            upload_dir = DATA_DIR / 'uploads'
            if upload_dir.exists():
                files = list(upload_dir.glob('*'))
                if files:
                    results = self.processor.batch_process(files)
                    logger.info(f"✓ ประมวลผลไฟล์ {len(results)} ไฟล์")
        except Exception as e:
            logger.error(f"ข้อผิดพลาด: {e}")
    
    def task_scan_uploads(self):
        """งานสแกนไฟล์ที่อัปโหลด"""
        try:
            upload_dir = DATA_DIR / 'uploads'
            files = scan_directory(str(upload_dir))
            if files:
                logger.info(f"✓ พบเพิ่มเติม {len(files)} ไฟล์")
        except Exception as e:
            logger.error(f"ข้อผิดพลาด: {e}")
    
    # ===== ตั้งค่างาน =====
    
    def schedule_tasks(self):
        """กำหนดการทำงานตามเวลา"""
        # งานรายวัน
        schedule.every().day.at(SCHEDULE_TIMES['report']).do(self.task_daily_report)
        schedule.every().day.at(SCHEDULE_TIMES['backup']).do(self.task_data_backup)
        schedule.every().day.at(SCHEDULE_TIMES['check']).do(self.task_system_check)
        schedule.every().day.at(SCHEDULE_TIMES['cleanup']).do(self.task_cleanup)
        
        # งานรายชั่วโมง
        schedule.every().hour.do(self.task_system_check)
        schedule.every().hour.do(self.task_process_files)
        schedule.every().hour.do(self.task_scan_uploads)
        
        logger.info("📅 ตั้งค่างานอัตโนมัติเสร็จสิ้น")
    
    def start_file_watcher(self):
        """เริ่ม File Watcher ในดัชนีหลัง"""
        try:
            watcher = FileWatcher([str(DATA_DIR / 'uploads')])
            watcher.start()
        except Exception as e:
            logger.error(f"ข้อผิดพลาดในการเริ่ม File Watcher: {e}")
    
    def start_api_server(self):
        """เริ่ม API Server ในดัชนีหลัง"""
        try:
            logger.info("🌐 เริ่ม API Server ที่ http://localhost:5000")
            flask_app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
        except Exception as e:
            logger.error(f"ข้อผิดพลาดในการเริ่ม API: {e}")
    
    def run(self):
        """เรียกใช้ระบบจนกว่าจะถูกหยุด"""
        self.schedule_tasks()
        
        # เริ่ม File Watcher ในดัชนีหลัง
        watcher_thread = threading.Thread(target=self.start_file_watcher, daemon=True)
        watcher_thread.start()
        
        # เริ่ม API Server ในดัชนีหลัง
        api_thread = threading.Thread(target=self.start_api_server, daemon=True)
        api_thread.start()
        
        logger.info("🚀 ระบบอัตโนมัติเริ่มทำงาน...")
        logger.info("📊 ส่วนประกอบ:")
        logger.info("   ✓ Scheduler - งานอัตโนมัติตามเวลา")
        logger.info("   ✓ File Watcher - ตรวจสอบโฟลเดอร์")
        logger.info("   ✓ Data Processor - ประมวลผลข้อมูล")
        logger.info("   ✓ API Server - อัปโหลดและจัดการไฟล์")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("⛔ หยุดระบบอัตโนมัติ")


def main():
    """ฟังก์ชันหลัก"""
    system = AutomationSystem()
    system.run()


if __name__ == "__main__":
    main()
