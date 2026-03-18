# Dadik Pro — Foydalanish bo'yicha qo'llanma

Ushbu hujjat **Dadik Pro** platformasini o'rnatish, sozlash va undan foydalanish bo'yicha to'liq ma'lumot beradi. Platforma hozirda **PostgreSQL** ma'lumotlar bazasi va **Eskiz.uz** SMS xizmati bilan to'liq integratsiya qilingan.

## 🚀 Tizimning asosiy imkoniyatlari
- **Mijozlar Bazasi**: Mijozlarni ro'yxatga olish va ularning ma'lumotlarini boshqarish.
- **Bonus Tizimi**: Har bir mijozga ballar qo'shish va ularni kuzatib borish.
- **SMS Marketing**: Eskiz.uz orqali barcha mijozlarga bir vaqtning o'zida SMS yuborish.
- **Kontent Boshqaruvi**: Saytdagi yangiliklar va bannerlarni dashboard orqali boshqarish.
- **Eksport**: Mijozlar bazasini Excel va CSV formatlarida yuklab olish.

## 🛠 O'rnatish va Ishga tushirish

### 1. Ma'lumotlar bazasini sozlash (PostgreSQL)
Tizim endi SQLite o'rniga PostgreSQL'da ishlaydi. Bazani sozlash uchun terminalga quyidagini yozing:
```bash
sudo -u postgres psql -c "CREATE USER kali WITH PASSWORD '123'; ALTER USER kali CREATEDB;"
createdb dadikpro
```

### 2. Virtual muhitni faollashtirish va kutubxonalarni o'rnatish
```bash
source venv_linux/bin/activate
pip install -r requirements.txt
```

### 3. Migratsiyalarni amalga oshirish
Bazadagi jadvallarni yaratish uchun:
```bash
python manage.py migrate
```

### 4. Admin yaratish
Admin panelga kirish uchun maxsus foydalanuvchi yaratilgan:
- **Login**: `admin`
- **Parol**: `123`
*(Agar qaytadan yaratish kerak bo'lsa: `python create_admin.py`)*

### 5. Serverni ishga tushirish
```bash
python manage.py runserver
```

## 📩 Eskiz SMS Xizmati
Tizim **Eskiz.uz** API orqali ishlaydi. SMS yuborish uchun `.env` faylida sizning ma'lumotlaringiz saqlangan:
- `ESKIZ_EMAIL`: ruslanxusenov28@gmail.com
- `ESKIZ_PASSWORD`: *Siz bergan maxfiy parol*

**SMS yuborish tartibi:**
1. Admin panelga kiring.
2. "SMS Marketing" bo'limiga o'ting.
3. Xabar matnini yozing.
4. "Kampaniyani boshlash" tugmasini bosing. Tizim avtomatik ravishda Eskiz'dan `token` oladi va barcha mijozlarga SMS yuboradi.

## 📊 Dashboard Bo'limlari
- **Bosh sahifa**: Jami mijozlar soni va bugungi yangi qo'shilganlar ko'rinadi.
- **Mijozlar**: Ro'yxatdagi barcha mijozlarni qidirish va boshqarish.
- **Ball qo'shish**: Mijozning ID raqami orqali unga bonus ballar berish.
- **Yangiliklar/Bannerlar**: Saytning asosiy sahifasidagi reklamalarni yangilash.

## 📁 Fayllar strukturasi
- `apps/customers/`: Mijozlar modeli va mantiqi.
- `apps/marketing/utils.py`: Eskiz API bilan bog'lanuvchi mijoz klassi.
- `templates/dashboard/`: Admin panelning vizual ko'rinishi.
- `core/settings.py`: Asosiy sozlamalar va API kalitlari.

---
**Dadik Pro — Biznesingizni avtomatlashtirishda yordam beradi!**