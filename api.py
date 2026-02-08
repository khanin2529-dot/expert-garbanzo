# -*- coding: utf-8 -*-
"""
API Server สำหรับรับและจัดการไฟล์อัปโหลด + Authentication
"""

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import logging
import os
from pathlib import Path
from datetime import datetime
import json

# Import Auth
from auth import auth_manager, require_auth, require_role

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ตั้งค่า
UPLOAD_FOLDER = Path(__file__).parent / "data" / "uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'json'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# สร้างโฟลเดอร์หากไม่มี
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """ตรวจสอบนามสกุลไฟล์ที่อนุญาต"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file(filename):
    """ตรวจสอบนามสกุลไฟล์ที่อนุญาต"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def home():
    """หน้าแรก"""
    return jsonify({
        "name": "ผู้เชี่ยวชาญถั่วซิกฟี",
        "version": "2.0.0",
        "status": "ทำงานปกติ",
        "authenticated_endpoints": {
            "POST /login": "เข้าสู่ระบบ",
            "POST /register": "สมัครสมาชิก (Admin only)",
            "POST /upload": "อัปโหลดไฟล์",
            "GET /files": "ดูรายการไฟล์",
            "DELETE /file/<filename>": "ลบไฟล์",
            "GET /health": "ตรวจสอบสถานะ"
        },
        "note": "ต้องเพิ่ม Authorization header: Bearer <token>"
    })


# ===== Authentication Endpoints =====

@app.route('/login', methods=['POST'])
def login():
    """เข้าสู่ระบบ"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "ต้องระบุ username และ password"}), 400
        
        user = auth_manager.authenticate(username, password)
        if not user:
            # บันทึก failed login
            db_manager.add_audit_log(
                action="LOGIN_FAILED",
                username=username,
                details={"reason": "Invalid credentials"}
            )
            return jsonify({"error": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"}), 401
        
        token = auth_manager.create_token(username)
        
        # บันทึก successful login
        db_manager.add_audit_log(
            action="LOGIN_SUCCESS",
            username=username,
            details={"role": user['role']}
        )
        
        # บันทึก session
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        db_manager.add_session(username, token, expires_at)
        
        return jsonify({
            "success": True,
            "token": token,
            "username": username,
            "role": user['role'],
            "message": "เข้าสู่ระบบสำเร็จ"
        }), 200
    
    except Exception as e:
        logger.error(f"❌ ข้อผิดพลาด: {e}")
        return jsonify({"error": str(e)}), 500


from datetime import timedelta


@app.route('/register', methods=['POST'])
@require_auth
@require_role('admin')
def register():
    """สมัครผู้ใช้ใหม่ (Admin only)"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')
        
        if not username or not password:
            return jsonify({"error": "ต้องระบุ username และ password"}), 400
        
        if auth_manager.register_user(username, password, role):
            # บันทึก audit log
            db_manager.add_audit_log(
                action="USER_REGISTERED",
                username=request.current_user['username'],
                details={"new_user": username, "role": role}
            )
            
            return jsonify({
                "success": True,
                "message": f"สมัครผู้ใช้ {username} สำเร็จ",
                "username": username,
                "role": role
            }), 201
        else:
            return jsonify({"error": "สมัครผู้ใช้ไม่สำเร็จ"}), 400
    
    except Exception as e:
        logger.error(f"❌ ข้อผิดพลาด: {e}")
        return jsonify({"error": str(e)}), 500


# ===== Profile Management =====

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


# ===== Data Export =====

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


# ===== Audit Logs =====

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


# ===== Statistics =====

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


# ===== File Upload Endpoints =====

@app.route('/upload', methods=['POST'])
@require_auth
@require_role('admin', 'user')
def upload_file():
    """รับและบันทึกไฟล์อัปโหลด"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "ไม่มีไฟล์ในคำขอ"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "ไม่ได้เลือกไฟล์"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": f"ไม่อนุญาตนามสกุลนี้ อนุญาต: {ALLOWED_EXTENSIONS}"}), 400
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        unique_filename = timestamp + filename
        
        filepath = UPLOAD_FOLDER / unique_filename
        file.save(str(filepath))
        
        logger.info(f"✓ อัปโหลดไฟล์สำเร็จ: {unique_filename} (ผู้ใช้: {request.current_user['username']})")
        
        return jsonify({
            "success": True,
            "message": "อัปโหลดสำเร็จ",
            "filename": unique_filename,
            "size": filepath.stat().st_size,
            "uploaded_by": request.current_user['username'],
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"❌ ข้อผิดพลาดในการอัปโหลด: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/files', methods=['GET'])
@require_auth
@require_role('admin', 'user', 'viewer')
def list_files():
    """แสดงรายการไฟล์ที่อัปโหลด"""
    try:
        files = []
        for file_path in UPLOAD_FOLDER.glob("*"):
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        return jsonify({
            "success": True,
            "count": len(files),
            "files": files
        }), 200
    
    except Exception as e:
        logger.error(f"❌ ข้อผิดพลาด: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/file/<filename>', methods=['DELETE'])
@require_auth
@require_role('admin', 'user')
def delete_file(filename):
    """ลบไฟล์"""
    try:
        filepath = UPLOAD_FOLDER / secure_filename(filename)
        
        if not filepath.exists():
            return jsonify({"error": "ไฟล์ไม่พบ"}), 404
        
        filepath.unlink()
        logger.info(f"✓ ลบไฟล์สำเร็จ: {filename} (ผู้ใช้: {request.current_user['username']})")
        
        return jsonify({
            "success": True,
            "message": f"ลบไฟล์ {filename} สำเร็จ"
        }), 200
    
    except Exception as e:
        logger.error(f"❌ ข้อผิดพลาด: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """ตรวจสอบสถานะ (ไม่ต้อง login)"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "upload_folder_exists": UPLOAD_FOLDER.exists()
    }), 200


@app.errorhandler(413)
def request_entity_too_large(error):
    """จัดการข้อผิดพลาดไฟล์ขนาดใหญ่"""
    return jsonify({"error": f"ไฟล์ใหญ่เกินไป (สูงสุด {MAX_FILE_SIZE/1024/1024:.0f}MB)"}), 413


@app.errorhandler(404)
def not_found(error):
    """จัดการ API ที่ไม่พบ"""
    return jsonify({"error": "ไม่พบ Endpoint นี้"}), 404


if __name__ == '__main__':
    logger.info("🚀 เริ่มเรียกใช้ API Server ด้วย Authentication...")
    app.run(host='0.0.0.0', port=5000, debug=False)


@app.route('/upload', methods=['POST'])
def upload_file_old():
    """เพิ่มไฟล์ (POST) - เก่า"""
    try:
        # ตรวจสอบว่ามีไฟล์ในคำขอหรือไม่
        if 'file' not in request.files:
            return jsonify({"error": "ไม่มีไฟล์ในคำขอ"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "ไม่ได้เลือกไฟล์"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": f"ไม่อนุญาตนามสกุลนี้ อนุญาต: {ALLOWED_EXTENSIONS}"}), 400
        
        # บันทึกไฟล์ด้วยชื่อปลอดภัย
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        unique_filename = timestamp + filename
        
        filepath = UPLOAD_FOLDER / unique_filename
        file.save(str(filepath))
        
        logger.info(f"✓ อัปโหลดไฟล์สำเร็จ: {unique_filename}")
        
        return jsonify({
            "success": True,
            "message": "อัปโหลดสำเร็จ",
            "filename": unique_filename,
            "size": filepath.stat().st_size,
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"❌ ข้อผิดพลาดในการอัปโหลด: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/files', methods=['GET'])
def list_files():
    """แสดงรายการไฟล์ที่อัปโหลด"""
    try:
        files = []
        for file_path in UPLOAD_FOLDER.glob("*"):
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        return jsonify({
            "success": True,
            "count": len(files),
            "files": files
        }), 200
    
    except Exception as e:
        logger.error(f"❌ ข้อผิดพลาดในการดูรายการไฟล์: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/file/<filename>', methods=['DELETE'])
def delete_file(filename):
    """ลบไฟล์"""
    try:
        filepath = UPLOAD_FOLDER / secure_filename(filename)
        
        if not filepath.exists():
            return jsonify({"error": "ไฟล์ไม่พบ"}), 404
        
        filepath.unlink()
        logger.info(f"✓ ลบไฟล์สำเร็จ: {filename}")
        
        return jsonify({
            "success": True,
            "message": f"ลบไฟล์ {filename} สำเร็จ"
        }), 200
    
    except Exception as e:
        logger.error(f"❌ ข้อผิดพลาดในการลบไฟล์: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """ตรวจสอบสถานะ"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "upload_folder_exists": UPLOAD_FOLDER.exists()
    }), 200


@app.errorhandler(413)
def request_entity_too_large(error):
    """จัดการข้อผิดพลาดไฟล์ขนาดใหญ่"""
    return jsonify({"error": f"ไฟล์ใหญ่เกินไป (สูงสุด {MAX_FILE_SIZE/1024/1024:.0f}MB)"}), 413


@app.errorhandler(404)
def not_found(error):
    """จัดการ API ที่ไม่พบ"""
    return jsonify({"error": "ไม่พบ Endpoint นี้"}), 404


if __name__ == '__main__':
    logger.info("🚀 เริ่มเรียกใช้ API Server...")
    app.run(host='0.0.0.0', port=5000, debug=False)


@app.route('/upload', methods=['POST'])
def upload_file_old():
    """เพิ่มไฟล์ (POST) - เก่า"""
    try:
        # ตรวจสอบว่ามีไฟล์ในคำขอ
        if 'file' not in request.files:
            return jsonify({'error': 'ไม่พบไฟล์ในคำขอ'}), 400
        
        file = request.files['file']
        
        # ตรวจสอบชื่อไฟล์
        if file.filename == '':
            return jsonify({'error': 'ไม่ได้เลือกไฟล์'}), 400
        
        # ตรวจสอบนามสกุล
        if not allowed_file(file.filename):
            return jsonify({'error': f'ประเภทไฟล์ไม่ได้รับอนุญาต'}), 400
        
        # บันทึกไฟล์
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        filename = timestamp + filename
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        file_size = os.path.getsize(filepath)
        logger.info(f"✓ อัปโหลดไฟล์: {filename} ({file_size} bytes)")
        
        return jsonify({
            'message': 'อัปโหลดสำเร็จ',
            'filename': filename,
            'size': file_size,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"ข้อผิดพลาด: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/files', methods=['GET'])
def list_files():
    """ดูรายชื่อไฟล์ (GET)"""
    try:
        files = []
        for file in UPLOAD_FOLDER.iterdir():
            if file.is_file():
                files.append({
                    'name': file.name,
                    'size': file.stat().st_size,
                    'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
        
        return jsonify({
            'total': len(files),
            'files': files
        }), 200
    
    except Exception as e:
        logger.error(f"ข้อผิดพลาด: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/files/<filename>', methods=['GET'])
def download_file(filename):
    """ดาวน์โหลดไฟล์ (GET)"""
    try:
        filepath = UPLOAD_FOLDER / secure_filename(filename)
        
        if not filepath.exists():
            return jsonify({'error': 'ไม่พบไฟล์'}), 404
        
        from flask import send_file
        logger.info(f"✓ ดาวน์โหลดไฟล์: {filename}")
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        logger.error(f"ข้อผิดพลาด: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    """ลบไฟล์ (DELETE)"""
    try:
        filepath = UPLOAD_FOLDER / secure_filename(filename)
        
        if not filepath.exists():
            return jsonify({'error': 'ไม่พบไฟล์'}), 404
        
        filepath.unlink()
        logger.info(f"✓ ลบไฟล์: {filename}")
        
        return jsonify({'message': 'ลบไฟล์สำเร็จ'}), 200
    
    except Exception as e:
        logger.error(f"ข้อผิดพลาด: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    """ตรวจสอบสถานะ"""
    try:
        total_size = sum(f.stat().st_size for f in UPLOAD_FOLDER.iterdir() if f.is_file())
        file_count = len(list(UPLOAD_FOLDER.glob('*')))
        
        return jsonify({
            'status': 'ทำงานอยู่',
            'total_files': file_count,
            'total_size': total_size,
            'upload_folder': str(UPLOAD_FOLDER)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('api.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("🚀 เริ่ม API Server ที่ http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)
