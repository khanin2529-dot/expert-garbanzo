# 💾 Database & Data Export Guide

ระบบ **ผู้เชี่ยวชาญถั่วซิกฟี v2.0** มีระบบเก็บข้อมูลอัตโนมัติและการส่งออกข้อมูล

## 📊 ประเภทข้อมูลที่เก็บ

### 1. Users Database (`data/database/users.json`)
- Username, Password Hash
- Role (Admin/User/Viewer)
- Active Status
- Created/Updated Timestamps

### 2. Profiles Database (`data/database/profiles.json`)
- Full Name, Email, Phone
- Department, Avatar, Bio
- Created/Updated Timestamps

### 3. Audit Logs (`data/database/audit_logs.json`)
- บันทึกการเข้าสู่ระบบ
- บันทึกการสมัครผู้ใช้
- บันทึกการอัปโหลดไฟล์
- บันทึกการลบไฟล์
- บันทึกการอัปเดตโปรไฟล์
- IP Address, User Agent

### 4. Sessions Database (`data/database/sessions.json`)
- ข้อมูล Token
- วันหมดอายุ
- IP Address

## 🔐 API Endpoints

### Profile Management

#### ดึงโปรไฟล์
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5000/profile
```

**Response:**
```json
{
  "success": true,
  "profile": {
    "username": "john",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "08x-xxx-xxxx",
    "department": "IT",
    "avatar": "url",
    "bio": "Developer",
    "created_at": "2026-02-08T00:00:00",
    "updated_at": "2026-02-08T00:00:00"
  }
}
```

#### อัปเดตโปรไฟล์
```bash
curl -X PUT -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "newemail@example.com",
    "phone": "08x-xxx-xxxx",
    "department": "Engineering",
    "bio": "Senior Developer"
  }' \
  http://localhost:5000/profile
```

### Data Export

#### ส่งออกข้อมูลผู้ใช้ (โหลด JSON)
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5000/export/user \
  -o user_export.json
```

**ไฟล์ที่ส่งออก:**
```json
{
  "export_time": "2026-02-08T00:00:00",
  "user": { ... },
  "profile": { ... },
  "audit_logs": [ ... ],
  "sessions": [ ... ]
}
```

#### ส่งออกข้อมูลทั้งหมด (Admin only)
```bash
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:5000/export/data \
  -o full_export.json
```

### Audit Logs

#### ดึง Audit Logs (Admin only)
```bash
# ทั้งหมด
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:5000/audit-logs

# เฉพาะผู้ใช้ + ข้อมูล 50 รายการ
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:5000/audit-logs?username=john&limit=50
```

#### ดึงสถิติ (Admin only)
```bash
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:5000/statistics
```

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_users": 10,
    "total_profiles": 10,
    "total_audit_logs": 250,
    "active_sessions": 5
  }
}
```

## 🛠️ Quick Start

### 1. Login & ดึง Token
```bash
TOKEN=$(curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r '.token')

echo "Token: $TOKEN"
```

### 2. ดูโปรไฟล์
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/profile | jq
```

### 3. อัปเดตโปรไฟล์
```bash
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Administrator",
    "email": "admin@example.com",
    "department": "Management"
  }' \
  http://localhost:5000/profile | jq
```

### 4. ส่งออกข้อมูล
```bash
# ข้อมูลผู้ใช้
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/export/user \
  -o mydata_$(date +%Y%m%d_%H%M%S).json

# ข้อมูลทั้งหมด (ต้อง Admin)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/export/data \
  -o fulldata_$(date +%Y%m%d_%H%M%S).json
```

### 5. ดู Audit Logs
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/audit-logs | jq
```

### 6. ดูสถิติ
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/statistics | jq
```

## 📁 File Structure

```
data/
├── database/
│   ├── users.json          # ข้อมูลผู้ใช้
│   ├── profiles.json       # โปรไฟล์ผู้ใช้
│   ├── audit_logs.json     # บันทึกกิจกรรม
│   └── sessions.json       # ข้อมูล Sessions
├── uploads/                # ไฟล์อัปโหลด
├── processed/              # ไฟล์ที่ประมวลผล
└── export_*.json          # ไฟล์ export (Auto-generated)
```

## 🔄 Automatic Data Management

ระบบจะ **เก็บข้อมูลอัตโนมัติ** เมื่อ:

1. ✅ ผู้ใช้เข้าสู่ระบบ → บันทึก login log
2. ✅ สมัครผู้ใช้ใหม่ → สร้าง profile + audit log
3. ✅ อัปเดตโปรไฟล์ → บันทึก audit log
4. ✅ อัปโหลดไฟล์ → บันทึก audit log
5. ✅ ส่งออกข้อมูล → บันทึก export log

## 📊 Export Automation

สร้างสคริปต์สำหรับส่งออกข้อมูลอัตโนมัติ:

```bash
#!/bin/bash
# export_daily.sh

ADMIN_TOKEN="TOKEN_HERE"
EXPORT_DIR="/backups/exports"

mkdir -p "$EXPORT_DIR"

# ส่งออกทั้งหมด
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:5000/export/data \
  -o "$EXPORT_DIR/full_$(date +%Y%m%d).json"

echo "✅ ส่งออกข้อมูล $(date +%Y-%m-%d\ %H:%M:%S)"
```

เพิ่มเข้า crontab:
```bash
0 2 * * * bash /path/to/export_daily.sh  # ทุกวันเวลา 2:00 AM
```

## ⚠️ Data Protection

1. **Backup Regularly** - ส่งออกข้อมูลทุกวัน
2. **Secure Export** - ใช้ HTTPS ในโปรดัคชั่น
3. **Access Control** - Admin role สำหรับส่งออกทั้งหมด
4. **Encrypt Data** - พิจารณาการเข้ารหัส JSON
5. **Monitor Logs** - ตรวจสอบ audit logs อย่างสม่ำเสมอ

---

**ระบบเก็บข้อมูลพร้อมใช้งาน!** 💾
