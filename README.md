https://github.com/pancakeswap/infinity-core/commit/2eb67b3e17c681c5a1ee7a31dbd7128c30cd6968# ผู้เชี่ยวชาญถั่วซิกฟี 🤖

โครงการ expert-garbanzo เป็นระบบอัตโนมัติแบบครบวงจร (Complete Automation System) ที่ออกแบบมาเพื่อจัดการ ประมวลผล และทำงานต่างๆ ได้อย่างมีประสิทธิภาพและเชื่อถือได้

## ✨ คุณสมบัติ

- ✅ **Scheduler** - ระบบทำงานอัตโนมัติตามเวลา
- ✅ **API Server** - อัปโหลดและจัดการไฟล์ผ่าน HTTP
- ✅ **File Watcher** - ตรวจสอบการเปลี่ยนแปลงไฟล์อัตโนมัติ
- ✅ **Data Processor** - ประมวลผลและวิเคราะห์ข้อมูล (CSV, JSON, Text)
- ✅ **Backup** - สำรองข้อมูลอัตโนมัติ
- ✅ **Health Check** - ตรวจสอบสุขภาพระบบ
- ✅ **Logging** - บันทึกกิจกรรมทั้งหมด
- ✅ **Cleanup** - ล้างไฟล์เก่าและชั่วคราวอัตโนมัติ

## 🏗️ สถาปัตยกรรมระบบ

```
┌─────────────────────────────────────────────┐
│         Automation System v2.0              │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Scheduler │  │File      │  │Data      │ │
│  │          │  │Watcher   │  │Processor │ │
│  └──────────┘  └──────────┘  └──────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │        API Server (Flask)             │ │
│  │  ├─ POST /upload                      │ │
│  │  ├─ GET /files                        │ │
│  │  ├─ GET /files/<filename>             │ │
│  │  ├─ DELETE /files/<filename>          │ │
│  │  └─ GET /status                       │ │
│  └───────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

## 📋 ตั้งค่าครั้งแรก

### 1. ติดตั้ง Python (เวอร์ชัน 3.8 ขึ้นไป)

### 2. สร้าง Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 4. ตั้งค่าไฟล์สภาพแวดล้อม
```bash
cp .env.example .env
# แก้ไข .env ตามความต้องการของคุณ
```

## 🚀 การใช้งาน

### วิธีที่ 1: ใช้ Shell Script
```bash
./start.sh
```

### วิธีที่ 2: ใช้ Python โดยตรง
```bash
python main.py
```

### วิธีที่ 3: ใช้แยกส่วน

**Scheduler + Data Processing:**
```bash
python main.py
```

**API Server (แยก):**
```bash
python api.py
```

## 📁 โครงสร้างโครงการ

```
expert-garbanzo/
├── main.py              # โปรแกรมหลัก (Scheduler + Watcher + Processor)
├── api.py               # API Server (Flask)
├── file_watcher.py      # File Watcher
├── data_processor.py    # Data Processor
├── config.py            # ตั้งค่าระบบ
├── utils.py             # ฟังก์ชันช่วยเหลือ
├── requirements.txt     # Dependencies
├── .env.example         # ตัวอย่างไฟล์สภาพแวดล้อม
├── .gitignore          # ไฟล์ที่ไม่ต้องการ upload
├── logs/               # บันทึกระบบ
├── data/
│   ├── uploads/        # ไฟล์ที่เพิ่งอัปโหลด
│   └── results/        # ผลลัพธ์ประมวลผล
└── backups/            # สำรองข้อมูล
```

## ⏰ ตารางงาน

ระบบจะทำงานอัตโนมัติตามเวลาต่อไปนี้:

- **09:00** - สรุปรายงานประจำวัน
- **12:00** - สำรองข้อมูล
- **15:00** - ตรวจสอบระบบ
- **18:00** - ล้างไฟล์ชั่วคราว
- **รายชั่วโมง** - ตรวจสอบสุขภาพระบบ + ประมวลผลไฟล์

## 🌐 API Documentation

### 1. Upload File
```bash
curl -X POST -F "file=@file.csv" http://localhost:5000/upload
```

### 2. List Files
```bash
curl http://localhost:5000/files
```

### 3. Download File
```bash
curl http://localhost:5000/files/filename.csv -o filename.csv
```

### 4. Delete File
```bash
curl -X DELETE http://localhost:5000/files/filename.csv
```

### 5. Check Status
```bash
curl http://localhost:5000/status
```

## 📊 การดูบันทึก

```bash
# ดูบันทึกระบบ (Scheduler)
tail -f logs/automation.log

# ใช้ shell script เพื่อดู
./logs.sh

# ค้นหาข้อความในบันทึก
grep "ข้อความค้นหา" logs/automation.log
```

## 🎯 ตัวอย่างการใช้งานแบบสมบูรณ์

### Terminal 1: เรียกใช้ Scheduler หลัก
```bash
./start.sh
# หรือ
python main.py
```

### Terminal 2: เปิด File Watcher
```bash
source venv/bin/activate
python file_watcher.py
```

### Terminal 3: เปิด Data Processor
```bash
source venv/bin/activate
python data_processor.py
```

### Terminal 4: เปิด API Server
```bash
source venv/bin/activate
python api.py
# API available at: http://localhost:5000
```

### Terminal 5: ดูบันทึก
```bash
./logs.sh
# หรือ
tail -f logs/automation.log
```

## 🔧 การแก้ไขปัญหา

**ปัญหา**: ImportError เมื่อโหลดโมดูล
```bash
pip install -r requirements.txt
```

**ปัญหา**: บันทึกไม่ปรากฏ
- ตรวจสอบว่าโฟลเดอร์ `logs/` มีอยู่
- ตรวจสอบสิทธิ์การเขียนไฟล์

**ปัญหา**: API Port 5000 ถูกใช้งานแล้ว
```bash
# ใช้ port อื่น
export FLASK_PORT=5001
python api.py
```

## 📝 บันทึก

- **เวอร์ชัน 2.0.0** - ระบบสมบูรณ์แบบ (API + File Watcher + Data Processor)
- **เวอร์ชัน 1.0.0** - ระบบอัตโนมัติพื้นฐาน
- **วันที่**: กุมภาพันธ์ 2026

---

**ทำให้เป็นอัตโนมัติ | Automate Everything** 🎯

*ระบบนี้ถูกออกแบบเพื่อจัดการ ประมวลผล และทำงานต่างๆ ได้หมดอย่างอัตโนมัติโดยไม่ต้องเขียนโค้ด*

# ค้นหาข้อความในบันทึก
grep "ข้อความค้นหา" logs/automation.log

# ใช้ shell script
./logs.sh
```

## ⚙️ การตั้งค่าขั้นสูง

แก้ไขไฟล์ `.env` เพื่อปรับเปลี่ยน:

```env
# ข้อมูลพื้นฐาน
APP_NAME=ผู้เชี่ยวชาญถั่วซิกฟี
ENVIRONMENT=development
LOG_LEVEL=INFO

# ตั้งค่างาน
SCHEDULE_REPORT_TIME=09:00
SCHEDULE_BACKUP_TIME=12:00
SCHEDULE_CHECK_TIME=15:00
SCHEDULE_CLEANUP_TIME=18:00

# การแจ้งเตือน
NOTIFY_ON_ERROR=true
NOTIFY_EMAIL=your-email@example.com
```

## 📝 ตัวอย่างการใช้งาน

### ตัวอย่าง 1: อัปโหลดไฟล์และประมวลผล

```bash
# 1. เริ่มระบบ
python main.py

# 2. ในหน้าต่างอื่น อัปโหลดไฟล์
curl -X POST -F "file=@data.csv" http://localhost:5000/upload

# 3. ระบบจะตรวจสอบและประมวลผลโดยอัตโนมัติ
# ดูผลลัพธ์ใน data/results/ และ logs/automation.log
```

### ตัวอย่าง 2: ดูรายชื่อไฟล์ที่อัปโหลด

```bash
curl http://localhost:5000/files | python -m json.tool
```

### ตัวอย่าง 3: ล้างไฟล์เก่า

```bash
python -c "from utils import cleanup_old_files; cleanup_old_files('data/uploads', days=7)"
```

## 🔧 การแก้ไขปัญหา

**ปัญหา**: ImportError เมื่อโหลดโมดูล
```bash
pip install -r requirements.txt
```

**ปัญหา**: Port 5000 ถูกใช้งาน
```bash
# เปลี่ยน port ใน api.py หรือ config
python -m flask run --port 5001
```

**ปัญหา**: บันทึกไม่ปรากฏ
- ตรวจสอบว่าโฟลเดอร์ `logs/` มีอยู่
- ตรวจสอบสิทธิ์การเขียนไฟล์
- ลองใช้ `./logs.sh` เพื่อดูบันทึก

**ปัญหา**: ไฟล์ไม่ได้ถูกประมวลผล
- ตรวจสอบประเภทไฟล์ (รองรับ: CSV, JSON, TXT, LOG)
- ดูเนื้อหาใน `data/results/` สำหรับรายงาน

## 🚀 บรรจุขึ้น Production

### ใช้ Systemd Service
```bash
# สร้างไฟล์ service
sudo nano /etc/systemd/system/automation.service

[Unit]
Description=Expert Garbanzo Automation System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/expert-garbanzo
ExecStart=/path/to/expert-garbanzo/venv/bin/python main.py

[Install]
WantedBy=multi-user.target

# เปิดใช้งาน
sudo systemctl enable automation
sudo systemctl start automation
```

### ใช้ Docker
```bash
# สร้าง Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]

# Build & Run
docker build -t automation .
docker run -d -p 5000:5000 automation
```

## 📊 Performance Monitoring

ระบบอัตโนมัติจะบันทึก:
- **CPU Usage** - การใช้งาน CPU
- **Memory Usage** - การใช้หน่วยความจำ
- **Disk Usage** - พื้นที่ดิสก์
- **File Count** - จำนวนไฟล์
- **Processing Time** - เวลาประมวลผล

ดูรายงานโดยละเอียดใน `data/results/report_*.json`

## 📝 บันทึก

- **เวอร์ชัน 2.0.0** - ระบบสมบูรณ์ (API + Watcher + Processor)
- **เวอร์ชัน 1.0.0** - ระบบอัตโนมัติพื้นฐาน
- **วันที่**: กุมภาพันธ์ 2026

## 📧 การติดต่อ

สำหรับคำถามหรือปัญหา กรุณาติดต่อผู้ดูแลระบบ

## 📄 License

MIT License - สามารถใช้งานได้อย่างเสรี

## 🚀 ตัวอย่างการใช้งานแบบสม่ำเสมอ

```bash
# Terminal 1: เก็บเฝ้าระบบหลัก
./start.sh

# Terminal 2: รับและตรวจสอบไฟล์
python file_watcher.py

# Terminal 3: ประมวลผลข้อมูล
python data_processor.py

# Terminal 4: เปิด API Server
python api.py

# Terminal 5: ดูบันทึก
./logs.sh
```

---

**ทำให้เป็นอัตโนมัติ | Automate Everything** 🎯

*ระบบนี้ถูกออกแบบให้ทำงานได้หมดอย่างอัตโนมัติโดยไม่ต้องเขียนโค้ด*

**ยินดีต้อนรับสู่ระบบอัตโนมัติสมบูรณ์ของคุณ!** ✨
