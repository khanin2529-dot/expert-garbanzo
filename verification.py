# -*- coding: utf-8 -*-
"""
Profile Verification System - ยืนยันตัวตนและส่งโปรไฟล์
"""

import logging
import secrets
import string
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict
import json

logger = logging.getLogger(__name__)


class VerificationManager:
    """จัดการการยืนยันตัวตนและโปรไฟล์"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data" / "database"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.verifications_db = self.data_dir / "verifications.json"
        self.shared_profiles_db = self.data_dir / "shared_profiles.json"
        
        self._init_databases()
    
    def _init_databases(self):
        """สร้างฐานข้อมูลถ้าไม่มี"""
        for db_file in [self.verifications_db, self.shared_profiles_db]:
            if not db_file.exists():
                with open(db_file, 'w') as f:
                    json.dump([], f)
    
    # ===== Verification Endpoints =====
    
    def generate_verification_code(self, username: str) -> str:
        """สร้างรหัสยืนยัน (6 หลัก)"""
        try:
            code = ''.join(secrets.choice(string.digits) for _ in range(6))
            
            verifications = self._read_json(self.verifications_db)
            
            verification = {
                "id": len(verifications) + 1,
                "username": username,
                "code": code,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(minutes=15)).isoformat(),
                "verified": False,
                "attempts": 0
            }
            
            verifications.append(verification)
            self._write_json(self.verifications_db, verifications)
            
            logger.info(f"✅ สร้างรหัสยืนยัน: {username}")
            return code
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return None
    
    def verify_code(self, username: str, code: str) -> bool:
        """ตรวจสอบรหัสยืนยัน"""
        try:
            verifications = self._read_json(self.verifications_db)
            
            for v in verifications:
                if v['username'] == username and not v['verified']:
                    # ตรวจสอบการหมดอายุ
                    expires = datetime.fromisoformat(v['expires_at'])
                    if expires < datetime.now():
                        logger.warning(f"⚠️ รหัสหมดอายุ: {username}")
                        return False
                    
                    # ตรวจสอบจำนวนครั้งที่พยายาม
                    if v['attempts'] >= 3:
                        logger.warning(f"❌ พยายามเกินจำนวน: {username}")
                        return False
                    
                    if v['code'] == code:
                        v['verified'] = True
                        v['verified_at'] = datetime.now().isoformat()
                        self._write_json(self.verifications_db, verifications)
                        
                        logger.info(f"✅ ยืนยันสำเร็จ: {username}")
                        return True
                    else:
                        v['attempts'] += 1
                        self._write_json(self.verifications_db, verifications)
                        logger.warning(f"❌ รหัสไม่ถูกต้อง: {username}")
                        return False
            
            logger.warning(f"❌ ไม่พบการยืนยัน: {username}")
            return False
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    def is_verified(self, username: str) -> bool:
        """ตรวจสอบว่ายืนยันแล้วหรือไม่"""
        try:
            verifications = self._read_json(self.verifications_db)
            
            for v in verifications:
                if v['username'] == username and v['verified']:
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    # ===== Profile Sharing =====
    
    def request_profile_share(self, username: str, recipient: str) -> str:
        """ขออนุญาตแชร์โปรไฟล์"""
        try:
            share_request = {
                "id": secrets.token_urlsafe(16),
                "username": username,
                "recipient": recipient,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
                "status": "pending",  # pending, approved, rejected
                "security_code": self._generate_security_code()
            }
            
            shared = self._read_json(self.shared_profiles_db)
            shared.append(share_request)
            self._write_json(self.shared_profiles_db, shared)
            
            logger.info(f"📤 ขออนุญาตแชร์โปรไฟล์: {username} -> {recipient}")
            return share_request['security_code']
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return None
    
    def approve_profile_share(self, username: str, security_code: str) -> bool:
        """อนุมัติการแชร์โปรไฟล์"""
        try:
            shared = self._read_json(self.shared_profiles_db)
            
            for share in shared:
                if share['username'] == username and share['security_code'] == security_code:
                    share['status'] = 'approved'
                    share['approved_at'] = datetime.now().isoformat()
                    self._write_json(self.shared_profiles_db, shared)
                    
                    logger.info(f"✅ อนุมัติแชร์โปรไฟล์: {username}")
                    return True
            
            logger.warning(f"❌ ไม่พบขออนุญาต")
            return False
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    def reject_profile_share(self, username: str, security_code: str) -> bool:
        """ปฏิเสธการแชร์โปรไฟล์"""
        try:
            shared = self._read_json(self.shared_profiles_db)
            
            for share in shared:
                if share['username'] == username and share['security_code'] == security_code:
                    share['status'] = 'rejected'
                    share['rejected_at'] = datetime.now().isoformat()
                    self._write_json(self.shared_profiles_db, shared)
                    
                    logger.info(f"❌ ปฏิเสธแชร์โปรไฟล์: {username}")
                    return True
            
            logger.warning(f"❌ ไม่พบขออนุญาต")
            return False
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    def get_shared_profiles(self, recipient: str) -> list:
        """ดึงโปรไฟล์ที่ได้รับอนุญาต"""
        try:
            shared = self._read_json(self.shared_profiles_db)
            
            approved = [
                s for s in shared 
                if s['recipient'] == recipient and s['status'] == 'approved'
            ]
            
            return approved
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return []
    
    def _generate_security_code(self) -> str:
        """สร้างรหัสความปลอดภัย (8 หลัก)"""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    
    # ===== Helper Functions =====
    
    def _read_json(self, filepath: Path):
        """อ่านไฟล์ JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _write_json(self, filepath: Path, data):
        """เขียนไฟล์ JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# สร้าง instance เดียว
verification_manager = VerificationManager()
