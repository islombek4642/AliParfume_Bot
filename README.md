# 🌟 AliParfume Bot

AliParfume - bu atir-upa va kosmetika mahsulotlari savdosi uchun mo'ljallangan professional Telegram bot. Bot to'liq modulli arxitektura, ko'p tilli qo'llab-quvvatlash (UZ/RU) va Docker asosidagi infratuzilma bilan qurilgan.

## 🚀 Asosiy Imkoniyatlar

- **Katalog va Savatcha**: Mahsulotlarni kategoriyalar bo'yicha ko'rish va savatchaga qo'shish.
- **Ko'p Adminli Tizim**: Bir nechta administratorni `.env` orqali boshqarish.
- **Reklama (Broadcast)**: Adminlar barcha foydalanuvchilarga rasm, video va matnli reklamalarni tasdiqlash bilan yuborishi mumkin.
- **Avtomatik Lokalizatsiya**: Foydalanuvchi tanlagan tilga (O'zbekcha/Ruscha) moslashuvchi interfeys.
- **O'zbekiston Vaqti**: Loglar va bazadagi barcha vaqt ko'rsatkichlari har doim `Asia/Tashkent` vaqtida.

## 🛠 Texnologiyalar

- **Python 3.11+**
- **Aiogram 3.x** (Telegram Bot Framework)
- **PostgreSQL 15** (Database)
- **SQLAlchemy 2.0** (ORM)
- **Docker & Docker-Compose** (Containerization)

## ⚙️ Sozlash (.env)

Loyiha ildiz papkasida `.env` faylini yarating va quyidagilarni to'ldiring:

```env
BOT_TOKEN=Sizning_Bot_Tokeningiz
ADMIN_ID=admin_id1,admin_id2
CHANNEL_ID=-100...

DB_HOST=db
DB_USER=aliparfume_user
DB_PASS=your_password
DB_NAME=aliparfume_db
DB_PORT=5432
```

## 📦 Lokal Ishga Tushirish

Agar kompyuteringizda **Docker** o'rnatilgan bo'lsa:

```bash
python run.py
```

## 🌐 Serverda Ishga Tushirish (Linux)

Serverda botni avtomatik sozlash va ishga tushirish uchun:

```bash
bash deploy.sh
```

## 📂 Loyiha Tuzilishi

- `data/`: Konfiguratsiya va lokalizatsiya fayllari.
- `database/`: Ver ma'lumotlar bazasi modellari va bazaga ulanish.
- `handlers/`: Bot buyruqlari va mantiqiy bo'limlari (Admin/User).
- `services/`: Biznes logikasi (Business logic).
- `utils/`: Yordamchi yordamchilar (Timezone, Seeding).

---
Loyiha **AliParfume** jamoasi uchun maxsus tayyorlangan.
