# 🔐 Authentication & Authorization Guide

ระบบ **ผู้เชี่ยวชาญถั่วซิกฟี v2.0** ใช้ Token-based Authentication

## 📋 Account เริ่มต้น

```
Username: admin
Password: admin123
Role: admin
```

⚠️ **⚠️ ต้องเปลี่ยนรหัสผ่านตั้งแต่ครั้งแรก!**

## 🔑 Role & Permissions

### Admin
- ✅ อ่านไฟล์ (read)
- ✅ อัปโหลดไฟล์ (write)
- ✅ ลบไฟล์ (delete)
- ✅ จัดการผู้ใช้ (manage_users)
- ✅ ดูบันทึก (view_logs)

### User
- ✅ อ่านไฟล์ (read)
- ✅ อัปโหลดไฟล์ (write)
- ✅ ลบไฟล์ (delete)

### Viewer
- ✅ อ่านไฟล์ (read)

## 📡 API Endpoints

### 1. Login
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "success": true,
  "token": "abc123xyz...",
  "username": "admin",
  "role": "admin",
  "message": "เข้าสู่ระบบสำเร็จ"
}
```

### 2. Register User (Admin only)
```bash
TOKEN="abc123xyz..."

curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "username": "john",
    "password": "securepass123",
    "role": "user"
  }'
```

### 3. Upload File
```bash
TOKEN="abc123xyz..."

curl -X POST -F "file=@data.csv" \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/upload
```

### 4. List Files
```bash
TOKEN="abc123xyz..."

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/files | json_pp
```

### 5. Delete File
```bash
TOKEN="abc123xyz..."

curl -X DELETE \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/file/20260207_123456_data.csv
```

## 🔄 Token Management

- **Token Validity:** 24 ชั่วโมง
- **Token Storage:** `data/tokens.json`
- **User Storage:** `data/users.json`

### Token หมดอายุ?
```bash
# Login อีกครั้ง
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 🛡️ Best Practices

1. **ห้ามแชร์ Token** - ถือว่าเป็นรหัสผ่าน
2. **เปลี่ยนรหัสผ่าน** - หลังการเข้าระบบครั้งแรก
3. **ใช้ HTTPS** - ในโปรดัคชั่น
4. **Rotate Token** - ทุก 30 วัน
5. **Logout** - เมื่อเสร็จการใช้งาน

## 📊 User Management Files

### users.json
```json
[
  {
    "username": "admin",
    "password": "sha256_hash",
    "role": "admin",
    "created": "2026-02-07T23:00:00",
    "active": true
  }
]
```

### tokens.json
```json
[
  {
    "token": "abc123xyz...",
    "username": "admin",
    "created": "2026-02-07T23:50:00",
    "expires": "2026-02-08T23:50:00"
  }
]
```

## 🚀 Quick Start

```bash
# 1. เข้าสู่ระบบ
TOKEN=$(curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r '.token')

echo "Token: $TOKEN"

# 2. ดูรายการไฟล์
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/files | jq .

# 3. อัปโหลดไฟล์
curl -X POST -F "file=@test.csv" \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/upload | jq .

# 4. สมัครผู้ใช้ใหม่
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"username": "newuser", "password": "pass123", "role": "user"}' | jq .
```

## ⚡ Error Handling

| Status | Error | Solution |
|--------|-------|----------|
| 400 | Missing username/password | ระบุ username และ password |
| 401 | Invalid credentials | ตรวจสอบ username/password |
| 401 | No Authorization token | เพิ่ม Authorization header |
| 403 | Unauthorized role | ต้อง admin role |
| 404 | File not found | ตรวจสอบชื่อไฟล์ |

---

**ระบบตรวจสอบสิทธิ์พร้อมใช้งาน!** 🔐
