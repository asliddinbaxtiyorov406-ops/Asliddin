# MUROJAT BOT

Telegram orqali Qamashi tumani yoshlari murojaatlarini qabul qiluvchi bot.

## Imkoniyatlar

- Foydalanuvchidan ism-familiya, telefon raqam va MFYni oladi
- Kanalga obunani tekshiradi
- Murojaat, taklif, moliyaviy yordam, ish o'rinlari va yoshlar imkoniyatlari bo'yicha so'rov qabul qiladi
- `/help` oynasida lotincha va kirillcha ko'rinishni almashtirish mumkin
- Ma'lumotlarni MongoDB'ga saqlaydi, ulanish bo'lmasa avtomatik SQLite fallback ishlaydi
- Botdagi har bir MFY uchun alohida admin-yetakchi biriktiriladi
- Foydalanuvchi tanlagan MFY bo'yicha murojaat faqat o'sha MFY adminiga yuboriladi
- Har bir admin faqat o'ziga biriktirilgan bitta MFY murojaatlariga javob qaytara oladi
- `ADMIN_ID` glavniy boshliq sifatida barcha MFYlardan kelgan murojaatlarni ko'radi
- Kuzatuvchi odamga ma'lumot boradi, lekin u javob bera olmaydi
- `/admin` orqali qisqa statistika ko'rish mumkin

## O'rnatish

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows uchun:

```powershell
py -m venv .venv
.\.venv\Scripts\activate
py -m pip install -r requirements.txt
```

## Sozlash

`.env.example` fayldan `.env` yarating va qiymatlarni to'ldiring:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=123456789
ADMIN_URL=@glavniy_nazoratchi
REQUIRED_CHANNEL=@your_channel_username
CHANNEL_ID=-1001234567890
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=murojat_bot
REGION_LEADERS_ENV_PATH=region_leaders.env
ALLOW_SHARED_REGION_ADMINS=false
FSM_STORAGE_BACKEND=auto
FSM_MONGO_DB_NAME=murojat_bot_fsm
FSM_MONGO_COLLECTION_NAME=states_and_data
WEBHOOK_PATH=/telegram/webhook
WEBHOOK_SECRET_TOKEN=replace_with_long_random_string
WEBHOOK_SETUP_TOKEN=replace_with_admin_setup_token
WEBHOOK_URL=

# Azlartepa
MFY_ADMIN_AZLARTEPA=111111111 | @azlartepa_admin
# Badaxshon
MFY_ADMIN_BADAXSHON=222222222 | @badaxshon_admin
# Boburtepa
MFY_ADMIN_BOBURTEPA=333333333 | @boburtepa_admin
```

`ADMIN_ID` glavniy boshliq hisoblanadi. U barcha MFYlardan kelgan murojaatlarni ko'radi va /admin orqali umumiy nazorat qiladi.
`ADMIN_URL` esa glavniy kuzatuvchining Telegram manzili uchun.

Har bir MFY uchun `.env` ichida alohida qator bo'ladi. Format:

```text
MFY_ADMIN_<MFY_NOMI>=TELEGRAM_ID | @username
```

Masalan:

```text
MFY_ADMIN_AZLARTEPA=111111111 | @azlartepa_admin
MFY_ADMIN_UZUN=222222222 | @uzun_admin
```

Bu yerda:

- `111111111` bu adminning Telegram ID si va bot uchun asosiy qiymat shu
- `@username` adashmaslik uchun yoziladigan Telegram manzil

Fuqaro `Azlartepa`ni tanlasa, murojaat `MFY_ADMIN_AZLARTEPA` ichidagi Telegram ID egasiga yuboriladi va javobni ham faqat shu yetakchi bera oladi.

Amaliy ishlatishda barcha `MFY_ADMIN_*` qatorlarini to'g'ridan-to'g'ri `.env` ichiga kiritish tavsiya qilinadi.
`region_leaders.env` esa faqat ixtiyoriy zaxira fallback hisoblanadi.

`region_leaders.env` formati:

```text
Azlartepa=111111111 | @azlartepa_admin | https://t.me/azlartepa_admin
Badaxshon=222222222 | @badaxshon_admin | https://t.me/badaxshon_admin
```

Muhim:

- Bot barcha MFYlar uchun admin topishi shart. Eng to'g'ri yo'l: hammasini `.env` ichida saqlash
- Bitta Telegram ID faqat bitta MFYga biriktirilishi kerak
- Biror MFY qoldirilsa yoki bitta admin bir nechta MFYga yozilsa, bot default rejimda ishga tushmaydi
- Kanal bo'yicha obuna tekshiruvi bitta umumiy kanal orqali ishlaydi, har bir MFY uchun alohida kanal kerak emas

Agar vaqtincha bitta adminni bir nechta MFYga biriktirib ishlatishingiz kerak bo'lsa:

- `ALLOW_SHARED_REGION_ADMINS=true` qilib qo'ying

`MONGODB_URI` orqali local MongoDB yoki MongoDB Atlas ulanish manzilini berasiz.

## Ishga tushirish

```bash
python main.py
```

Windows uchun:

```powershell
py main.py
```

## Vercelga Deploy

Endi loyiha Vercel uchun `api/index.py` webhook entrypoint bilan tayyor:

- Telegram webhook endpoint: `/api/telegram/webhook`
- Health endpoint: `/api/healthz`
- Webhook setup endpoint: `/api/setup-webhook` (`X-Setup-Token` header bilan)

Tartib:

1. Loyihani GitHub'ga push qiling.
2. Vercel'da project yarating va repository'ni ulang.
3. Vercel Environment Variables'ga `.env` dagi qiymatlarni kiriting.
4. `MONGODB_URI` ni Atlas yoki doimiy MongoDB manziliga bering (serverless rejimda juda muhim).
5. Deploy tugagach webhookni o'rnating:

```bash
curl -X POST "https://<your-project>.vercel.app/api/setup-webhook" \
  -H "X-Setup-Token: <WEBHOOK_SETUP_TOKEN>"
```

Yoki `WEBHOOK_SETUP_TOKEN` ishlatmasdan ham Telegram API orqali qo'lda o'rnatishingiz mumkin:

```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
  -d "url=https://<your-project>.vercel.app/api/telegram/webhook" \
  -d "secret_token=<WEBHOOK_SECRET_TOKEN>"
```

## Database

Bot odatda MongoDB ichida `murojat_bot` nomli database bilan ishlaydi. Nomni `MONGODB_DB_NAME` orqali o'zgartirishingiz mumkin.

Collectionlar:

- `users` - foydalanuvchilar
- `requests` - murojaatlar
- `counters` - murojaat ID hisoblagichi
- `meta` - xizmat ma'lumotlari

Agar MongoDB ulanmasa, bot avtomatik `murojat_bot.db` SQLite fallback bilan ishga tushadi.

Agar eski `murojat_bot.db` SQLite fayli mavjud bo'lsa va MongoDB bo'sh bo'lsa, bot birinchi ishga tushishda ma'lumotlarni avtomatik ko'chiradi.

## MongoDB ni Ishga Tushirish

Local MongoDB uchun misol:

```powershell
docker run -d --name murojat-mongo -p 27017:27017 mongo:7
```

So'ng `.env` ichida quyidagini ishlatishingiz mumkin:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=murojat_bot
```

## VPSda 24/7 Ishlatish

1. Loyihani serverga yuklang
2. Python virtual environment yarating
3. MongoDB ishlayotganini tekshiring
4. `pip install -r requirements.txt` qiling
5. `.env` faylni to'ldiring
6. `deploy/murojat-bot.service.example` faylini server yo'lingizga moslang
7. `systemd` orqali ishga tushiring

Misol:

```bash
sudo cp deploy/murojat-bot.service.example /etc/systemd/system/murojat-bot.service
sudo systemctl daemon-reload
sudo systemctl enable murojat-bot
sudo systemctl start murojat-bot
sudo systemctl status murojat-bot
```

## Northflank'da 24/7 Tekin Variant

2026-04-18 holatiga ko'ra Northflank rasmiy sahifalarida `Sandbox` planida `Always-on-compute` va `2 free services` ko'rsatilgan. Shu loyiha Northflank uchun `Dockerfile` bilan tayyorlab qo'yildi.

Qisqa tartib:

1. Loyihani GitHub'ga push qiling
2. Northflank'da `Combined service` yarating
3. Build method sifatida `Dockerfile` ni tanlang
4. Public port qo'shmang
5. Runtime variable'larni `.env` asosida kiriting
6. `MONGODB_URI` ni albatta to'ldiring

Batafsil yo'riqnoma:

- [deploy/NORTHFLANK_FREE.md](deploy/NORTHFLANK_FREE.md)

Muhim:

- Northflank karta qo'shishni talab qiladi
- karta paid resurs ishlatilmaguncha yechilmaydi
- free tier 24/7 ishlashi mumkin, lekin provider uni production uchun rasmiy tavsiya qilmaydi
