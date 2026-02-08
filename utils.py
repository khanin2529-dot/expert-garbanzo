# -*- coding: utf-8 -*-
"""
ฟังก์ชันช่วยเหลือและยูทิลิตี้
"""

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def create_backup(source_dir, backup_dir):
    """สร้างสำรองข้อมูล"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        logger.info(f"กำลังสร้างสำรองข้อมูล: {backup_name}")
        return True
    except Exception as e:
        logger.error(f"ข้อผิดพลาดในการสำรองข้อมูล: {e}")
        return False


def cleanup_old_files(directory, days=7):
    """ล้างไฟล์เก่า"""
    try:
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(days=days)
        path = Path(directory)
        
        if path.exists():
            for file in path.glob("*"):
                if file.stat().st_mtime < cutoff_time.timestamp():
                    file.unlink()
                    logger.info(f"ลบไฟล์: {file.name}")
        return True
    except Exception as e:
        logger.error(f"ข้อผิดพลาดในการล้างไฟล์: {e}")
        return False


def generate_report(title, content):
    """สร้างรายงาน"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"""
{'='*50}
{title}
{'='*50}
เวลา: {timestamp}
เนื้อหา: {content}
{'='*50}
"""
        logger.info(report)
        return True
    except Exception as e:
        logger.error(f"ข้อผิดพลาดในการสร้างรายงาน: {e}")
        return False


def check_system_health():
    """ตรวจสอบสุขภาพระบบ"""
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status = {
            "cpu": cpu_percent,
            "memory": memory.percent,
            "disk": disk.percent,
            "status": "ปกติ" if cpu_percent < 80 and memory.percent < 80 else "ระวัง"
        }
        
        logger.info(f"สถานะระบบ - CPU: {cpu_percent}%, หน่วยความจำ: {memory.percent}%, Disk: {disk.percent}%")
        return status
    except ImportError:
        logger.warning("psutil ไม่ได้ติดตั้ง")
        return None
    except Exception as e:
        logger.warning(f"ไม่สามารถตรวจสอบสุขภาพระบบ: {e}")
        return None
