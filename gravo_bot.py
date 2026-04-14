“””
GRAVO Bot v3.0 — Groq AI Edition
“””

import os, time, logging, sqlite3
import threading, requests
from datetime import datetime
from pathlib import Path
from flask import Flask

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ══════════════════════════════════════════════════════════════

# ✏️  منطقة التعديل — عدّل هنا فقط

# ══════════════════════════════════════════════════════════════

BOT_TOKEN      = os.environ.get(“BOT_TOKEN”, “”)
ADMIN_IDS      = list(map(int, os.environ.get(“ADMIN_IDS”, “123456789”).split(”,”)))
GROQ_API_KEY   = os.environ.get(“GROQ_API_KEY”, “”)
WHATSAPP       = “213668338569”
TELEGRAM_ADMIN = “HamidBnc”

SHOP = {
“name”:    “GRAVO”,
“version”: “v1.0”,
“address”: “Universite Abou Bekr Belkaid - Departement Architecture, Chetouane, Tlemcen”,
“phone”:   “06 68 33 85 69”,
“hours”: {
“ar”: {
“الأحد - الخميس”: “07:15 - 17:00”,
“الجمعة”: “مغلق”,
“السبت”: “بطلب مسبق فقط”,
},
“fr”: {
“Dim - Jeu”: “07:15 - 17:00”,
“Vendredi”: “Ferme”,
“Samedi”: “Sur demande uniquement”,
},
“en”: {
“Sun - Thu”: “07:15 - 17:00”,
“Friday”: “Closed”,
“Saturday”: “By prior request only”,
},
},
}

SPECIALTIES = [
“Genie Architecture”,
“Genie Electrique”,
“Genie Mecanique”,
“Autre specialite”,
]

PRICES = {
“A4”: {
“Papier normal”:  10,
“Papier Photo”:   50,
“Autocollants”:   50,
},
“A3”: {
“Couleur”:        50,
“Noir et Blanc”:  30,
},
“A2”: {
“Couleur”:       100,
“Noir et Blanc”:  70,
“Papier Photo”:    0,
},
“A1”: {
“Couleur”:       200,
“Noir et Blanc”: 150,
“Papier Photo”:    0,
},
“A0”: {
“Couleur HQ”:    350,
“Noir et Blanc”: 300,
},
}

SUBSCRIPTIONS = {
“ChatGPT”:         {“price”: 800,  “emoji”: “🤖”},
“Gemini Pro”:      {“price”: 900,  “emoji”: “✨”},
“Canva Pro”:       {“price”: 750,  “emoji”: “🎨”},
“CapCut Pro”:      {“price”: 1000, “emoji”: “🎬”},
“YouTube Premium”: {“price”: 1000, “emoji”: “▶️”},
“Netflix”:         {“price”: 1500, “emoji”: “🎥”},
“Disney+”:         {“price”: 1200, “emoji”: “🏰”},
}

PACKS = {
“student_pack”: {
“name”: “Student Pack”,
“emoji”: “🔥”,
“items”: [“Canva Pro”, “ChatGPT”],
“price”: 1200,
“full”:  1550,
},
“ai_comparison”: {
“name”: “AI Comparison Pack”,
“emoji”: “🎯”,
“items”: [“ChatGPT”, “Gemini Pro”],
“price”: 1350,
“full”:  1700,
},
“power_ai”: {
“name”: “Power AI Pack”,
“emoji”: “⚡”,
“items”: [“ChatGPT”, “Gemini Pro”, “Canva Pro”],
“price”: 1900,
“full”:  2450,
},
“content_creator”: {
“name”: “Content Creator Pack”,
“emoji”: “🎬”,
“items”: [“Canva Pro”, “CapCut Pro”, “YouTube Premium”],
“price”: 2100,
“full”:  2750,
},
“entertainment”: {
“name”: “Entertainment Pack”,
“emoji”: “🍿”,
“items”: [“Netflix”, “Disney+”, “YouTube Premium”],
“price”: 2800,
“full”:  3700,
},
“ultimate_ai”: {
“name”: “Ultimate AI Pack”,
“emoji”: “🚀”,
“items”: [“ChatGPT”, “Gemini Pro”, “Canva Pro”, “CapCut Pro”],
“price”: 2600,
“full”:  3450,
},
“all_in_one”: {
“name”: “All In One”,
“emoji”: “💫”,
“items”: [“ChatGPT”, “Gemini Pro”, “Canva Pro”, “CapCut Pro”, “YouTube Premium”, “Netflix”, “Disney+”],
“price”: 5000,
“full”:  7150,
},
“vip_access”: {
“name”: “VIP Access”,
“emoji”: “💎”,
“items”: [“ChatGPT”, “Gemini Pro”, “Canva Pro”, “CapCut Pro”, “YouTube Premium”, “Netflix”, “Disney+”],
“price”: 6000,
“full”:  None,
},
}

VIP_LEVELS = {
“Bronze”: {
“emoji”: “🥉”,
“ar”: [“اولوية بسيطة في الطلبات”, “تعديل واحد لكل مشروع”, “وصول للقوالب”, “بطاقة GRAVO VIP”],
“fr”: [“Priorite simple”, “1 modification par projet”, “Acces aux modeles”, “Carte GRAVO VIP”],
“en”: [“Basic priority”, “1 edit per project”, “Template access”, “GRAVO VIP card”],
},
“Silver”: {
“emoji”: “🥈”,
“ar”: [“كل مزايا Bronze”, “تعديلات غير محدودة”, “خصم 10%”, “محتوى حصري”, “استشارة عبر الخاص”],
“fr”: [“Tout Bronze”, “Modifications illimitees”, “Reduction 10%”, “Contenu exclusif”, “Consultation directe”],
“en”: [“All Bronze”, “Unlimited edits”, “10% discount”, “Exclusive content”, “Direct consultation”],
},
“Gold”: {
“emoji”: “🥇”,
“ar”: [“كل مزايا Silver”, “ارشاد شخصي لكل مشروع”, “مشاريع جاهزة VIP”, “اولوية قصوى”, “طباعة Premium”],
“fr”: [“Tout Silver”, “Accompagnement personnel”, “Projets VIP prets”, “Priorite maximale”, “Impression Premium”],
“en”: [“All Silver”, “Personal guidance”, “Ready VIP projects”, “Max priority”, “Premium printing”],
},
“Platinum”: {
“emoji”: “💎”,
“ar”: [“كل مزايا Gold”, “دعم مستمر 24/7”, “تواصل مباشر مع الادارة”, “شهادة VIP”, “هدايا دورية”, “طباعة Ultra Premium”],
“fr”: [“Tout Gold”, “Support 24/7”, “Contact direct direction”, “Certificat VIP”, “Cadeaux periodiques”, “Ultra Premium”],
“en”: [“All Gold”, “24/7 support”, “Direct admin contact”, “VIP certificate”, “Periodic gifts”, “Ultra Premium printing”],
},
}

# ══════════════════════════════════════════════════════════════

# النصوص بـ 3 لغات

# ══════════════════════════════════════════════════════════════

MSG = {
“choose_lang”: “🌐 Choose your language / اختر لغتك / Choisissez votre langue”,
“welcome”: {
“ar”: “🔥 <b>مرحبا بك في GRAVO Community v1.0</b>\n\nنظام احترافي لطالب الهندسة.\nلا انتظار. لا تشويش. نتائج فقط.\n\n🎯 اختر ما تحتاجه:”,
“fr”: “🔥 <b>Bienvenue dans GRAVO Community v1.0</b>\n\nSysteme professionnel pour l’etudiant en ingenierie.\nPas d’attente. Pas de confusion. Resultats uniquement.\n\n🎯 Choisissez ce dont vous avez besoin :”,
“en”: “🔥 <b>Welcome to GRAVO Community v1.0</b>\n\nA professional system for engineering students.\nNo waiting. No confusion. Results only.\n\n🎯 Choose what you need:”,
},
“reg_start”: {
“ar”: “👋 <b>اهلا بك في GRAVO!</b>\n\nسجّل معلوماتك مرة واحدة فقط\nوسيتذكرك البوت دائما!\n\n📝 <b>ما اسمك الكامل؟</b>”,
“fr”: “👋 <b>Bienvenue dans GRAVO!</b>\n\nEnregistrez vos informations une seule fois\nLe bot se souviendra de vous!\n\n📝 <b>Quel est votre nom complet?</b>”,
“en”: “👋 <b>Welcome to GRAVO!</b>\n\nRegister your info once\nThe bot will always remember you!\n\n📝 <b>What is your full name?</b>”,
},
“reg_specialty”: {
“ar”: “🎓 <b>ما تخصصك؟</b>”,
“fr”: “🎓 <b>Quelle est votre specialite?</b>”,
“en”: “🎓 <b>What is your specialty?</b>”,
},
“reg_year”: {
“ar”: “📅 <b>ما سنتك الدراسية؟</b>”,
“fr”: “📅 <b>Quelle est votre annee d’etude?</b>”,
“en”: “📅 <b>What is your academic year?</b>”,
},
“reg_group”: {
“ar”: “👥 <b>رقم groupك؟</b>\n<i>(مثال: G1, G2…)</i>”,
“fr”: “👥 <b>Votre numero de groupe?</b>\n<i>(ex: G1, G2…)</i>”,
“en”: “👥 <b>Your group number?</b>\n<i>(e.g. G1, G2…)</i>”,
},
“reg_hall”: {
“ar”: “🚪 <b>رقم القاعة او المدرج؟</b>\n<i>(مثال: Amphi A, Salle 12)</i>”,
“fr”: “🚪 <b>Numero de salle ou amphitheatre?</b>\n<i>(ex: Amphi A, Salle 12)</i>”,
“en”: “🚪 <b>Hall or lecture room number?</b>\n<i>(e.g. Amphi A, Room 12)</i>”,
},
“reg_done”: {
“ar”: “✅ <b>تم التسجيل!</b>\n\nالبوت سيتذكرك دائما 🤖”,
“fr”: “✅ <b>Inscription reussie!</b>\n\nLe bot se souviendra toujours de vous 🤖”,
“en”: “✅ <b>Registration complete!</b>\n\nThe bot will always remember you 🤖”,
},
“main_menu”: {
“ar”: “📋 القائمة الرئيسية:”,
“fr”: “📋 Menu principal:”,
“en”: “📋 Main menu:”,
},
“btn_student”:   {“ar”: “🎓 خدمات الطلبة”,   “fr”: “🎓 Services etudiants”, “en”: “🎓 Student Services”},
“btn_quick”:     {“ar”: “⚡ خدمات سريعة”,    “fr”: “⚡ Services rapides”,    “en”: “⚡ Quick Services”},
“btn_subs”:      {“ar”: “💳 الاشتراكات”,      “fr”: “💳 Abonnements”,         “en”: “💳 Subscriptions”},
“btn_vip”:       {“ar”: “👑 VIP”,              “fr”: “👑 VIP”,                 “en”: “👑 VIP”},
“btn_assistant”: {“ar”: “🤖 مساعد Gravo”,     “fr”: “🤖 Assistant Gravo”,     “en”: “🤖 Gravo Assistant”},
“btn_back”:      {“ar”: “↩️ رجوع”,            “fr”: “↩️ Retour”,              “en”: “↩️ Back”},
“btn_profile”:   {“ar”: “👤 ملفي”,            “fr”: “👤 Mon profil”,           “en”: “👤 My profile”},
“btn_lang”:      {“ar”: “🌐 تغيير اللغة”,     “fr”: “🌐 Changer la langue”,    “en”: “🌐 Change language”},
“btn_print”:     {“ar”: “🖨️ طباعة”,           “fr”: “🖨️ Impression”,          “en”: “🖨️ Printing”},
“btn_design”:    {“ar”: “📐 تصميم مشروع”,     “fr”: “📐 Conception projet”,    “en”: “📐 Project design”},
“btn_edit”:      {“ar”: “✏️ تعديل مشروع”,     “fr”: “✏️ Modification projet”,  “en”: “✏️ Project editing”},
“btn_maquette”:  {“ar”: “🏗️ ماكيت”,           “fr”: “🏗️ Maquette”,            “en”: “🏗️ Maquette”},
“btn_convert”:   {“ar”: “🔄 تحويل PDF-PNG”,   “fr”: “🔄 Convertir PDF-PNG”,   “en”: “🔄 Convert PDF-PNG”},
“btn_fix”:       {“ar”: “🔧 تصحيح ملف”,       “fr”: “🔧 Corriger fichier”,     “en”: “🔧 Fix file”},
“btn_imgfix”:    {“ar”: “🖼️ تعديل صورة”,     “fr”: “🖼️ Modifier image”,       “en”: “🖼️ Edit image”},
“btn_individual”:{“ar”: “📱 خدمات فردية”,     “fr”: “📱 Services individuels”, “en”: “📱 Individual services”},
“btn_packs”:     {“ar”: “📦 الباقات”,          “fr”: “📦 Packs”,                “en”: “📦 Packs”},
“btn_confirm”:   {“ar”: “✅ تاكيد”,            “fr”: “✅ Confirmer”,            “en”: “✅ Confirm”},
“btn_cancel”:    {“ar”: “❌ الغاء”,            “fr”: “❌ Annuler”,              “en”: “❌ Cancel”},
“btn_free”:      {“ar”: “🟢 متابعة عادي”,     “fr”: “🟢 Continuer normal”,    “en”: “🟢 Continue normal”},
“btn_upgrade”:   {“ar”: “💎 الترقية الى VIP”, “fr”: “💎 Passer au VIP”,       “en”: “💎 Upgrade to VIP”},
“btn_vip_now”:   {“ar”: “⚡ VIP الان”,         “fr”: “⚡ VIP maintenant”,       “en”: “⚡ VIP now”},
“btn_join_vip”:  {“ar”: “✅ اريد الانضمام”,    “fr”: “✅ Je veux rejoindre”,    “en”: “✅ I want to join”},
“btn_whatsapp”:  {“ar”: “💬 واتساب”,           “fr”: “💬 WhatsApp”,             “en”: “💬 WhatsApp”},
“btn_telegram”:  {“ar”: “✈️ تيليغرام”,        “fr”: “✈️ Telegram”,            “en”: “✈️ Telegram”},
“print_choice”: {
“ar”: “🖨️ <b>طلب الطباعة</b>\n\n🟢 <b>الوضع العادي:</b>\n  تنفيذ حسب الضغط الحالي\n  بدون اولوية\n\n💎 <b>VIP:</b>\n  تنفيذ سريع\n  اولوية مباشرة\n  جودة Premium\n\n🎯 ماذا تريد الان؟”,
“fr”: “🖨️ <b>Demande d’impression</b>\n\n🟢 <b>Mode normal:</b>\n  Execution selon la charge\n  Sans priorite\n\n💎 <b>VIP:</b>\n  Execution rapide\n  Priorite immediate\n  Qualite Premium\n\n🎯 Que voulez-vous maintenant?”,
“en”: “🖨️ <b>Print Request</b>\n\n🟢 <b>Normal mode:</b>\n  Execution based on current load\n  No priority\n\n💎 <b>VIP:</b>\n  Fast execution\n  Immediate priority\n  Premium quality\n\n🎯 What do you want now?”,
},
“vip_push”: {
“ar”: “⏳ <b>طلبك قيد التنفيذ حسب الضغط الحالي.</b>\n\n💎 تريد اولوية؟\nاضغط VIP الان واحصل على:\n  تنفيذ فوري\n  جودة اعلى\n  دعم مباشر\n\n⏰ الطلب عالي - VIP يحصل على اولوية!”,
“fr”: “⏳ <b>Votre commande est en cours.</b>\n\n💎 Vous voulez la priorite?\nAppuyez sur VIP maintenant:\n  Execution immediate\n  Meilleure qualite\n  Support direct\n\n⏰ Forte demande - VIP obtient la priorite!”,
“en”: “⏳ <b>Your order is being processed.</b>\n\n💎 Want priority?\nPress VIP now and get:\n  Instant execution\n  Higher quality\n  Direct support\n\n⏰ High demand - VIP gets priority!”,
},
“vip_intro”: {
“ar”: “👑 <b>GRAVO VIP</b>\n\nتهانينا، انت على وشك الدخول لمستوى مختلف.\n\n⚡ تنفيذ سريع\n⚡ اولوية كاملة\n⚡ محتوى وخدمات متقدمة\n\n⏰ <b>الاماكن محدودة!</b>\nالفائزون يتصرفون الان.\n\nاختر مستواك:”,
“fr”: “👑 <b>GRAVO VIP</b>\n\nFelicitations, vous etes sur le point d’entrer dans un niveau different.\n\n⚡ Execution rapide\n⚡ Priorite complete\n⚡ Contenu et services avances\n\n⏰ <b>Places limitees!</b>\nLes gagnants agissent maintenant.\n\nChoisissez votre niveau:”,
“en”: “👑 <b>GRAVO VIP</b>\n\nCongratulations, you’re about to enter a different level.\n\n⚡ Fast execution\n⚡ Full priority\n⚡ Advanced content and services\n\n⏰ <b>Limited spots!</b>\nWinners act now.\n\nChoose your level:”,
},
“subs_intro”: {
“ar”: “💳 <b>الاشتراكات المتاحة</b>\n\nاختر خدمة او باقة:”,
“fr”: “💳 <b>Abonnements disponibles</b>\n\nChoisissez un service ou un pack:”,
“en”: “💳 <b>Available Subscriptions</b>\n\nChoose a service or pack:”,
},
“sub_request”: {
“ar”: “📧 <b>ارسل بريدك الالكتروني</b>\nسنتواصل معك لاتمام الاشتراك:”,
“fr”: “📧 <b>Envoyez votre adresse email</b>\nNous vous contacterons pour finaliser l’abonnement:”,
“en”: “📧 <b>Send your email address</b>\nWe will contact you to complete the subscription:”,
},
“sub_received”: {
“ar”: “✅ <b>تم استلام طلبك!</b>\nسيتواصل معك فريقنا قريبا.”,
“fr”: “✅ <b>Votre demande a ete recue!</b>\nNotre equipe vous contactera bientot.”,
“en”: “✅ <b>Your request has been received!</b>\nOur team will contact you soon.”,
},
“order_received”: {
“ar”: “✅ <b>تم استلام طلبك!</b>\nسيتواصل معك فريقنا قريبا.”,
“fr”: “✅ <b>Votre commande a ete recue!</b>\nNotre equipe vous contactera bientot.”,
“en”: “✅ <b>Your order has been received!</b>\nOur team will contact you soon.”,
},
“design_intro”: {
“ar”: “📐 <b>تصميم مشروع</b>\n\nارسل التفاصيل:\n1 نوع المشروع (منزل / عمارة / …)\n2 عدد الطوابق\n3 هل لديك فكرة او مثال؟\n4 الموعد النهائي\n\nارسل في رسالة واحدة”,
“fr”: “📐 <b>Conception de projet</b>\n\nEnvoyez les details:\n1 Type de projet\n2 Nombre d’etages\n3 Avez-vous une idee ou exemple?\n4 Date limite\n\nEnvoyez en un seul message”,
“en”: “📐 <b>Project Design</b>\n\nSend the details:\n1 Project type\n2 Number of floors\n3 Do you have an idea or example?\n4 Deadline\n\nSend in one message”,
},
“edit_intro”: {
“ar”: “✏️ <b>تعديل مشروع</b>\n\nارسل:\nالملف (PDF / صورة)\nالتعديلات المطلوبة\nالموعد النهائي\n\nسيتم الرد عليك مباشرة”,
“fr”: “✏️ <b>Modification de projet</b>\n\nEnvoyez:\nLe fichier (PDF / image)\nLes modifications souhaitees\nDate limite\n\nVous serez contacte directement”,
“en”: “✏️ <b>Project Editing</b>\n\nSend:\nThe file (PDF / image)\nRequired modifications\nDeadline\n\nYou will be contacted directly”,
},
“assistant_intro”: {
“ar”: “🤖 <b>مساعد Gravo</b>\n\nيمكنك سؤالي عن اي شيء:\nالاسعار والخدمات\nكيفية عمل النظام\nنصائح للمشروع\n\nساوجهك مباشرة للخدمة المناسبة”,
“fr”: “🤖 <b>Assistant Gravo</b>\n\nVous pouvez me poser n’importe quelle question:\nTarifs et services\nFonctionnement du systeme\nConseils pour votre projet\n\nJe vous guiderai vers le service appropriate”,
“en”: “🤖 <b>Gravo Assistant</b>\n\nYou can ask me anything:\nPrices and services\nHow the system works\nProject tips\n\nI will guide you to the right service”,
},
“send_file_first”: {
“ar”: “ارسل الملف اولا (PDF او صورة).”,
“fr”: “Envoyez d’abord le fichier (PDF ou image).”,
“en”: “Send the file first (PDF or image).”,
},
“quick_received”: {
“ar”: “تم استلام الملف وسيتم معالجته فورا!”,
“fr”: “Fichier recu et sera traite immediatement!”,
“en”: “File received and will be processed immediately!”,
},
}

SYSTEM_PROMPT = “”“You are the smart assistant of GRAVO - a professional print and design service center for engineering students at Universite Abou Bekr Belkaid, Chetouane, Tlemcen.

SHOP INFO:
Address: Departement Architecture, Chetouane, Tlemcen
Phone: 06 68 33 85 69
Hours: Sunday to Thursday 07:15 to 17:00 | Friday closed | Saturday by prior request only

PRINTING PRICES:
A4: normal paper 10da | Photo paper 50da | Stickers 50da
A3: Color 50da | Black&White 30da
A2: Color 100da | B&W 70da
A1: Color 200da | B&W 150da
A0: Color HQ 350da | B&W 300da

SUBSCRIPTIONS:
ChatGPT: 800da | Gemini Pro: 900da | Canva Pro: 750da
CapCut Pro: 1000da | YouTube Premium: 1000da
Netflix: 1500da | Disney+: 1200da

VIP SYSTEM: Bronze, Silver, Gold, Platinum
Benefits: Priority execution, Premium printing, Personal consultation, VIP card

RESPONSE RULES:

1. Always respond in the SAME language the user writes in (Arabic, French, English, or Algerian dialect)
1. Always respond in 3 steps: Answer -> Guide to service -> CTA
1. VIP upsell at 3 points: after file submission, when detecting delays, when user hesitates
1. Use FOMO: “Limited spots!” | “High demand” | “Winners act now”
1. Be professional, persuasive, and friendly
1. For Saturday: explain prior authorization requirement
1. Keep responses short and clear
   “””

# ══════════════════════════════════════════════════════════════

# Logging

# ══════════════════════════════════════════════════════════════

logging.basicConfig(
level=logging.INFO,
format=”%(asctime)s [%(levelname)s] %(message)s”
)
log = logging.getLogger(“GRAVO”)

# ══════════════════════════════════════════════════════════════

# قاعدة البيانات

# ══════════════════════════════════════════════════════════════

DB_PATH = “/tmp/gravo.db”

class DB:
def **init**(self):
self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
self._init()

```
def _init(self):
    self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            chat_id     INTEGER PRIMARY KEY,
            username    TEXT,
            full_name   TEXT,
            specialty   TEXT,
            year        TEXT,
            group_num   TEXT,
            hall        TEXT,
            lang        TEXT DEFAULT 'ar',
            vip_level   TEXT,
            vip_number  INTEGER,
            joined_at   TEXT,
            last_seen   TEXT
        );
        CREATE TABLE IF NOT EXISTS orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id     INTEGER,
            type        TEXT DEFAULT 'print',
            filename    TEXT,
            size        TEXT,
            paper       TEXT,
            copies      INTEGER DEFAULT 1,
            price       TEXT,
            details     TEXT,
            status      TEXT DEFAULT 'pending',
            created_at  TEXT
        );
    """)
    self.conn.commit()

def get_student(self, chat_id):
    cur = self.conn.execute("SELECT * FROM students WHERE chat_id=?", (chat_id,))
    row = cur.fetchone()
    if not row:
        return None
    return dict(zip([d[0] for d in cur.description], row))

def save_student(self, chat_id, **kwargs):
    existing = self.get_student(chat_id)
    kwargs["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    if existing:
        sets = ", ".join(f"{k}=?" for k in kwargs)
        self.conn.execute(
            f"UPDATE students SET {sets} WHERE chat_id=?",
            list(kwargs.values()) + [chat_id]
        )
    else:
        kwargs["chat_id"] = chat_id
        kwargs["joined_at"] = kwargs["last_seen"]
        cols = ", ".join(kwargs.keys())
        self.conn.execute(
            f"INSERT INTO students ({cols}) VALUES ({','.join(['?']*len(kwargs))})",
            list(kwargs.values())
        )
    self.conn.commit()

def get_lang(self, chat_id):
    s = self.get_student(chat_id)
    return s.get("lang", "ar") if s else "ar"

def add_vip(self, chat_id, level):
    cur = self.conn.execute(
        "SELECT COUNT(*)+1 FROM students WHERE vip_level IS NOT NULL"
    )
    num = cur.fetchone()[0]
    self.conn.execute(
        "UPDATE students SET vip_level=?, vip_number=? WHERE chat_id=?",
        (level, num, chat_id)
    )
    self.conn.commit()
    return num

def add_order(self, chat_id, type_="print", filename="", size="",
              paper="", copies=1, price="", details=""):
    cur = self.conn.execute(
        "INSERT INTO orders (chat_id,type,filename,size,paper,copies,price,details,status,created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (chat_id, type_, filename, size, paper, copies, price, details,
         "pending", datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    self.conn.commit()
    return cur.lastrowid

def get_orders(self, chat_id, n=3):
    cur = self.conn.execute(
        "SELECT * FROM orders WHERE chat_id=? ORDER BY created_at DESC LIMIT ?",
        (chat_id, n)
    )
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]

def stats(self):
    cur = self.conn.execute("""
        SELECT
            (SELECT COUNT(*) FROM students) students,
            (SELECT COUNT(*) FROM students WHERE vip_level IS NOT NULL) vips,
            (SELECT COUNT(*) FROM orders) orders,
            (SELECT COUNT(*) FROM orders WHERE status='pending') pending
    """)
    return dict(zip(["students", "vips", "orders", "pending"], cur.fetchone()))
```

db           = DB()
bot          = telebot.TeleBot(BOT_TOKEN, parse_mode=“HTML”)
user_states  = {}
user_history = {}

# ══════════════════════════════════════════════════════════════

# مساعدات اللغة

# ══════════════════════════════════════════════════════════════

def T(key, lang=“ar”):
val = MSG.get(key)
if isinstance(val, dict):
return val.get(lang, val.get(“ar”, “”))
return val or “”

def L(chat_id):
return db.get_lang(chat_id)

# ══════════════════════════════════════════════════════════════

# Groq AI

# ══════════════════════════════════════════════════════════════

def ask_ai(chat_id, text):
student = db.get_student(chat_id) or {}
ctx = “”
if student.get(“full_name”):
ctx += (
f”\n[Student: {student.get(‘full_name’)} | “
f”{student.get(‘specialty’, ‘’)} | “
f”{student.get(‘year’, ‘’)} | “
f”G{student.get(‘group_num’, ‘’)} | “
f”Lang: {student.get(‘lang’, ‘ar’)}]”
)
if student.get(“vip_level”):
ctx += f”\n[VIP: {student[‘vip_level’]} #{student.get(‘vip_number’, 0):03d}]”

```
hist = user_history.setdefault(chat_id, [])
hist.append({"role": "user", "content": text + ctx})
if len(hist) > 12:
    hist[:] = hist[-12:]

try:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + hist
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": messages,
            "max_tokens": 800,
            "temperature": 0.7,
        },
        timeout=25
    )
    data = response.json()
    reply = data["choices"][0]["message"]["content"]
    if reply:
        hist.append({"role": "assistant", "content": reply})
        return reply
except Exception as e:
    log.error(f"Groq ERROR: {e}")

lang = L(chat_id)
errors = {
    "ar": "⚠️ خطا مؤقت. تواصل معنا: 06 68 33 85 69",
    "fr": "⚠️ Erreur temporaire. Contactez-nous: 06 68 33 85 69",
    "en": "⚠️ Temporary error. Contact us: 06 68 33 85 69",
}
return errors.get(lang, errors["ar"])
```

# ══════════════════════════════════════════════════════════════

# لوحات المفاتيح

# ══════════════════════════════════════════════════════════════

def lang_kb():
kb = InlineKeyboardMarkup(row_width=3)
kb.add(
InlineKeyboardButton(“🇩🇿 العربية”,  callback_data=“lang_ar”),
InlineKeyboardButton(“🇫🇷 Français”, callback_data=“lang_fr”),
InlineKeyboardButton(“🇬🇧 English”,  callback_data=“lang_en”),
)
return kb

def main_kb(chat_id):
lang = L(chat_id)
kb = InlineKeyboardMarkup(row_width=2)
kb.add(
InlineKeyboardButton(T(“btn_student”,   lang), callback_data=“m_student”),
InlineKeyboardButton(T(“btn_quick”,     lang), callback_data=“m_quick”),
InlineKeyboardButton(T(“btn_subs”,      lang), callback_data=“m_subs”),
InlineKeyboardButton(T(“btn_vip”,       lang), callback_data=“m_vip”),
InlineKeyboardButton(T(“btn_assistant”, lang), callback_data=“m_assistant”),
)
s = db.get_student(chat_id)
if s and s.get(“vip_level”):
kb.add(InlineKeyboardButton(
f”🪪 {s[‘vip_level’]}”, callback_data=“m_card”
))
kb.add(
InlineKeyboardButton(T(“btn_profile”, lang), callback_data=“m_profile”),
InlineKeyboardButton(T(“btn_lang”,    lang), callback_data=“m_lang”),
)
return kb

def back_kb(lang=“ar”):
return InlineKeyboardMarkup().add(
InlineKeyboardButton(T(“btn_back”, lang), callback_data=“back”)
)

def student_kb(lang):
kb = InlineKeyboardMarkup(row_width=2)
kb.add(
InlineKeyboardButton(T(“btn_print”,    lang), callback_data=“m_print”),
InlineKeyboardButton(T(“btn_design”,   lang), callback_data=“m_design”),
InlineKeyboardButton(T(“btn_edit”,     lang), callback_data=“m_edit”),
InlineKeyboardButton(T(“btn_maquette”, lang), callback_data=“m_maquette”),
InlineKeyboardButton(T(“btn_back”,     lang), callback_data=“back”),
)
return kb

def quick_kb(lang):
kb = InlineKeyboardMarkup(row_width=1)
kb.add(
InlineKeyboardButton(T(“btn_convert”, lang), callback_data=“qs_convert”),
InlineKeyboardButton(T(“btn_fix”,     lang), callback_data=“qs_fix”),
InlineKeyboardButton(T(“btn_imgfix”,  lang), callback_data=“qs_imgfix”),
InlineKeyboardButton(T(“btn_back”,    lang), callback_data=“back”),
)
return kb

def subs_main_kb(lang):
kb = InlineKeyboardMarkup(row_width=2)
kb.add(
InlineKeyboardButton(T(“btn_individual”, lang), callback_data=“subs_individual”),
InlineKeyboardButton(T(“btn_packs”,      lang), callback_data=“subs_packs”),
InlineKeyboardButton(T(“btn_back”,       lang), callback_data=“back”),
)
return kb

def subs_individual_kb(lang):
kb = InlineKeyboardMarkup(row_width=1)
for key, val in SUBSCRIPTIONS.items():
kb.add(InlineKeyboardButton(
f”{val[‘emoji’]} {key} - {val[‘price’]} da”,
callback_data=f”sub_{key}”
))
kb.add(InlineKeyboardButton(T(“btn_back”, lang), callback_data=“subs_back”))
return kb

def subs_packs_kb(lang):
kb = InlineKeyboardMarkup(row_width=1)
for key, pack in PACKS.items():
discount = “”
if pack[“full”]:
pct = round((1 - pack[“price”] / pack[“full”]) * 100)
discount = f” (-{pct}%)”
kb.add(InlineKeyboardButton(
f”{pack[‘emoji’]} {pack[‘name’]} - {pack[‘price’]} da{discount}”,
callback_data=f”pack_{key}”
))
kb.add(InlineKeyboardButton(T(“btn_back”, lang), callback_data=“subs_back”))
return kb

def print_choice_kb(lang):
kb = InlineKeyboardMarkup(row_width=1)
kb.add(
InlineKeyboardButton(T(“btn_free”,    lang), callback_data=“print_free”),
InlineKeyboardButton(T(“btn_upgrade”, lang), callback_data=“m_vip”),
)
return kb

def size_kb(lang):
kb = InlineKeyboardMarkup(row_width=3)
for s in [“A4”, “A3”, “A2”, “A1”, “A0”]:
kb.add(InlineKeyboardButton(f”📄 {s}”, callback_data=f”sz_{s}”))
kb.add(InlineKeyboardButton(T(“btn_back”, lang), callback_data=“back”))
return kb

def paper_kb(size, lang):
kb = InlineKeyboardMarkup(row_width=1)
for label, price in PRICES.get(size, {}).items():
p = f”{price} da” if price else “Prix special”
kb.add(InlineKeyboardButton(
f”{label} - {p}”,
callback_data=f”pp_{label}_{price}”
))
kb.add(InlineKeyboardButton(T(“btn_back”, lang), callback_data=“back_size”))
return kb

def copies_kb():
kb = InlineKeyboardMarkup(row_width=5)
for i in [1, 2, 3, 5, 10]:
kb.add(InlineKeyboardButton(str(i), callback_data=f”cp_{i}”))
return kb

def confirm_kb(lang):
kb = InlineKeyboardMarkup(row_width=2)
kb.add(
InlineKeyboardButton(T(“btn_confirm”, lang), callback_data=“ok_print”),
InlineKeyboardButton(T(“btn_cancel”,  lang), callback_data=“cancel”),
)
return kb

def vip_levels_kb(lang):
kb = InlineKeyboardMarkup(row_width=2)
for level, data in VIP_LEVELS.items():
kb.add(InlineKeyboardButton(
f”{data[‘emoji’]} {level}”,
callback_data=f”vl_{level}”
))
kb.add(InlineKeyboardButton(T(“btn_back”, lang), callback_data=“back”))
return kb

def vip_join_kb(lang):
kb = InlineKeyboardMarkup(row_width=1)
kb.add(
InlineKeyboardButton(T(“btn_join_vip”, lang), url=f”https://wa.me/{WHATSAPP}”),
InlineKeyboardButton(T(“btn_telegram”, lang), url=f”https://t.me/{TELEGRAM_ADMIN}”),
InlineKeyboardButton(T(“btn_back”,     lang), callback_data=“back”),
)
return kb

def vip_push_kb(lang):
kb = InlineKeyboardMarkup(row_width=1)
kb.add(
InlineKeyboardButton(T(“btn_vip_now”, lang), callback_data=“m_vip”),
InlineKeyboardButton(T(“btn_back”,    lang), callback_data=“back”),
)
return kb

def contact_kb(lang):
kb = InlineKeyboardMarkup(row_width=1)
kb.add(
InlineKeyboardButton(T(“btn_whatsapp”, lang), url=f”https://wa.me/{WHATSAPP}”),
InlineKeyboardButton(T(“btn_telegram”, lang), url=f”https://t.me/{TELEGRAM_ADMIN}”),
InlineKeyboardButton(T(“btn_back”,     lang), callback_data=“back”),
)
return kb

def specialty_kb():
kb = InlineKeyboardMarkup(row_width=1)
for sp in SPECIALTIES:
kb.add(InlineKeyboardButton(sp, callback_data=f”sp_{sp}”))
return kb

def year_kb():
kb = InlineKeyboardMarkup(row_width=3)
for y in [“L1”, “L2”, “L3”, “M1”, “M2”, “Doctorat”]:
kb.add(InlineKeyboardButton(y, callback_data=f”yr_{y}”))
return kb

# ══════════════════════════════════════════════════════════════

# تسجيل الطالب

# ══════════════════════════════════════════════════════════════

def start_registration(chat_id):
user_states[chat_id] = {“step”: “choose_lang”}
bot.send_message(chat_id, T(“choose_lang”), reply_markup=lang_kb())

def handle_registration(msg):
cid   = msg.chat.id
text  = msg.text or “”
state = user_states.get(cid, {})
step  = state.get(“step”)
lang  = state.get(“lang”, db.get_lang(cid))

```
if step == "reg_name":
    state["full_name"] = text.strip()
    state["step"]      = "reg_specialty"
    user_states[cid]   = state
    bot.send_message(cid, T("reg_specialty", lang), reply_markup=specialty_kb())

elif step == "reg_group":
    state["group_num"] = text.strip()
    state["step"]      = "reg_hall"
    user_states[cid]   = state
    bot.send_message(cid, T("reg_hall", lang))

elif step == "reg_hall":
    state["hall"] = text.strip()
    db.save_student(
        cid,
        username  = msg.from_user.username or "",
        full_name = state.get("full_name", ""),
        specialty = state.get("specialty", ""),
        year      = state.get("year", ""),
        group_num = state.get("group_num", ""),
        hall      = state.get("hall", ""),
        lang      = lang,
    )
    user_states.pop(cid, None)
    s = db.get_student(cid)
    bot.send_message(
        cid,
        T("reg_done", lang) + f"\n\n"
        f"👤 {s['full_name']}\n"
        f"🎓 {s['specialty']}\n"
        f"📅 {s['year']} | G{s['group_num']}\n"
        f"🚪 {s['hall']}",
        reply_markup=main_kb(cid)
    )
```

# ══════════════════════════════════════════════════════════════

# /start

# ══════════════════════════════════════════════════════════════

@bot.message_handler(commands=[“start”])
def cmd_start(msg):
cid     = msg.chat.id
student = db.get_student(cid)
db.save_student(cid, username=msg.from_user.username or “”)

```
if not student or not student.get("full_name"):
    start_registration(cid)
    return

lang = student.get("lang", "ar")
vip  = student.get("vip_level")
name = student.get("full_name", "")

greeting = {
    "ar": f"💎 مرحبا عضو VIP {vip}!" if vip else f"اهلا {name}! 👋",
    "fr": f"💎 Bienvenue membre VIP {vip}!" if vip else f"Bonjour {name}! 👋",
    "en": f"💎 Welcome VIP member {vip}!" if vip else f"Hello {name}! 👋",
}.get(lang, "")

bot.send_message(
    cid,
    f"<b>{greeting}</b>\n"
    f"🎓 {student.get('specialty', '')} | "
    f"{student.get('year', '')} | "
    f"G{student.get('group_num', '')}\n\n"
    + T("welcome", lang),
    reply_markup=main_kb(cid)
)
```

@bot.message_handler(commands=[“menu”])
def cmd_menu(msg):
lang = L(msg.chat.id)
bot.send_message(msg.chat.id, T(“main_menu”, lang), reply_markup=main_kb(msg.chat.id))

# ══════════════════════════════════════════════════════════════

# Callbacks — اللغة

# ══════════════════════════════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data.startswith(“lang_”))
def cb_lang(call):
cid  = call.message.chat.id
lang = call.data.split(”_”)[1]
state = user_states.get(cid, {})

```
db.save_student(cid, lang=lang)

if state.get("step") == "choose_lang":
    state["lang"] = lang
    state["step"] = "reg_name"
    user_states[cid] = state
    bot.edit_message_text(T("reg_start", lang), cid, call.message.message_id)
else:
    bot.edit_message_text(
        T("main_menu", lang), cid,
        call.message.message_id,
        reply_markup=main_kb(cid)
    )
bot.answer_callback_query(call.id)
```

@bot.callback_query_handler(func=lambda c: c.data == “m_lang”)
def cb_change_lang(call):
bot.edit_message_text(
T(“choose_lang”), call.message.chat.id,
call.message.message_id, reply_markup=lang_kb()
)
bot.answer_callback_query(call.id)

# ══════════════════════════════════════════════════════════════

# Callbacks — القائمة

# ══════════════════════════════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data == “m_student”)
def cb_student(call):
cid  = call.message.chat.id
lang = L(cid)
choose = {“ar”: “اختر الخدمة:”, “fr”: “Choisissez:”, “en”: “Choose:”}.get(lang, “”)
bot.edit_message_text(
T(“btn_student”, lang) + “\n\n” + choose,
cid, call.message.message_id,
reply_markup=student_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_quick”)
def cb_quick_menu(call):
cid  = call.message.chat.id
lang = L(cid)
choose = {“ar”: “اختر الخدمة:”, “fr”: “Choisissez:”, “en”: “Choose:”}.get(lang, “”)
bot.edit_message_text(
T(“btn_quick”, lang) + “\n\n” + choose,
cid, call.message.message_id,
reply_markup=quick_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_subs”)
def cb_subs(call):
cid  = call.message.chat.id
lang = L(cid)
bot.edit_message_text(
T(“subs_intro”, lang), cid,
call.message.message_id,
reply_markup=subs_main_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “subs_individual”)
def cb_subs_individual(call):
cid  = call.message.chat.id
lang = L(cid)
bot.edit_message_text(
T(“subs_intro”, lang), cid,
call.message.message_id,
reply_markup=subs_individual_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “subs_packs”)
def cb_subs_packs(call):
cid  = call.message.chat.id
lang = L(cid)
bot.edit_message_text(
T(“subs_intro”, lang), cid,
call.message.message_id,
reply_markup=subs_packs_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “subs_back”)
def cb_subs_back(call):
cid  = call.message.chat.id
lang = L(cid)
bot.edit_message_text(
T(“subs_intro”, lang), cid,
call.message.message_id,
reply_markup=subs_main_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(“sub_”))
def cb_sub_item(call):
cid  = call.message.chat.id
lang = L(cid)
key  = call.data[4:]
sub  = SUBSCRIPTIONS.get(key, {})
user_states[cid] = {“step”: “sub_email”, “sub_item”: key}
bot.edit_message_text(
f”{sub.get(‘emoji’, ‘’)} <b>{key}</b>\n”
f”💰 {sub.get(‘price’, 0)} da\n\n”
+ T(“sub_request”, lang),
cid, call.message.message_id
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(“pack_”))
def cb_pack(call):
cid  = call.message.chat.id
lang = L(cid)
key  = call.data[5:]
pack = PACKS.get(key, {})
items = “ + “.join(pack.get(“items”, []))
user_states[cid] = {“step”: “sub_email”, “sub_item”: pack.get(“name”, key)}
bot.edit_message_text(
f”{pack.get(‘emoji’, ‘’)} <b>{pack.get(‘name’, ‘’)}</b>\n\n”
f”📦 {items}\n”
f”💰 <b>{pack.get(‘price’, 0)} da</b>\n\n”
+ T(“sub_request”, lang),
cid, call.message.message_id
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(“qs_”))
def cb_quick_service(call):
cid  = call.message.chat.id
lang = L(cid)
svc  = call.data[3:]
labels = {
“convert”: T(“btn_convert”, lang),
“fix”:     T(“btn_fix”,     lang),
“imgfix”:  T(“btn_imgfix”,  lang),
}
user_states[cid] = {“step”: f”qs_{svc}”}
bot.edit_message_text(
f”{labels.get(svc, ‘’)}\n\n” + T(“send_file_first”, lang),
cid, call.message.message_id
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_vip”)
def cb_vip(call):
cid  = call.message.chat.id
lang = L(cid)
s    = db.get_student(cid) or {}
if s.get(“vip_level”):
already = {
“ar”: f”💎 انت بالفعل عضو {s[‘vip_level’]}! 🔥”,
“fr”: f”💎 Vous etes deja membre {s[‘vip_level’]}! 🔥”,
“en”: f”💎 You are already a {s[‘vip_level’]} member! 🔥”,
}.get(lang, “”)
bot.edit_message_text(already, cid, call.message.message_id, reply_markup=back_kb(lang))
else:
bot.edit_message_text(
T(“vip_intro”, lang), cid,
call.message.message_id,
reply_markup=vip_levels_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(“vl_”))
def cb_vip_level(call):
cid   = call.message.chat.id
lang  = L(cid)
level = call.data[3:]
data  = VIP_LEVELS.get(level, {})
perks = data.get(lang, data.get(“ar”, []))
scarcity = {
“ar”: “بقيت اماكن محدودة! الفائزون يتصرفون الان.”,
“fr”: “Places limitees! Les gagnants agissent maintenant.”,
“en”: “Limited spots! Winners act now.”,
}.get(lang, “”)
bot.edit_message_text(
f”{data.get(‘emoji’, ‘’)} <b>{level}</b>\n\n”
+ “\n”.join(f”  ✅ {p}” for p in perks)
+ f”\n\n🔥 <b>{scarcity}</b>”,
cid, call.message.message_id,
reply_markup=vip_join_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_assistant”)
def cb_assistant(call):
cid  = call.message.chat.id
lang = L(cid)
user_states[cid] = {“step”: “chatting”}
bot.edit_message_text(
T(“assistant_intro”, lang), cid,
call.message.message_id,
reply_markup=back_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_print”)
def cb_print(call):
cid  = call.message.chat.id
lang = L(cid)
s    = db.get_student(cid) or {}
if s.get(“vip_level”):
user_states[cid] = {“step”: “awaiting_file”}
vip_tag = {
“ar”: f”⭐ اولوية VIP {s[‘vip_level’]} مفعّلة!”,
“fr”: f”⭐ Priorite VIP {s[‘vip_level’]} activee!”,
“en”: f”⭐ VIP {s[‘vip_level’]} priority activated!”,
}.get(lang, “”)
send_file = {
“ar”: “ارسل ملفك:”,
“fr”: “Envoyez votre fichier:”,
“en”: “Send your file:”,
}.get(lang, “”)
bot.edit_message_text(
vip_tag + “\n\n📎 “ + send_file,
cid, call.message.message_id
)
else:
bot.edit_message_text(
T(“print_choice”, lang), cid,
call.message.message_id,
reply_markup=print_choice_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “print_free”)
def cb_print_free(call):
cid  = call.message.chat.id
lang = L(cid)
user_states[cid] = {“step”: “awaiting_file”}
send_file = {
“ar”: “ارسل ملفك:”,
“fr”: “Envoyez votre fichier:”,
“en”: “Send your file:”,
}.get(lang, “”)
bot.edit_message_text(“📎 “ + send_file, cid, call.message.message_id)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_design”)
def cb_design(call):
cid  = call.message.chat.id
lang = L(cid)
user_states[cid] = {“step”: “design_details”}
bot.edit_message_text(
T(“design_intro”, lang), cid,
call.message.message_id,
reply_markup=back_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_edit”)
def cb_edit_project(call):
cid  = call.message.chat.id
lang = L(cid)
user_states[cid] = {“step”: “edit_details”}
bot.edit_message_text(
T(“edit_intro”, lang), cid,
call.message.message_id,
reply_markup=back_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_maquette”)
def cb_maquette(call):
cid  = call.message.chat.id
lang = L(cid)
user_states[cid] = {“step”: “maquette_details”}
text = {
“ar”: “🏗️ <b>ماكيت</b>\n\nارسل تفاصيل الماكيت:\n1 نوع المشروع\n2 المقياس المطلوب\n3 المواد المفضلة\n4 الموعد النهائي”,
“fr”: “🏗️ <b>Maquette</b>\n\nEnvoyez les details:\n1 Type de projet\n2 Echelle souhaitee\n3 Materiaux preferes\n4 Date limite”,
“en”: “🏗️ <b>Maquette</b>\n\nSend details:\n1 Project type\n2 Required scale\n3 Preferred materials\n4 Deadline”,
}.get(lang, “”)
bot.edit_message_text(text, cid, call.message.message_id, reply_markup=back_kb(lang))
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_profile”)
def cb_profile(call):
cid  = call.message.chat.id
lang = L(cid)
s    = db.get_student(cid)
if not s or not s.get(“full_name”):
bot.answer_callback_query(call.id)
return
vip_line = (
f”\n💎 VIP: <b>{s[‘vip_level’]} #{s.get(‘vip_number’, 0):03d}</b>”
if s.get(“vip_level”) else “”
)
edit_label = {“ar”: “✏️ تعديل”, “fr”: “✏️ Modifier”, “en”: “✏️ Edit”}.get(lang, “✏️”)
kb = InlineKeyboardMarkup(row_width=1)
kb.add(
InlineKeyboardButton(edit_label, callback_data=“edit_reg”),
InlineKeyboardButton(T(“btn_back”, lang), callback_data=“back”),
)
bot.edit_message_text(
f”👤 <b>{s.get(‘full_name’, ‘’)}</b>\n”
f”🎓 {s.get(‘specialty’, ‘’)}\n”
f”📅 {s.get(‘year’, ‘’)} | G{s.get(‘group_num’, ‘’)}\n”
f”🚪 {s.get(‘hall’, ‘’)}”
f”{vip_line}\n”
f”🌐 {s.get(‘lang’, ‘ar’).upper()}”,
cid, call.message.message_id, reply_markup=kb
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_card”)
def cb_card(call):
cid  = call.message.chat.id
lang = L(cid)
s    = db.get_student(cid) or {}
num  = s.get(“vip_number”, 0)
card_text = {
“ar”: “هذه البطاقة تمنحك الاولوية في كل طلب! 🔥”,
“fr”: “Cette carte vous donne toujours la priorite! 🔥”,
“en”: “This card always gives you priority! 🔥”,
}.get(lang, “”)
bot.edit_message_text(
f”🪪 <b>GRAVO Timbre VIP Member #{num:03d}</b>\n\n”
f”👤 {s.get(‘full_name’, ‘’)}\n”
f”🎓 {s.get(‘specialty’, ‘’)}\n”
f”💎 {s.get(‘vip_level’, ‘’)}\n”
f”📅 {s.get(‘joined_at’, ‘’)}\n\n”
+ card_text,
cid, call.message.message_id,
reply_markup=back_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “edit_reg”)
def cb_edit_reg(call):
cid  = call.message.chat.id
lang = L(cid)
user_states[cid] = {“step”: “reg_name”, “lang”: lang}
bot.edit_message_text(T(“reg_start”, lang), cid, call.message.message_id)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “back”)
def cb_back(call):
cid  = call.message.chat.id
lang = L(cid)
user_states.pop(cid, None)
bot.edit_message_text(
T(“main_menu”, lang), cid,
call.message.message_id,
reply_markup=main_kb(cid)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(“sp_”))
def cb_specialty(call):
cid   = call.message.chat.id
state = user_states.get(cid, {})
lang  = state.get(“lang”, L(cid))
state[“specialty”] = call.data[3:]
state[“step”]      = “reg_year”
user_states[cid]   = state
bot.edit_message_text(
f”🎓 <b>{state[‘specialty’]}</b>\n\n” + T(“reg_year”, lang),
cid, call.message.message_id,
reply_markup=year_kb()
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(“yr_”))
def cb_year(call):
cid   = call.message.chat.id
state = user_states.get(cid, {})
lang  = state.get(“lang”, L(cid))
state[“year”] = call.data[3:]
state[“step”] = “reg_group”
user_states[cid] = state
bot.edit_message_text(
f”📅 <b>{state[‘year’]}</b>\n\n” + T(“reg_group”, lang),
cid, call.message.message_id
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(“sz_”))
def cb_size(call):
cid   = call.message.chat.id
lang  = L(cid)
state = user_states.get(cid)
if not state:
return
state[“size”] = call.data[3:]
state[“step”] = “awaiting_paper”
choose_paper = {
“ar”: “اختر نوع الورق:”,
“fr”: “Choisissez le papier:”,
“en”: “Choose paper type:”,
}.get(lang, “”)
bot.edit_message_text(
f”📏 <b>{state[‘size’]}</b>\n\n” + choose_paper,
cid, call.message.message_id,
reply_markup=paper_kb(state[“size”], lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(“pp_”))
def cb_paper(call):
cid   = call.message.chat.id
lang  = L(cid)
state = user_states.get(cid)
if not state:
return
parts = call.data.split(”_”, 2)
label = parts[1] if len(parts) > 1 else “?”
price = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
state.update({“paper”: label, “unit_price”: price, “step”: “awaiting_copies”})
p = f”{price} da” if price else “Prix special”
copies_text = {
“ar”: “كم نسخة؟”,
“fr”: “Combien de copies?”,
“en”: “How many copies?”,
}.get(lang, “”)
bot.edit_message_text(
f”📄 {label} - {p}\n\n” + copies_text,
cid, call.message.message_id,
reply_markup=copies_kb()
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(“cp_”))
def cb_copies(call):
cid    = call.message.chat.id
lang   = L(cid)
state  = user_states.get(cid)
if not state:
return
copies = int(call.data[3:])
up     = state.get(“unit_price”, 0)
total  = f”{up * copies} da” if up else {
“ar”: “سيحدد”, “fr”: “A determiner”, “en”: “TBD”
}.get(lang, “”)
state.update({“copies”: copies, “price”: total, “step”: “awaiting_confirm”})
s = db.get_student(cid) or {}
vip_tag = f”\n⭐ VIP {s[‘vip_level’]}!” if s.get(“vip_level”) else “”
summary = {
“ar”: “📋 <b>ملخص الطلب</b>”,
“fr”: “📋 <b>Resume</b>”,
“en”: “📋 <b>Order Summary</b>”,
}.get(lang, “”)
confirm_text = {
“ar”: “هل تؤكد؟”,
“fr”: “Confirmez-vous?”,
“en”: “Do you confirm?”,
}.get(lang, “”)
bot.edit_message_text(
summary + vip_tag + f”\n\n”
f”📄 <code>{state[‘filename’]}</code>\n”
f”📏 {state[‘size’]} | {state[‘paper’]}\n”
f”🔢 {copies}x | 💰 {total}\n\n”
+ confirm_text,
cid, call.message.message_id,
reply_markup=confirm_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “ok_print”)
def cb_confirm(call):
cid   = call.message.chat.id
lang  = L(cid)
state = user_states.pop(cid, None)
if not state:
return
s   = db.get_student(cid) or {}
oid = db.add_order(
cid, “print”,
state[“filename”],
state[“size”],
state[“paper”],
state[“copies”],
state[“price”]
)
received_text = {
“ar”: “تم استلام طلبك! ✅”,
“fr”: “Commande recue! ✅”,
“en”: “Order received! ✅”,
}.get(lang, “”)
bot.edit_message_text(
f”🖨️ <b>{received_text}</b>\n”
f”📄 {state[‘filename’]} | {state[‘size’]} | {state[‘copies’]}x | {state[‘price’]}”,
cid, call.message.message_id
)
if not s.get(“vip_level”):
bot.send_message(cid, T(“vip_push”, lang), reply_markup=vip_push_kb(lang))
else:
vip_ok = {
“ar”: “طلبك له اولوية VIP! 🔥”,
“fr”: “Priorite VIP! 🔥”,
“en”: “VIP priority! 🔥”,
}.get(lang, “”)
bot.send_message(cid, f”✅ {vip_ok}”, reply_markup=main_kb(cid))

```
vip_tag = f"💎 {s['vip_level']}" if s.get("vip_level") else "🟢 Free"
notify_admin(
    f"🖨️ <b>#{oid}</b> {vip_tag}\n"
    f"👤 {s.get('full_name', '?')} | {s.get('specialty', '?')} | G{s.get('group_num', '?')}\n"
    f"📏 {state['size']} | {state['paper']} | {state['copies']}x | {state['price']}\n"
    f"📄 {state['filename']}"
)
bot.answer_callback_query(call.id)
```

@bot.callback_query_handler(func=lambda c: c.data == “cancel”)
def cb_cancel(call):
cid  = call.message.chat.id
lang = L(cid)
user_states.pop(cid, None)
cancelled = {
“ar”: “تم الالغاء.”,
“fr”: “Annule.”,
“en”: “Cancelled.”,
}.get(lang, “”)
bot.edit_message_text(
f”❌ {cancelled}”, cid,
call.message.message_id,
reply_markup=main_kb(cid)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “back_size”)
def cb_back_size(call):
cid  = call.message.chat.id
lang = L(cid)
choose_size = {
“ar”: “اختر الحجم:”,
“fr”: “Choisissez la taille:”,
“en”: “Choose size:”,
}.get(lang, “”)
bot.edit_message_text(
f”📏 {choose_size}”, cid,
call.message.message_id,
reply_markup=size_kb(lang)
)
bot.answer_callback_query(call.id)

# ══════════════════════════════════════════════════════════════

# استقبال الملفات

# ══════════════════════════════════════════════════════════════

@bot.message_handler(content_types=[“document”, “photo”])
def handle_file(msg):
cid  = msg.chat.id
lang = L(cid)
s    = db.get_student(cid)

```
if not s or not s.get("full_name"):
    not_reg = {
        "ar": "سجّل اولا! /start",
        "fr": "Inscrivez-vous d'abord! /start",
        "en": "Register first! /start",
    }.get(lang, "")
    bot.send_message(cid, not_reg)
    return

state = user_states.get(cid, {})
step  = state.get("step", "")

if msg.content_type == "document":
    fname = msg.document.file_name or f"file_{int(time.time())}"
    ext   = Path(fname).suffix.lower()
    fsize = msg.document.file_size / (1024 * 1024)
else:
    fname = f"photo_{int(time.time())}.jpg"
    ext   = ".jpg"
    fsize = msg.photo[-1].file_size / (1024 * 1024)

if step.startswith("qs_"):
    oid = db.add_order(cid, step, fname, details=step[3:])
    user_states.pop(cid, None)
    bot.send_message(cid, T("quick_received", lang), reply_markup=main_kb(cid))
    notify_admin(
        f"⚡ <b>Service rapide #{oid}</b>\n"
        f"👤 {s.get('full_name', '?')}\n"
        f"📄 {fname} | {step[3:]}"
    )
    return

if step == "edit_details":
    user_states[cid] = {**state, "filename": fname, "step": "edit_text"}
    file_received = {
        "ar": f"✅ استلم: <code>{fname}</code>\n\nالان ارسل التعديلات المطلوبة:",
        "fr": f"✅ Recu: <code>{fname}</code>\n\nEnvoyez maintenant les modifications:",
        "en": f"✅ Received: <code>{fname}</code>\n\nNow send the required edits:",
    }.get(lang, "")
    bot.send_message(cid, file_received)
    return

if ext not in [".pdf", ".jpg", ".jpeg", ".png"]:
    unsupported = {
        "ar": f"الصيغة {ext} غير مدعومة.",
        "fr": f"Format {ext} non supporte.",
        "en": f"Format {ext} not supported.",
    }.get(lang, "")
    bot.send_message(cid, f"⚠️ {unsupported}")
    return

if fsize > 50:
    too_big = {
        "ar": f"الملف كبير ({fsize:.1f} MB). الحد 50 MB.",
        "fr": f"Fichier trop grand ({fsize:.1f} MB). Limite 50 MB.",
        "en": f"File too large ({fsize:.1f} MB). Limit 50 MB.",
    }.get(lang, "")
    bot.send_message(cid, f"❌ {too_big}")
    return

vip_tag = f"\n⭐ VIP {s['vip_level']}!" if s.get("vip_level") else ""
user_states[cid] = {"step": "awaiting_size", "filename": fname}

file_ok = {
    "ar": f"✅ استُلم الملف{vip_tag}\n📄 <code>{fname}</code>\n\nاختر الحجم:",
    "fr": f"✅ Fichier recu{vip_tag}\n📄 <code>{fname}</code>\n\nChoisissez la taille:",
    "en": f"✅ File received{vip_tag}\n📄 <code>{fname}</code>\n\nChoose size:",
}.get(lang, "")

bot.send_message(cid, file_ok, reply_markup=size_kb(lang))
```

# ══════════════════════════════════════════════════════════════

# الرسائل النصية

# ══════════════════════════════════════════════════════════════

@bot.message_handler(func=lambda m: True)
def handle_text(msg):
cid   = msg.chat.id
text  = msg.text or “”
lang  = L(cid)
state = user_states.get(cid, {})
step  = state.get(“step”, “”)

```
if step in ["reg_name", "reg_group", "reg_hall"]:
    handle_registration(msg)
    return

if step == "sub_email":
    s   = db.get_student(cid) or {}
    oid = db.add_order(
        cid, "subscription",
        details=f"{state.get('sub_item', '')} | {text}"
    )
    user_states.pop(cid, None)
    bot.send_message(cid, T("sub_received", lang), reply_markup=main_kb(cid))
    notify_admin(
        f"💳 <b>Abonnement #{oid}</b>\n"
        f"👤 {s.get('full_name', '?')}\n"
        f"📦 {state.get('sub_item', '?')}\n"
        f"📧 {text}"
    )
    return

if step == "design_details":
    s   = db.get_student(cid) or {}
    oid = db.add_order(cid, "design", details=text)
    user_states.pop(cid, None)
    bot.send_message(cid, T("order_received", lang), reply_markup=main_kb(cid))
    notify_admin(
        f"📐 <b>Design #{oid}</b>\n"
        f"👤 {s.get('full_name', '?')} | {s.get('specialty', '?')}\n"
        f"📝 {text}"
    )
    return

if step == "edit_text":
    s   = db.get_student(cid) or {}
    oid = db.add_order(cid, "edit", state.get("filename", ""), details=text)
    user_states.pop(cid, None)
    bot.send_message(cid, T("order_received", lang), reply_markup=main_kb(cid))
    notify_admin(
        f"✏️ <b>Edition #{oid}</b>\n"
        f"👤 {s.get('full_name', '?')}\n"
        f"📄 {state.get('filename', '?')}\n"
        f"📝 {text}"
    )
    return

if step == "maquette_details":
    s   = db.get_student(cid) or {}
    oid = db.add_order(cid, "maquette", details=text)
    user_states.pop(cid, None)
    bot.send_message(cid, T("order_received", lang), reply_markup=main_kb(cid))
    notify_admin(
        f"🏗️ <b>Maquette #{oid}</b>\n"
        f"👤 {s.get('full_name', '?')}\n"
        f"📝 {text}"
    )
    return

if step == "awaiting_file":
    bot.send_message(cid, T("send_file_first", lang))
    return

db.save_student(cid, last_seen=datetime.now().strftime("%Y-%m-%d %H:%M"))
thinking_text = {"ar": "💭 ...", "fr": "💭 ...", "en": "💭 ..."}.get(lang, "💭 ...")
thinking = bot.send_message(cid, thinking_text)
reply    = ask_ai(cid, text)
bot.delete_message(cid, thinking.message_id)
bot.send_message(cid, reply, reply_markup=main_kb(cid))
```

# ══════════════════════════════════════════════════════════════

# الأدمن

# ══════════════════════════════════════════════════════════════

def notify_admin(text):
for aid in ADMIN_IDS:
try:
bot.send_message(aid, text)
except Exception:
pass

def is_admin(msg):
return msg.from_user.id in ADMIN_IDS

@bot.message_handler(commands=[“stats”], func=is_admin)
def cmd_stats(msg):
s = db.stats()
bot.send_message(
msg.chat.id,
f”📊 <b>GRAVO Statistics</b>\n\n”
f”👥 Etudiants: <b>{s[‘students’]}</b>\n”
f”💎 VIP: <b>{s[‘vips’]}</b>\n”
f”📬 Commandes: <b>{s[‘orders’]}</b>\n”
f”⏳ En attente: <b>{s[‘pending’]}</b>”
)

@bot.message_handler(commands=[“addvip”], func=is_admin)
def cmd_addvip(msg):
parts = msg.text.split()
if len(parts) < 3:
bot.send_message(msg.chat.id, “/addvip <chat_id> <Bronze|Silver|Gold|Platinum>”)
return
cid   = int(parts[1])
level = parts[2]
num   = db.add_vip(cid, level)
bot.send_message(msg.chat.id, f”✅ VIP #{num:03d} - {level}”)
try:
lang = db.get_lang(cid)
congrats = {
“ar”: f”مبروك! انت الان عضو GRAVO VIP {level}!\nرقم العضوية #{num:03d}\nمزاياك فعّالة الان 🔥”,
“fr”: f”Felicitations! Vous etes maintenant membre GRAVO VIP {level}!\nMembre #{num:03d}\nVos avantages sont actifs 🔥”,
“en”: f”Congrats! You are now GRAVO VIP {level}!\nMember #{num:03d}\nYour benefits are now active 🔥”,
}.get(lang, “”)
bot.send_message(cid, f”🎉 <b>{congrats}</b>”, reply_markup=main_kb(cid))
except Exception:
pass

@bot.message_handler(commands=[“students”], func=is_admin)
def cmd_students(msg):
cur = db.conn.execute(
“SELECT full_name, specialty, year, group_num, lang, vip_level “
“FROM students ORDER BY joined_at DESC LIMIT 10”
)
rows = cur.fetchall()
if not rows:
bot.send_message(msg.chat.id, “Aucun etudiant encore.”)
return
lines = [”<b>👥 10 derniers etudiants:</b>\n”]
for r in rows:
vip = f” 💎{r[5]}” if r[5] else “”
lines.append(f”• {r[0]} | {r[1]} | {r[2]} | G{r[3]} | {r[4].upper()}{vip}”)
bot.send_message(msg.chat.id, “\n”.join(lines))

# ══════════════════════════════════════════════════════════════

# Flask

# ══════════════════════════════════════════════════════════════

app = Flask(**name**)

@app.route(”/”)
def index():
return “GRAVO Bot v3.0 - Groq Edition - Running!”

@app.route(”/health”)
def health():
return {“status”: “ok”, “version”: “3.0”, “ai”: “groq”}

def run_flask():
port = int(os.environ.get(“PORT”, 8080))
app.run(host=“0.0.0.0”, port=port)

# ══════════════════════════════════════════════════════════════

if **name** == “**main**”:
log.info(“GRAVO Bot v3.0 - Groq Edition”)
threading.Thread(target=run_flask, daemon=True).start()
bot.infinity_polling(timeout=30, long_polling_timeout=15)
