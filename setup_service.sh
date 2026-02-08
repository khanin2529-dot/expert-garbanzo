#!/bin/bash
# Script เพื่อติดตั้ง Systemd Service

echo "🔧 ติดตั้ง Systemd Service..."

# ตรวจสอบ root
if [ "$EUID" -ne 0 ]; then 
   echo "❌ ต้องระบบสิทธิ์ root"
   echo "รันครั้งนี้: sudo bash setup_service.sh"
   exit 1
fi

# ติดตั้งไปยัง /opt/
INSTALL_PATH="/opt/expert-garbanzo"
echo "📁 ติดตั้งไปยัง: $INSTALL_PATH"

# สร้างโฟลเดอร์
mkdir -p "$INSTALL_PATH"
cp -r . "$INSTALL_PATH"

# ตั้งค่าสิทธิ์
chown -R www-data:www-data "$INSTALL_PATH"
chmod +x "$INSTALL_PATH/start.sh"
chmod +x "$INSTALL_PATH/logs.sh"

# ติดตั้ง Service
echo "📝 ติดตั้ง Service..."
cp "$INSTALL_PATH/automation.service" /etc/systemd/system/
cp "$INSTALL_PATH/api.service" /etc/systemd/system/

# โหลด Service
systemctl daemon-reload

# เปิดใช้งาน Service
systemctl enable automation.service
systemctl enable api.service

echo "✅ ติดตั้ง Service สำเร็จ"
echo ""
echo "📋 คำสั่งต่อไป:"
echo "  เริ่มระบบ:        sudo systemctl start automation.service"
echo "  เริ่ม API:         sudo systemctl start api.service"
echo "  ตรวจสอบสถานะ:     sudo systemctl status automation.service"
echo "  ดูบันทึก:         sudo journalctl -u automation.service -f"
echo ""
echo "🚀 ระบบจะเริ่มอัตโนมัติเมื่อ Reboot"
