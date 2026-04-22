# Northflank'da 24/7 Ishga Tushirish

Ushbu loyiha Northflank'ning Dockerfile orqali build qilish usuliga tayyorlangan.

## Nega Northflank?

2026-04-18 holatiga ko'ra Northflank rasmiy sahifalarida:

- `Sandbox` rejimida `Always-on-compute - no sleeping :)` bor
- `2 free services` va `1 free database` bor
- GitHub'dan to'g'ridan-to'g'ri deploy qilish mumkin

Muhim:

- Northflank hisob yaratishda karta qo'shishni so'raydi
- karta paid resurs ishlatilmaguncha yechilmaydi
- free tier ishlab tursa ham, Northflank uni production uchun rasmiy tavsiya qilmaydi

## 1. Kodni GitHub'ga joylang

Loyihani GitHub repository'ga push qiling.

## 2. Northflank hisob oching

1. `Sandbox` planini tanlang
2. billing bo'limida karta qo'shing
3. yangi `Project` yarating

## 3. MongoDB qo'shing

1. Project ichida `Addon` yarating
2. `MongoDB` ni tanlang
3. free database variantini tanlang
4. addon ishga tushgach, `Connection details` sahifasini oching
5. oddiy application ulanish stringini oling

So'ng service uchun `MONGODB_URI` nomli runtime variable yarating va shu qiymatni joylang.

Eslatma:

- bu bot SQLite fallback bilan ham ishga tushadi
- lekin Northflank konteyner fayl tizimi doimiy saqlanmaydi
- shuning uchun 24/7 va ma'lumot yo'qolmasligi uchun `MONGODB_URI` majburiy deb hisoblang

## 4. Service yarating

1. `Create service`
2. `Combined service` ni tanlang
3. GitHub repository va branch'ni tanlang
4. Build method sifatida `Dockerfile` ni tanlang
5. public port qo'shmang
6. kerak bo'lsa healthcheck qo'shmang
7. environment variable'larni kiriting

## 5. Kiritiladigan environment variable'lar

Kamida quyidagilar bo'lishi kerak:

```env
BOT_TOKEN=...
ADMIN_ID=...
ADMIN_URL=@...
REQUIRED_CHANNEL=@...
CHANNEL_ID=-100...
MONGODB_URI=mongodb://... yoki mongodb+srv://...
MONGODB_DB_NAME=murojat_bot
```

`MFY_ADMIN_*` qatorlarini imkon qadar to'liq kiriting.
Agar ayrim MFYlar qolib ketsa, bot repo ichidagi `region_leaders.env` faylidan fallback sifatida foydalanadi.

Eng oson yo'l:

1. local `.env` dagi qiymatlarni oching
2. Northflank `Runtime variables` ga birma-bir ko'chiring
3. `.env` faylning o'zini yuklamang

## 6. Ishga tushirish

Deploy tugagach service logida bot polling boshlaganini ko'rasiz.

Bot to'g'ri ishga tushganini tekshirish:

1. Telegram'da `/start` yuboring
2. kanal obunasi tekshiruvini sinab ko'ring
3. bitta test murojaat yuborib admin tomonga kelishini tekshiring

## 7. Agar free sandbox yetmasa

Agar Northflank free cheklovlari sizga mos kelmasa, shu loyiha uchun eng yaxshi keyingi tekin variant:

- Oracle Cloud Always Free VM

Bu repo ichida VPS uchun tayyor fayllar bor:

- `deploy/install_vps.sh`
- `deploy/murojat-bot.service.example`

Oracle VM'da ular bilan botni systemd orqali 24/7 ishlatish mumkin.
