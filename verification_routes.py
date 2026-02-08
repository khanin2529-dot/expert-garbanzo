# -*- coding: utf-8 -*-
"""
Verification API Routes - ยืนยันตัวตนและแชร์โปรไฟล์
"""

from flask import request, jsonify
from functools import wraps
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def register_verification_routes(app, verification_manager, db_manager, require_auth):
    """ลงทะเบียน Verification routes"""
    
    @app.route('/verify/send-code', methods=['POST'])
    @require_auth
    def send_verification_code():
        """ส่งรหัสยืนยัน"""
        try:
            username = request.current_user['username']
            
            code = verification_manager.generate_verification_code(username)
            
            db_manager.add_audit_log(
                action="VERIFICATION_CODE_SENT",
                username=username,
                details={"code": code}
            )
            
            return jsonify({
                "success": True,
                "message": f"ส่งรหัสยืนยันไปยัง {username} แล้ว",
                "code": code  # ⚠️ ส่งให้ผู้ใช้ยืนยัน (ในโปรดัคชั่นต้องส่งทาง SMS/Email)
            }), 200
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return jsonify({"error": str(e)}), 500
    
    
    @app.route('/verify/confirm-code', methods=['POST'])
    @require_auth
    def confirm_verification_code():
        """ยืนยันรหัส"""
        try:
            username = request.current_user['username']
            data = request.get_json()
            code = data.get('code')
            
            if not code:
                return jsonify({"error": "ต้องระบุรหัสยืนยัน"}), 400
            
            if verification_manager.verify_code(username, code):
                # อัปเดต verified status ในโปรไฟล์
                db_manager.update_profile(
                    username,
                    verified=True,
                    verified_at=datetime.now().isoformat()
                )
                
                db_manager.add_audit_log(
                    action="PROFILE_VERIFIED",
                    username=username,
                    details={}
                )
                
                return jsonify({
                    "success": True,
                    "message": "ยืนยันตัวตนสำเร็จ ✅",
                    "verified": True
                }), 200
            else:
                return jsonify({"error": "รหัสยืนยันไม่ถูกต้อง"}), 400
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return jsonify({"error": str(e)}), 500
    
    
    @app.route('/verify/status', methods=['GET'])
    @require_auth
    def get_verification_status():
        """ตรวจสอบสถานะการยืนยัน"""
        try:
            username = request.current_user['username']
            profile = db_manager.get_profile(username)
            
            verified = verification_manager.is_verified(username)
            
            return jsonify({
                "success": True,
                "username": username,
                "verified": verified,
                "badge": "✅ Verified" if verified else "⏳ Pending Verification",
                "profile": profile
            }), 200
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return jsonify({"error": str(e)}), 500


def register_profile_share_routes(app, verification_manager, db_manager, require_auth):
    """ลงทะเบียน Profile Share routes"""
    
    @app.route('/profile/share-request', methods=['POST'])
    @require_auth
    def request_profile_share():
        """ขออนุญาติแชร์โปรไฟล์"""
        try:
            username = request.current_user['username']
            data = request.get_json()
            recipient = data.get('recipient')
            
            if not recipient:
                return jsonify({"error": "ต้องระบุ recipient"}), 400
            
            # ตรวจสอบว่ามีการยืนยันหรือไม่
            if not verification_manager.is_verified(username):
                return jsonify({
                    "error": "ต้องยืนยันตัวตนก่อน",
                    "message": "Please verify your identity first"
                }), 403
            
            security_code = verification_manager.request_profile_share(username, recipient)
            
            db_manager.add_audit_log(
                action="PROFILE_SHARE_REQUESTED",
                username=username,
                details={"recipient": recipient, "code": security_code}
            )
            
            return jsonify({
                "success": True,
                "message": f"ขออนุญาติแชร์โปรไฟล์ไปยัง {recipient} สำเร็จ",
                "security_code": security_code
            }), 201
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return jsonify({"error": str(e)}), 500
    
    
    @app.route('/profile/share-approve', methods=['POST'])
    @require_auth
    def approve_profile_share():
        """อนุมัติการแชร์โปรไฟล์"""
        try:
            username = request.current_user['username']
            data = request.get_json()
            security_code = data.get('security_code')
            
            if not security_code:
                return jsonify({"error": "ต้องระบุ security code"}), 400
            
            if verification_manager.approve_profile_share(username, security_code):
                db_manager.add_audit_log(
                    action="PROFILE_SHARE_APPROVED",
                    username=username,
                    details={"code": security_code}
                )
                
                return jsonify({
                    "success": True,
                    "message": "อนุมัติการแชร์โปรไฟล์สำเร็จ ✅"
                }), 200
            else:
                return jsonify({"error": "ไม่สามารถอนุมัติได้"}), 400
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return jsonify({"error": str(e)}), 500
    
    
    @app.route('/profile/share-reject', methods=['POST'])
    @require_auth
    def reject_profile_share():
        """ปฏิเสธการแชร์โปรไฟล์"""
        try:
            username = request.current_user['username']
            data = request.get_json()
            security_code = data.get('security_code')
            
            if not security_code:
                return jsonify({"error": "ต้องระบุ security code"}), 400
            
            if verification_manager.reject_profile_share(username, security_code):
                db_manager.add_audit_log(
                    action="PROFILE_SHARE_REJECTED",
                    username=username,
                    details={"code": security_code}
                )
                
                return jsonify({
                    "success": True,
                    "message": "ปฏิเสธการแชร์โปรไฟล์สำเร็จ"
                }), 200
            else:
                return jsonify({"error": "ไม่สามารถปฏิเสธได้"}), 400
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return jsonify({"error": str(e)}), 500
    
    
    @app.route('/profile/shared-with-me', methods=['GET'])
    @require_auth
    def get_shared_profiles():
        """ดูโปรไฟล์ที่ได้รับอนุญาติแชร์"""
        try:
            username = request.current_user['username']
            
            shared_profiles = verification_manager.get_shared_profiles(username)
            
            return jsonify({
                "success": True,
                "count": len(shared_profiles),
                "shared_profiles": shared_profiles
            }), 200
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return jsonify({"error": str(e)}), 500


def register_all_verification_routes(app, verification_manager, db_manager, require_auth):
    """ลงทะเบียน routes ทั้งหมด"""
    register_verification_routes(app, verification_manager, db_manager, require_auth)
    register_profile_share_routes(app, verification_manager, db_manager, require_auth)


from datetime import datetime
