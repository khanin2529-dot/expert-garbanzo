#!/bin/bash
# Script เพื่อเรียกใช้ระบบอัตโนมัติ

# ตรวจสอบ Virtual Environment
if [ ! -d "venv" ]; then
    echo "สร้าง Virtual Environment..."
    python3 -m venv venv
fi

# เปิด Virtual Environment
source venv/bin/activate

# ติดตั้ง dependencies ถ้าจำเป็น
if [ ! -f "venv/installed" ]; then
    echo "ติดตั้ง dependencies..."
    pip install -r requirements.txt >> /dev/null 2>&1
    touch venv/installed
fi

# เรียกใช้ระบบ
echo "🚀 เริ่มเรียกใช้ระบบอัตโนมัติ..."
python main.py
