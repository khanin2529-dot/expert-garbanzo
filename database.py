# -*- coding: utf-8 -*-
"""
Database Manager - จัดการเก็บข้อมูลโปรไฟล์และประวัติ
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class DatabaseManager:
    """จัดการฐานข้อมูล JSON"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self.db_dir = self.data_dir / "database"
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
        self.users_db = self.db_dir / "users.json"
        self.profiles_db = self.db_dir / "profiles.json"
        self.audit_db = self.db_dir / "audit_logs.json"
        self.sessions_db = self.db_dir / "sessions.json"
        
        self._init_databases()
    
    def _init_databases(self):
        """สร้างฐานข้อมูลถ้าไม่มี"""
        for db_file in [self.users_db, self.profiles_db, self.audit_db, self.sessions_db]:
            if not db_file.exists():
                with open(db_file, 'w') as f:
                    json.dump([], f)
    
    # ===== Users Database =====
    
    def add_user(self, username, password_hash, role='user'):
        """เพิ่มผู้ใช้ใหม่"""
        try:
            users = self._read_json(self.users_db)
            
            # ตรวจสอบว่ามีแล้ว
            if any(u['username'] == username for u in users):
                logger.warning(f"⚠️ ผู้ใช้มีอยู่แล้ว: {username}")
                return False
            
            new_user = {
                "id": len(users) + 1,
                "username": username,
                "password": password_hash,
                "role": role,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "active": True
            }
            
            users.append(new_user)
            self._write_json(self.users_db, users)
            
            # เพิ่ม profile
            self.add_profile(username)
            
            # บันทึก audit log
            self.add_audit_log(
                action="USER_CREATED",
                username=username,
                details={"role": role}
            )
            
            logger.info(f"✅ เพิ่มผู้ใช้: {username}")
            return True
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        """ดึงข้อมูลผู้ใช้"""
        users = self._read_json(self.users_db)
        for user in users:
            if user['username'] == username:
                return user
        return None
    
    def get_all_users(self) -> List[Dict]:
        """ดึงข้อมูลผู้ใช้ทั้งหมด"""
        return self._read_json(self.users_db)
    
    def update_user(self, username: str, **kwargs):
        """อัปเดตข้อมูลผู้ใช้"""
        try:
            users = self._read_json(self.users_db)
            
            for user in users:
                if user['username'] == username:
                    user.update(kwargs)
                    user['updated_at'] = datetime.now().isoformat()
                    break
            
            self._write_json(self.users_db, users)
            
            self.add_audit_log(
                action="USER_UPDATED",
                username=username,
                details=kwargs
            )
            
            logger.info(f"✅ อัปเดตผู้ใช้: {username}")
            return True
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    # ===== Profiles Database =====
    
    def add_profile(self, username: str, full_name: str = "", email: str = ""):
        """เพิ่มโปรไฟล์ผู้ใช้"""
        try:
            profiles = self._read_json(self.profiles_db)
            
            new_profile = {
                "username": username,
                "full_name": full_name,
                "email": email,
                "phone": "",
                "department": "",
                "avatar": "",
                "bio": "",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            profiles.append(new_profile)
            self._write_json(self.profiles_db, profiles)
            
            logger.info(f"✅ สร้างโปรไฟล์: {username}")
            return True
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    def get_profile(self, username: str) -> Optional[Dict]:
        """ดึงโปรไฟล์ผู้ใช้"""
        profiles = self._read_json(self.profiles_db)
        for profile in profiles:
            if profile['username'] == username:
                return profile
        return None
    
    def update_profile(self, username: str, **kwargs):
        """อัปเดตโปรไฟล์"""
        try:
            profiles = self._read_json(self.profiles_db)
            
            found = False
            for profile in profiles:
                if profile['username'] == username:
                    profile.update(kwargs)
                    profile['updated_at'] = datetime.now().isoformat()
                    found = True
                    break
            
            if found:
                self._write_json(self.profiles_db, profiles)
                
                self.add_audit_log(
                    action="PROFILE_UPDATED",
                    username=username,
                    details=kwargs
                )
                
                logger.info(f"✅ อัปเดตโปรไฟล์: {username}")
                return True
            else:
                logger.warning(f"⚠️ ไม่พบโปรไฟล์: {username}")
                return False
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    # ===== Audit Logs =====
    
    def add_audit_log(self, action: str, username: str = "", details: Dict = None):
        """บันทึก audit log"""
        try:
            logs = self._read_json(self.audit_db)
            
            audit_entry = {
                "id": len(logs) + 1,
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "username": username,
                "details": details or {},
                "ip_address": "",
                "user_agent": ""
            }
            
            logs.append(audit_entry)
            self._write_json(self.audit_db, logs)
            
            return True
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    def get_audit_logs(self, username: str = None, limit: int = 100) -> List[Dict]:
        """ดึง audit logs"""
        logs = self._read_json(self.audit_db)
        
        if username:
            logs = [log for log in logs if log['username'] == username]
        
        return logs[-limit:]
    
    # ===== Sessions Management =====
    
    def add_session(self, username: str, token: str, expires_at: str):
        """บันทึก session"""
        try:
            sessions = self._read_json(self.sessions_db)
            
            session = {
                "id": len(sessions) + 1,
                "username": username,
                "token": token,
                "created_at": datetime.now().isoformat(),
                "expires_at": expires_at,
                "ip_address": "",
                "user_agent": "",
                "active": True
            }
            
            sessions.append(session)
            self._write_json(self.sessions_db, sessions)
            
            logger.info(f"✅ สร้าง session: {username}")
            return True
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    def get_user_sessions(self, username: str) -> List[Dict]:
        """ดึง sessions ของผู้ใช้"""
        sessions = self._read_json(self.sessions_db)
        return [s for s in sessions if s['username'] == username and s['active']]
    
    # ===== Export Functions =====
    
    def export_all_data(self, format='json'):
        """ส่งออกข้อมูลทั้งหมด"""
        try:
            export_file = self.data_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
            
            all_data = {
                "export_time": datetime.now().isoformat(),
                "users": self._read_json(self.users_db),
                "profiles": self._read_json(self.profiles_db),
                "audit_logs": self._read_json(self.audit_db),
                "sessions": self._read_json(self.sessions_db)
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ ส่งออกข้อมูล: {export_file}")
            return str(export_file)
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return None
    
    def export_user_data(self, username: str):
        """ส่งออกข้อมูลเฉพาะผู้ใช้"""
        try:
            export_file = self.data_dir / f"user_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            user_data = {
                "export_time": datetime.now().isoformat(),
                "user": self.get_user(username),
                "profile": self.get_profile(username),
                "audit_logs": self.get_audit_logs(username),
                "sessions": self.get_user_sessions(username)
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ ส่งออกข้อมูลผู้ใช้: {export_file}")
            return str(export_file)
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return None
    
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
    
    def get_statistics(self) -> Dict:
        """ดึงสถิติ"""
        return {
            "total_users": len(self.get_all_users()),
            "total_profiles": len(self._read_json(self.profiles_db)),
            "total_audit_logs": len(self._read_json(self.audit_db)),
            "active_sessions": len([s for s in self._read_json(self.sessions_db) if s['active']])
        }


# สร้าง instance เดียว
db_manager = DatabaseManager()
