# -*- coding: utf-8 -*-
"""
Data Processor - ประมวลผลและวิเคราะห์ข้อมูล
"""

import logging
import json
import csv
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class DataProcessor:
    """ประมวลผลข้อมูลจากไฟล์"""
    
    def __init__(self, input_dir, output_dir):
        """
        Args:
            input_dir: โฟลเดอร์ไฟล์อินพุต
            output_dir: โฟลเดอร์ไฟล์เอาต์พุต
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def process_csv(self, filepath):
        """ประมวลผล CSV"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            
            logger.info(f"✓ ประมวลผล CSV: {Path(filepath).name} ({len(data)} แถว)")
            return {
                'type': 'csv',
                'file': Path(filepath).name,
                'rows': len(data),
                'columns': list(reader.fieldnames) if reader.fieldnames else []
            }
        
        except Exception as e:
            logger.error(f"ข้อผิดพลาด: {e}")
            return None
    
    def process_json(self, filepath):
        """ประมวลผล JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"✓ ประมวลผล JSON: {Path(filepath).name}")
            return {
                'type': 'json',
                'file': Path(filepath).name,
                'keys': list(data.keys()) if isinstance(data, dict) else 'array',
                'size': len(data) if isinstance(data, (dict, list)) else 1
            }
        
        except Exception as e:
            logger.error(f"ข้อผิดพลาด: {e}")
            return None
    
    def process_text(self, filepath):
        """ประมวลผลไฟล์ข้อความ"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            words = content.split()
            
            logger.info(f"✓ ประมวลผล Text: {Path(filepath).name}")
            return {
                'type': 'text',
                'file': Path(filepath).name,
                'lines': len(lines),
                'words': len(words),
                'characters': len(content)
            }
        
        except Exception as e:
            logger.error(f"ข้อผิดพลาด: {e}")
            return None
    
    def process_file(self, filepath):
        """ประมวลผลไฟล์ตามประเภท"""
        filepath = Path(filepath)
        extension = filepath.suffix.lower()
        
        if extension == '.csv':
            return self.process_csv(filepath)
        elif extension == '.json':
            return self.process_json(filepath)
        elif extension in ['.txt', '.log']:
            return self.process_text(filepath)
        else:
            logger.warning(f"⚠️ ประเภทไฟล์ไม่รับรอง: {extension}")
            return None
    
    def batch_process(self, file_list):
        """ประมวลผลไฟล์หลายไฟล์"""
        results = []
        
        for file_path in file_list:
            result = self.process_file(file_path)
            if result:
                results.append(result)
        
        # บันทึกผลลัพธ์
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"report_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_files': len(results),
                'results': results
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 บันทึกรายงาน: {output_file.name}")
        return results
    
    def generate_summary(self):
        """สร้างสรุปข้อมูล"""
        try:
            input_files = list(self.input_dir.rglob('*'))
            output_files = list(self.output_dir.rglob('*'))
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'input_files': len([f for f in input_files if f.is_file()]),
                'output_files': len([f for f in output_files if f.is_file()]),
                'input_size': sum(f.stat().st_size for f in input_files if f.is_file()),
                'output_size': sum(f.stat().st_size for f in output_files if f.is_file())
            }
            
            logger.info(f"📈 สรุป: {summary['input_files']} ไฟล์อินพุต, {summary['output_files']} ไฟล์เอาต์พุต")
            return summary
        
        except Exception as e:
            logger.error(f"ข้อผิดพลาด: {e}")
            return None


def validate_data(data):
    """ตรวจสอบความถูกต้องของข้อมูล"""
    try:
        if not data:
            logger.warning("⚠️ ข้อมูลว่าง")
            return False
        
        logger.info(f"✓ ตรวจสอบข้อมูลผ่าน")
        return True
    
    except Exception as e:
        logger.error(f"ข้อผิดพลาด: {e}")
        return False


def export_data(data, output_file, format='json'):
    """ส่งออกข้อมูล"""
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        elif format == 'csv' and isinstance(data, list):
            if data:
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        
        logger.info(f"✓ ส่งออกข้อมูล: {output_path.name}")
        return True
    
    except Exception as e:
        logger.error(f"ข้อผิดพลาด: {e}")
        return False
