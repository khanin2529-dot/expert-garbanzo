# -*- coding: utf-8 -*-
"""
File Watcher - ตรวจสอบโฟลเดอร์และจัดการไฟล์ใหม่
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class FileChangeHandler(FileSystemEventHandler):
    """จัดการเหตุการณ์การเปลี่ยนแปลงไฟล์"""
    
    def on_created(self, event):
        """เมื่อสร้างไฟล์ใหม่"""
        if not event.is_directory:
            filename = Path(event.src_path).name
            logger.info(f"📥 ตรวจพบไฟล์ใหม่: {filename}")
    
    def on_deleted(self, event):
        """เมื่อลบไฟล์"""
        if not event.is_directory:
            filename = Path(event.src_path).name
            logger.info(f"🗑️ ตรวจพบการลบไฟล์: {filename}")
    
    def on_modified(self, event):
        """เมื่อแก้ไขไฟล์"""
        if not event.is_directory:
            filename = Path(event.src_path).name
            file_size = os.path.getsize(event.src_path)
            logger.info(f"✏️ ไฟล์ถูกแก้ไข: {filename} ({file_size} bytes)")


class FileWatcher:
    """ตรวจสอบโฟลเดอร์อัตโนมัติ"""
    
    def __init__(self, watch_paths):
        """
        Args:
            watch_paths: รายชื่อโฟลเดอร์ที่ต้องการตรวจสอบ
        """
        self.watch_paths = watch_paths
        self.observer = Observer()
    
    def start(self):
        """เริ่มการตรวจสอบ"""
        try:
            event_handler = FileChangeHandler()
            
            for path in self.watch_paths:
                if Path(path).exists():
                    self.observer.schedule(event_handler, str(path), recursive=True)
                    logger.info(f"👀 เริ่มตรวจสอบ: {path}")
                else:
                    logger.warning(f"⚠️ ไม่พบโฟลเดอร์: {path}")
            
            self.observer.start()
            logger.info("🔍 File Watcher เริ่มทำงาน")
        
        except Exception as e:
            logger.error(f"ข้อผิดพลาดในการเริ่ม File Watcher: {e}")
    
    def stop(self):
        """หยุดการตรวจสอบ"""
        try:
            self.observer.stop()
            self.observer.join()
            logger.info("⛔ File Watcher หยุด")
        
        except Exception as e:
            logger.error(f"ข้อผิดพลาด: {e}")


def get_file_info(filepath):
    """ดึงข้อมูลไฟล์"""
    try:
        path = Path(filepath)
        stat = path.stat()
        
        return {
            'name': path.name,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'extension': path.suffix
        }
    
    except Exception as e:
        logger.error(f"ข้อผิดพลาด: {e}")
        return None


def scan_directory(directory):
    """สแกนไฟล์ในโฟลเดอร์"""
    try:
        path = Path(directory)
        files = []
        
        for file in path.rglob('*'):
            if file.is_file():
                files.append(get_file_info(file))
        
        logger.info(f"📊 พบไฟล์ {len(files)} ไฟล์ ใน {directory}")
        return files
    
    except Exception as e:
        logger.error(f"ข้อผิดพลาด: {e}")
        return []
