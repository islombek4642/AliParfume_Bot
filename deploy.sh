#!/bin/bash

# Ranglar
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 AliParfume botini yangilash va ishga tushirish...${NC}"

# 1. .env faylini tekshirish
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 .env fayli topilmadi. .env.example dan nusxa olinmoqda...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠️  DIQQAT! .env faylini tahrirlang va BOT_TOKEN va boshqa ma'lumotlarni kiriting.${NC}"
    echo -e "Keyin qaytadan '${YELLOW}bash deploy.sh${NC}' ni ishga tushiring."
    exit 1
fi

# 2. Docker mavjudligini tekshirish
if ! [ -x "$(command -v docker-compose)" ]; then
  echo -e "${RED}❌ Xato: docker-compose o'rnatilmagan.${NC}" >&2
  exit 1
fi

# 3. Konteynerlarni yangilash
echo -e "${GREEN}🛑 Eski konteynerlarni to'xtatish...${NC}"
docker-compose down

echo -e "${GREEN}🏗️  Yangi obrazlarni qurish va ishga tushirish...${NC}"
docker-compose up --build -d

# 4. Ma'lumotlar bazasini sozlash (Seeding)
echo -e "${GREEN}⏳ Ma'lumotlar bazasi tayyor bo'lishini kutish (7 soniya)...${NC}"
sleep 7

echo -e "${GREEN}📦 Kategoriyalarni tekshirish va ma'lumotlarni kiritish...${NC}"
docker-compose exec bot python -m utils.init_data

echo -e "\n${GREEN}✅ Bot muvaffaqiyatli ishga tushirildi!${NC}"
echo -e "📝 Loglarni kuzatish: ${YELLOW}docker-compose logs -f bot${NC}"
echo -e "🛑 To'xtatish uchun: ${YELLOW}docker-compose down${NC}"
