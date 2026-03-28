import os
import subprocess
import time
import sys

def run_command(command):
    print(f"Bajarilmoqda: {' '.join(command)}")
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        print(f"Xatolik yuz berdi: {e}")
        return False
    return True

def main():
    print("🚀 AliParfume loyihasini Docker orqali ishga tushirish (Lokal)...")

    # 1. .env faylini tekshirish
    if not os.path.exists(".env"):
        print("📝 .env fayli topilmadi. .env.example dan nusxa olinmoqda...")
        with open(".env.example", "r") as f_src, open(".env", "w") as f_dst:
            f_dst.write(f_src.read())
        print("⚠️  DIQQAT! .env faylini tahrirlang va ma'lumotlarni kiriting.")
        return

    # 2. Docker Compose orqali barchasini ko'tarish
    if not run_command(["docker-compose", "up", "--build", "-d"]):
        print("❌ Docker-compose ishlamadi. Docker o'rnatilganligini tekshiring.")
        return

    print("⏳ Konteynerlar tayyor bo'lishini kutilmoqda (7 soniya)...")
    time.sleep(7)

    # 3. Ma'lumotlar bazasini initsializatsiya qilish (Seeding)
    print("📦 Kategoriyalarni bazaga qo'shish...")
    run_command(["docker-compose", "exec", "bot", "python", "-m", "utils.init_data"])

    print("\n✅ Hammasi tayyor! Bot hozir ishlayapti.")
    print("📝 Loglarni ko'rish uchun: docker-compose logs -f bot")
    
if __name__ == "__main__":
    main()
