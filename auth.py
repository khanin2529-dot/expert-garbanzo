# -*- coding: utf-8 -*-
"""
ระบบตรวจสอบสิทธิ์ (Authentication) และสิทธิ์การใช้งาน (Authorization)
"""

import logging
import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)

# ประเภทสิทธิ์
ROLES = {
    'admin': ['read', 'write', 'delete', 'manage_users', 'view_logs'],
    'user': ['read', 'write', 'delete'],
    'viewer': ['read']
}

# เส้นทางไฟล์สำหรับผู้ใช้
USERS_FILE = Path(__file__).parent / "data" / "users.json"
TOKENS_FILE = Path(__file__).parent / "data" / "tokens.json"


class AuthManager:
    """จัดการการตรวจสอบสิทธิ์"""
    
    def __init__(self):
        self.users_file = USERS_FILE
        self.tokens_file = TOKENS_FILE
        self._ensure_files()
    
    def _ensure_files(self):
        """สร้างไฟล์ถ้าไม่มี"""
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.users_file.exists():
            self._create_default_admin()
        
        if not self.tokens_file.exists():
            with open(self.tokens_file, 'w') as f:
                json.dump([], f)
    
    def _create_default_admin(self):
        """สร้าง Admin เริ่มต้น"""
        admin_user = {
            "username": "admin",
            "password": self._hash_password("admin123"),
            "role": "admin",
            "created": datetime.now().isoformat(),
            "active": True
        }
        
        with open(self.users_file, 'w') as f:
            json.dump([admin_user], f, ensure_ascii=False, indent=2)
        
        logger.info("✅ สร้าง Admin เริ่มต้น: username=admin, password=admin123")
    
    def _hash_password(self, password):
        """แฮช รหัสผ่าน"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password, hashed):
        """ตรวจสอบรหัสผ่าน"""
        return self._hash_password(password) == hashed
    
    def register_user(self, username, password, role='user'):
        """สมัครผู้ใช้ใหม่"""
        try:
            # อ่านผู้ใช้ปัจจุบัน
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            # ตรวจสอบว่ามีแล้ว
            if any(u['username'] == username for u in users):
                logger.warning(f"❌ ผู้ใช้มีอยู่แล้ว: {username}")
                return False
            
            # เพิ่มผู้ใช้ใหม่
            new_user = {
                "username": username,
                "password": self._hash_password(password),
                "role": role if role in ROLES else 'user',
                "created": datetime.now().isoformat(),
                "active": True
            }
            
            users.append(new_user)
            
            with open(self.users_file, 'w') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ สมัครผู้ใช้สำเร็จ: {username} ({new_user['role']})")
            return True
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    def authenticate(self, username, password):
        """ตรวจสอบชื่อผู้ใช้และรหัสผ่าน"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            for user in users:
                if user['username'] == username:
                    if user['active'] and self._verify_password(password, user['password']):
                        logger.info(f"✅ เข้าสู่ระบบสำเร็จ: {username}")
                        return user
                    else:
                        logger.warning(f"❌ รหัสผ่านไม่ถูกต้อง: {username}")
                        return None
            
            logger.warning(f"❌ ไม่พบผู้ใช้: {username}")
            return None
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return None
    
    def create_token(self, username, expires_in=86400):
        """สร้าง Token (24 ชั่วโมง)"""
        try:
            token = secrets.token_urlsafe(32)
            
            with open(self.tokens_file, 'r') as f:
                tokens = json.load(f)
            
            tokens.append({
                "token": token,
                "username": username,
                "created": datetime.now().isoformat(),
                "expires": (datetime.now() + timedelta(seconds=expires_in)).isoformat()
            })
            
            with open(self.tokens_file, 'w') as f:
                json.dump(tokens, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ สร้าง Token: {username}")
            return token
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return None
    
    def verify_token(self, token):
        """ตรวจสอบ Token"""
        try:
            with open(self.tokens_file, 'r') as f:
                tokens = json.load(f)
            
            for t in tokens:
                if t['token'] == token:
                    expires = datetime.fromisoformat(t['expires'])
                    if expires > datetime.now():
                        # ค้นหาผู้ใช้
                        with open(self.users_file, 'r') as f:
                            users = json.load(f)
                        
                        for user in users:
                            if user['username'] == t['username']:
                                return user
                    else:
                        logger.warning(f"❌ Token หมดอายุ")
                        return None
            
            logger.warning(f"❌ Token ไม่ถูกต้อง")
            return None
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return None
    
    def get_user_permissions(self, username):
        """ดึงสิทธิ์ของผู้ใช้"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            for user in users:
                if user['username'] == username:
                    role = user.get('role', 'user')
                    return ROLES.get(role, ROLES['user'])
            
            return []
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return []


# สร้าง instance เดียว
auth_manager = AuthManager()


# Decorators สำหรับ Flask

def require_auth(f):
    """Decorator เพื่อตรวจสอบ Token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({"error": "ไม่มี Authorization token"}), 401
        
        # เอา "Bearer " ออก
        if token.startswith('Bearer '):
            token = token[7:]
        
        user = auth_manager.verify_token(token)
        if not user:
            return jsonify({"error": "Token ไม่ถูกต้อง"}), 401
        
        # เก็บผู้ใช้ใน request
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function


def require_role(*roles):
    """Decorator เพื่อตรวจสอบสิทธิ์"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({"error": "ต้อง Login ก่อน"}), 401
            
            user_role = request.current_user.get('role', 'user')
            if user_role not in roles:
                return jsonify({"error": "ไม่มีสิทธิ์ในการเข้าถึง"}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
