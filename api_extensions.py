# -*- coding: utf-8 -*-
"""
API Extensions - Profile, Export, และ Audit เพิ่มเติม
"""

from flask import request, jsonify, send_file
from datetime import timedelta, datetime
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def register_profile_routes(app, auth_manager, db_manager, require_auth, require_role):
    """ลงทะเบียน Profile routes"""
    
    @app.route('/profile', methods=['GET'])
    @require_auth
    def get_profile():
        """ดึงโปรไฟล์ของผู้ใช้ปัจจุบัน"""
        try:
            username = request.current_user['username']
            profile = db_manager.get_profile(username)
            
            if not profile:
                return jsonify({"error": "ไม่พบโปรไฟล์"}), 404
            
            return jsonify({
                "success": True,
                "profile": profile
            }), 200
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return jsonify({"error": str(e)}), 500
    
    
    @app.route('/profile', methods=['PUT'])
    @require_auth
    def update_profile():
        """อัปเดตโปรไฟล์"""
        try:
            username = request.current_user['username']
            data = request.get_json()
            
            if db_manager.update_profile(username, **data):
                db_manager.add_audit_log(
                    action="PROFILE_UPDATED",
                    username=username,
                    details=data
                )
                
                profile = db_manager.get_profile(username)
                return jsonify({
                    "success": True,
                    "message": "อัปเดตโปรไฟล์สำเร็จ",
                    "profile": profile
                }), 200
            else:
                return jsonify({"error": "อัปเดตโปรไฟล์ไม่สำเร็จ"}), 400
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return jsonify({"error": str(e)}), 500


def register_export_routes(app, db_manager, require_auth, require_role):
    """ลงทะเบียน Export routes"""
    
    @app.route('/export/data', methods=['GET'])
    @require_auth
    @require_role('admin')
    def export_all_data():
        """ส่งออกข้อมูลทั้งหมด (Admin only)"""
        try:
            export_file = db_manager.export_all_data()
            
            db_manager.add_audit_log(
                action="DATA_EXPORTED",
                username=request.current_user['username'],
                details={"type": "all_data"}
            )
            
            return send_file(export_file, as_attachment=True)
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return jsonify({"error": str(e)}), 500
    
    
    @app.route('/export/user', methods=['GET'])
    @require_auth
    def export_user_data():
        """ส่งออกข้อมูลของผู้ใช้"""
        try:
            username = request.current_user['username']
            export_file = db_manager.export_user_data(username)
            
            db_manager.add_audit_log(
                action="USER_DATA_EXPORTED",
                username=username,
                details={}
            )
            
            return send_file(export_file, as_attachment=True)
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return jsonify({"error": str(e)}), 500


def register_audit_routes(app, db_manager, require_auth, require_role):
    """ลงทะเบียน Audit routes"""
    
    @app.route('/audit-logs', methods=['GET'])
    @require_auth
    @require_role('admin')
    def get_audit_logs():
        """ดึง audit logs (Admin only)"""
        try:
            username = request.args.get('username')
            limit = int(request.args.get('limit', 100))
            
            logs = db_manager.get_audit_logs(username=username, limit=limit)
            
            return jsonify({
                "success": True,
                "count": len(logs),
                "logs": logs
            }), 200
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return jsonify({"error": str(e)}), 500
    
    
    @app.route('/statistics', methods=['GET'])
    @require_auth
    @require_role('admin')
    def get_statistics():
        """ดึงสถิติ (Admin only)"""
        try:
            stats = db_manager.get_statistics()
            
            return jsonify({
                "success": True,
                "statistics": stats
            }), 200
        
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return jsonify({"error": str(e)}), 500


def register_all_routes(app, auth_manager, db_manager, require_auth, require_role):
    """ลงทะเบียน routes ทั้งหมด"""
    register_profile_routes(app, auth_manager, db_manager, require_auth, require_role)
    register_export_routes(app, db_manager, require_auth, require_role)
    register_audit_routes(app, db_manager, require_auth, require_role)
