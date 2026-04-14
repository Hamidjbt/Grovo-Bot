“””
╔══════════════════════════════════════════════════════════════╗
║              GRAVO Bot v3.0 — النسخة الكاملة               ║
║  ✅ 3 لغات كاملة    ✅ هيكل 5 أقسام                        ║
║  ✅ اشتراكات + باقات ✅ VIP System                          ║
║  ✅ Claude AI 3-step ✅ Render.com                          ║
╚══════════════════════════════════════════════════════════════╝

📌 كل التعديلات المستقبلية في القسم أدناه فقط
لا تحتاج تبحث في الكود — كل شيء في مكانه
“””

import os, time, logging, sqlite3
import threading, requests
from datetime import datetime
from pathlib import Path
from flask import Flask

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ╔══════════════════════════════════════════════════════════════╗

# ║          ✏️  منطقة التعديل — عدّل هنا فقط                 ║

# ╚══════════════════════════════════════════════════════════════╝

# ── إعدادات البوت ─────────────────────────────────────────────

BOT_TOKEN         = os.environ.get(“BOT_TOKEN”, “ضع_TOKEN_هنا”)
ADMIN_IDS         = list(map(int, os.environ.get(“ADMIN_IDS”, “123456789”).split(”,”)))
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
WHATSAPP          = “213668338569”
TELEGRAM_ADMIN    = “HamidBnc”

# ── معلومات المحل ──────────────────────────────────────────────

SHOP = {
“name”:    “GRAVO”,
“version”: “v1.0”,
“address”: “Université Abou Bekr Belkaïd — Département Architecture, Chetouane, Tlemcen”,
“phone”:   “06 68 33 85 69”,
“hours”: {
“ar”: {
“الأحد → الخميس”: “07:15 → 17:00”,
“الجمعة”:         “🔴 مغلق”,
“السبت”:          “⚡ بطلب مسبق فقط”,
},
“fr”: {
“Dim → Jeu”: “07:15 → 17:00”,
“Vendredi”:  “🔴 Fermé”,
“Samedi”:    “⚡ Sur demande uniquement”,
},
“en”: {
“Sun → Thu”: “07:15 → 17:00”,
“Friday”:    “🔴 Closed”,
“Saturday”:  “⚡ By prior request only”,
},
},
“saturday”: {
“ar”: (
“يوم السبت يتطلب إذن مسبق:\n”
“1️⃣ تقدم بطلب خطي لمسؤول الطلاب\n”
“2️⃣ المسؤول يوصله للإدارة\n”
f”📞 تواصل معنا: 06 68 33 85 69”
),
“fr”: (
“Le samedi nécessite une autorisation préalable :\n”
“1️⃣ Soumettez une demande écrite au responsable\n”
“2️⃣ Le responsable la transmet à l’administration\n”
f”📞 Contactez-nous : 06 68 33 85 69”
),
“en”: (
“Saturday requires prior authorization:\n”
“1️⃣ Submit a written request to the student officer\n”
“2️⃣ Officer forwards it to administration\n”
f”📞 Contact us: 06 68 33 85 69”
),
},
“affichage”: {
“ar”: “🚨 أيام Affichage: المحل مفتوح بدون توقف!”,
“fr”: “🚨 Jours Affichage : La boutique est ouverte sans interruption !”,
“en”: “🚨 Affichage days: Shop open non-stop!”,
},
}

# ── أسعار الطباعة ──────────────────────────────────────────────

PRICES = {
“A4”: {
“📄 Papier normal”:   10,
“🖼️ Papier Photo”:   50,
“🏷️ Autocollants”:   50,
},
“A3”: {
“🌈 Couleur”:         50,
“⬛ Noir & Blanc”:    30,
},
“A2”: {
“🌈 Couleur”:        100,
“⬛ Noir & Blanc”:    70,
“🖼️ Papier Photo”:    0,   # ← سيُحدَّد
},
“A1”: {
“🌈 Couleur”:        200,
“⬛ Noir & Blanc”:   150,
“🖼️ Papier Photo”:    0,   # ← سيُحدَّد
},
“A0”: {
“🌈 Couleur HQ”:     350,
“⬛ Noir & Blanc”:   300,
},
}

# ── الاشتراكات الفردية ─────────────────────────────────────────

SUBSCRIPTIONS = {
“ChatGPT”:          {“price”: 800,  “emoji”: “🤖”, “desc”: {“ar”: “ذكاء اصطناعي”, “fr”: “IA générative”, “en”: “Generative AI”}},
“Gemini Pro”:       {“price”: 900,  “emoji”: “✨”, “desc”: {“ar”: “ذكاء Google”, “fr”: “IA Google”, “en”: “Google AI”}},
“Canva Pro”:        {“price”: 750,  “emoji”: “🎨”, “desc”: {“ar”: “تصميم احترافي”, “fr”: “Design pro”, “en”: “Pro design”}},
“CapCut Pro”:       {“price”: 1000, “emoji”: “🎬”, “desc”: {“ar”: “مونتاج فيديو”, “fr”: “Montage vidéo”, “en”: “Video editing”}},
“YouTube Premium”:  {“price”: 1000, “emoji”: “▶️”, “desc”: {“ar”: “بدون إعلانات”, “fr”: “Sans publicités”, “en”: “Ad-free”}},
“Netflix”:          {“price”: 1500, “emoji”: “🎥”, “desc”: {“ar”: “أفلام ومسلسلات”, “fr”: “Films & séries”, “en”: “Movies & series”}},
“Disney+”:          {“price”: 1200, “emoji”: “🏰”, “desc”: {“ar”: “ترفيه عائلي”, “fr”: “Divertissement famille”, “en”: “Family entertainment”}},
}

# ── الباقات ────────────────────────────────────────────────────

# لتعديل باقة: غيّر name / items / price / desc

PACKS = {
“student_pack”: {
“name”:  “🔥 Student Pack”,
“items”: [“Canva Pro”, “ChatGPT”],
“price”: 1200,   # ← السعر بعد الخصم
“full”:  1550,   # ← السعر الكامل (للعرض)
“desc”: {
“ar”: “الثنائي المثالي لكل طالب”,
“fr”: “Le duo parfait pour chaque étudiant”,
“en”: “The perfect duo for every student”,
},
},
“ai_comparison”: {
“name”:  “🎯 AI Comparison Pack”,
“items”: [“ChatGPT”, “Gemini Pro”],
“price”: 1350,
“full”:  1700,
“desc”: {
“ar”: “قارن بين أقوى نموذجين AI”,
“fr”: “Comparez les 2 meilleurs modèles AI”,
“en”: “Compare the 2 strongest AI models”,
},
},
“power_ai”: {
“name”:  “⚡ Power AI Pack”,
“items”: [“ChatGPT”, “Gemini Pro”, “Canva Pro”],
“price”: 1900,
“full”:  2450,
“desc”: {
“ar”: “ثلاثي الذكاء والإبداع”,
“fr”: “Le trio intelligence & créativité”,
“en”: “The AI & creativity trio”,
},
},
“content_creator”: {
“name”:  “🎬 Content Creator Pack”,
“items”: [“Canva Pro”, “CapCut Pro”, “YouTube Premium”],
“price”: 2100,
“full”:  2750,
“desc”: {
“ar”: “كل ما يحتاجه صانع المحتوى”,
“fr”: “Tout ce qu’il faut pour créer du contenu”,
“en”: “Everything a content creator needs”,
},
},
“entertainment”: {
“name”:  “🍿 Entertainment Pack”,
“items”: [“Netflix”, “Disney+”, “YouTube Premium”],
“price”: 2800,
“full”:  3700,
“desc”: {
“ar”: “ترفيه بلا حدود”,
“fr”: “Divertissement sans limites”,
“en”: “Unlimited entertainment”,
},
},
“ultimate_ai”: {
“name”:  “🚀 Ultimate AI Pack”,
“items”: [“ChatGPT”, “Gemini Pro”, “Canva Pro”, “CapCut Pro”],
“price”: 2600,
“full”:  3450,
“desc”: {
“ar”: “الحزمة الاحترافية الكاملة”,
“fr”: “Le pack professionnel complet”,
“en”: “The complete professional pack”,
},
},
“all_in_one”: {
“name”:  “⚡ All In One”,
“items”: [“ChatGPT”, “Gemini Pro”, “Canva Pro”, “CapCut Pro”, “YouTube Premium”, “Netflix”, “Disney+”],
“price”: 5000,
“full”:  7150,
“desc”: {
“ar”: “كل الخدمات في مكان واحد”,
“fr”: “Tous les services en un seul endroit”,
“en”: “All services in one place”,
},
},
“vip_access”: {
“name”:  “💎 VIP Access”,
“items”: [“ChatGPT”, “Gemini Pro”, “Canva Pro”, “CapCut Pro”, “YouTube Premium”, “Netflix”, “Disney+”],
“price”: 6000,
“full”:  None,   # لا يعرض سعر كامل
“desc”: {
“ar”: “All In One + عضوية VIP GRAVO”,
“fr”: “All In One + Membre VIP GRAVO”,
“en”: “All In One + GRAVO VIP Membership”,
},
},
}

# ── مستويات VIP ────────────────────────────────────────────────

VIP_LEVELS = {
“🥉 Bronze”: {
“ar”: [“أولوية بسيطة في الطلبات”, “تعديل واحد لكل مشروع”, “وصول للقوالب”, “بطاقة GRAVO VIP”],
“fr”: [“Priorité simple”, “1 modification par projet”, “Accès aux modèles”, “Carte GRAVO VIP”],
“en”: [“Basic priority”, “1 edit per project”, “Template access”, “GRAVO VIP card”],
},
“🥈 Silver”: {
“ar”: [“كل مزايا Bronze”, “تعديلات غير محدودة”, “خصم 10%”, “محتوى حصري”, “استشارة عبر الخاص”],
“fr”: [“Tout Bronze”, “Modifications illimitées”, “Réduction 10%”, “Contenu exclusif”, “Consultation directe”],
“en”: [“All Bronze”, “Unlimited edits”, “10% discount”, “Exclusive content”, “Direct consultation”],
},
“🥇 Gold”: {
“ar”: [“كل مزايا Silver”, “إرشاد شخصي لكل مشروع”, “مشاريع جاهزة VIP”, “أولوية قصوى”, “طباعة Premium”],
“fr”: [“Tout Silver”, “Accompagnement personnel”, “Projets VIP prêts”, “Priorité maximale”, “Impression Premium”],
“en”: [“All Silver”, “Personal guidance”, “Ready VIP projects”, “Max priority”, “Premium printing”],
},
“💎 Platinum”: {
“ar”: [“كل مزايا Gold”, “دعم مستمر 24/7”, “تواصل مباشر مع الإدارة”, “شهادة VIP”, “هدايا دورية”, “طباعة Ultra Premium”],
“fr”: [“Tout Gold”, “Support 24/7”, “Contact direct direction”, “Certificat VIP”, “Cadeaux périodiques”, “Ultra Premium”],
“en”: [“All Gold”, “24/7 support”, “Direct admin contact”, “VIP certificate”, “Periodic gifts”, “Ultra Premium printing”],
},
}

# ── التخصصات ───────────────────────────────────────────────────

SPECIALTIES = [
“🏛️ هندسة معمارية”,
“⚡ هندسة كهربائية”,
“⚙️ هندسة ميكانيكية”,
“📚 تخصص آخر”,
]

# ╔══════════════════════════════════════════════════════════════╗

# ║          🌐 النصوص بـ 3 لغات — عدّل هنا                   ║

# ╚══════════════════════════════════════════════════════════════╝

MESSAGES = {
# ── اختيار اللغة ──────────────────────────────────────────
“choose_lang”: “🌐 Choose your language / اختر لغتك / Choisissez votre langue”,

```
# ── ترحيب ─────────────────────────────────────────────────
"welcome": {
    "ar": (
        "🔥 <b>مرحباً بك في GRAVO Community v1.0</b>\n\n"
        "نظام احترافي مصمم لطالب الهندسة.\n"
        "لا انتظار. لا تشويش. نتائج فقط.\n\n"
        "🎯 اختر ما تحتاجه:"
    ),
    "fr": (
        "🔥 <b>Bienvenue dans GRAVO Community v1.0</b>\n\n"
        "Un système professionnel conçu pour l'étudiant en ingénierie.\n"
        "Pas d'attente. Pas de confusion. Résultats uniquement.\n\n"
        "🎯 Choisissez ce dont vous avez besoin :"
    ),
    "en": (
        "🔥 <b>Welcome to GRAVO Community v1.0</b>\n\n"
        "A professional system built for engineering students.\n"
        "No waiting. No confusion. Results only.\n\n"
        "🎯 Choose what you need:"
    ),
},

# ── التسجيل ───────────────────────────────────────────────
"reg_start": {
    "ar": "👋 <b>أهلاً بك في GRAVO!</b>\n\nسجّل معلوماتك مرة واحدة فقط ✍️\nوسيتذكرك البوت دائماً!\n\n📝 <b>ما اسمك الكامل؟</b>",
    "fr": "👋 <b>Bienvenue dans GRAVO !</b>\n\nEnregistrez vos informations une seule fois ✍️\nLe bot se souviendra de vous !\n\n📝 <b>Quel est votre nom complet ?</b>",
    "en": "👋 <b>Welcome to GRAVO!</b>\n\nRegister your info once ✍️\nThe bot will always remember you!\n\n📝 <b>What is your full name?</b>",
},
"reg_specialty": {
    "ar": "🎓 <b>ما تخصصك؟</b>",
    "fr": "🎓 <b>Quelle est votre spécialité ?</b>",
    "en": "🎓 <b>What is your specialty?</b>",
},
"reg_year": {
    "ar": "📅 <b>ما سنتك الدراسية؟</b>",
    "fr": "📅 <b>Quelle est votre année d'étude ?</b>",
    "en": "📅 <b>What is your academic year?</b>",
},
"reg_group": {
    "ar": "👥 <b>رقم groupك؟</b>\n<i>(مثال: G1, G2...)</i>",
    "fr": "👥 <b>Votre numéro de groupe ?</b>\n<i>(ex: G1, G2...)</i>",
    "en": "👥 <b>Your group number?</b>\n<i>(e.g. G1, G2...)</i>",
},
"reg_hall": {
    "ar": "🚪 <b>رقم القاعة أو المدرج؟</b>\n<i>(مثال: Amphi A, Salle 12)</i>",
    "fr": "🚪 <b>Numéro de salle ou amphithéâtre ?</b>\n<i>(ex: Amphi A, Salle 12)</i>",
    "en": "🚪 <b>Hall or lecture room number?</b>\n<i>(e.g. Amphi A, Room 12)</i>",
},
"reg_done": {
    "ar": "✅ <b>تم التسجيل!</b>\n\nالبوت سيتذكرك دائماً 🤖",
    "fr": "✅ <b>Inscription réussie !</b>\n\nLe bot se souviendra toujours de vous 🤖",
    "en": "✅ <b>Registration complete!</b>\n\nThe bot will always remember you 🤖",
},

# ── القائمة الرئيسية ───────────────────────────────────────
"main_menu": {
    "ar": "📋 القائمة الرئيسية:",
    "fr": "📋 Menu principal :",
    "en": "📋 Main menu:",
},

# ── أزرار القائمة ─────────────────────────────────────────
"btn_student":  {"ar": "🎓 خدمات الطلبة",   "fr": "🎓 Services étudiants", "en": "🎓 Student Services"},
"btn_quick":    {"ar": "⚡ خدمات سريعة",    "fr": "⚡ Services rapides",    "en": "⚡ Quick Services"},
"btn_subs":     {"ar": "💳 الاشتراكات",      "fr": "💳 Abonnements",         "en": "💳 Subscriptions"},
"btn_vip":      {"ar": "👑 VIP",              "fr": "👑 VIP",                 "en": "👑 VIP"},
"btn_assistant":{"ar": "🤖 مساعد Gravo",     "fr": "🤖 Assistant Gravo",     "en": "🤖 Gravo Assistant"},
"btn_back":     {"ar": "↩️ رجوع",            "fr": "↩️ Retour",              "en": "↩️ Back"},
"btn_profile":  {"ar": "👤 ملفي",            "fr": "👤 Mon profil",           "en": "👤 My profile"},
"btn_prices":   {"ar": "💰 الأسعار",          "fr": "💰 Tarifs",              "en": "💰 Prices"},
"btn_hours":    {"ar": "🕐 المواعيد",         "fr": "🕐 Horaires",            "en": "🕐 Hours"},
"btn_orders":   {"ar": "📦 طلباتي",           "fr": "📦 Mes commandes",        "en": "📦 My orders"},
"btn_contact":  {"ar": "📞 تواصل معنا",       "fr": "📞 Nous contacter",       "en": "📞 Contact us"},
"btn_whatsapp": {"ar": "💬 واتساب",           "fr": "💬 WhatsApp",             "en": "💬 WhatsApp"},
"btn_telegram": {"ar": "✈️ تيليغرام",        "fr": "✈️ Telegram",            "en": "✈️ Telegram"},
"btn_confirm":  {"ar": "✅ تأكيد",            "fr": "✅ Confirmer",            "en": "✅ Confirm"},
"btn_cancel":   {"ar": "❌ إلغاء",            "fr": "❌ Annuler",              "en": "❌ Cancel"},
"btn_free":     {"ar": "🟢 متابعة عادي",     "fr": "🟢 Continuer normal",    "en": "🟢 Continue normal"},
"btn_upgrade":  {"ar": "💎 الترقية إلى VIP", "fr": "💎 Passer au VIP",       "en": "💎 Upgrade to VIP"},
"btn_vip_now":  {"ar": "⚡ VIP الآن",         "fr": "⚡ VIP maintenant",       "en": "⚡ VIP now"},
"btn_join_vip": {"ar": "✅ أريد الانضمام",    "fr": "✅ Je veux rejoindre",    "en": "✅ I want to join"},
"btn_lang":     {"ar": "🌐 تغيير اللغة",     "fr": "🌐 Changer la langue",    "en": "🌐 Change language"},

# ── خدمات الطلبة ──────────────────────────────────────────
"btn_print":    {"ar": "🖨️ طباعة",           "fr": "🖨️ Impression",          "en": "🖨️ Printing"},
"btn_design":   {"ar": "📐 تصميم مشروع",     "fr": "📐 Conception projet",    "en": "📐 Project design"},
"btn_edit":     {"ar": "✏️ تعديل مشروع",     "fr": "✏️ Modification projet",  "en": "✏️ Project editing"},
"btn_maquette": {"ar": "🏗️ ماكيت",           "fr": "🏗️ Maquette",            "en": "🏗️ Maquette"},

# ── خدمات سريعة ───────────────────────────────────────────
"btn_convert":  {"ar": "🔄 تحويل PDF↔PNG",   "fr": "🔄 Convertir PDF↔PNG",   "en": "🔄 Convert PDF↔PNG"},
"btn_fix":      {"ar": "🔧 تصحيح ملف",       "fr": "🔧 Corriger fichier",     "en": "🔧 Fix file"},
"btn_imgfix":   {"ar": "🖼️ تعديل صورة",     "fr": "🖼️ Modifier image",       "en": "🖼️ Edit image"},

# ── الطباعة ───────────────────────────────────────────────
"print_choice": {
    "ar": (
        "🖨️ <b>طلب الطباعة</b>\n\n"
        "🟢 <b>الوضع العادي:</b>\n"
        "  • تنفيذ حسب الضغط الحالي\n"
        "  • بدون أولوية\n\n"
        "💎 <b>VIP:</b>\n"
        "  • تنفيذ سريع\n"
        "  • أولوية مباشرة\n"
        "  • جودة Premium\n\n"
        "🎯 ماذا تريد الآن؟"
    ),
    "fr": (
        "🖨️ <b>Demande d'impression</b>\n\n"
        "🟢 <b>Mode normal :</b>\n"
        "  • Exécution selon la charge\n"
        "  • Sans priorité\n\n"
        "💎 <b>VIP :</b>\n"
        "  • Exécution rapide\n"
        "  • Priorité immédiate\n"
        "  • Qualité Premium\n\n"
        "🎯 Que voulez-vous maintenant ?"
    ),
    "en": (
        "🖨️ <b>Print Request</b>\n\n"
        "🟢 <b>Normal mode:</b>\n"
        "  • Execution based on current load\n"
        "  • No priority\n\n"
        "💎 <b>VIP:</b>\n"
        "  • Fast execution\n"
        "  • Immediate priority\n"
        "  • Premium quality\n\n"
        "🎯 What do you want now?"
    ),
},

# ── Push VIP بعد الطلب ─────────────────────────────────────
"vip_push": {
    "ar": (
        "⏳ <b>طلبك قيد التنفيذ حسب الضغط الحالي.</b>\n\n"
        "💎 تريد أولوية؟\n"
        "اضغط <b>VIP</b> الآن واحصل على:\n"
        "• تنفيذ فوري\n"
        "• جودة أعلى\n"
        "• دعم مباشر\n\n"
        "⏰ الطلب عالي — VIP يحصل على أولوية!"
    ),
    "fr": (
        "⏳ <b>Votre commande est en cours selon la charge actuelle.</b>\n\n"
        "💎 Vous voulez la priorité ?\n"
        "Appuyez sur <b>VIP</b> maintenant :\n"
        "• Exécution immédiate\n"
        "• Meilleure qualité\n"
        "• Support direct\n\n"
        "⏰ Forte demande — VIP obtient la priorité !"
    ),
    "en": (
        "⏳ <b>Your order is being processed based on current load.</b>\n\n"
        "💎 Want priority?\n"
        "Press <b>VIP</b> now and get:\n"
        "• Instant execution\n"
        "• Higher quality\n"
        "• Direct support\n\n"
        "⏰ High demand — VIP gets priority!"
    ),
},

# ── خطأ في الملف + Push VIP ────────────────────────────────
"file_error_vip": {
    "ar": (
        "⚠️ <b>تم اكتشاف مشكلة في الملف</b>\n\n"
        "المقاسات أو المعلومات غير صحيحة للطباعة.\n"
        "لكن لا تقلق! 🚀\n\n"
        "🔹 تصحيح الأخطاء متاح فقط لأعضاء VIP\n\n"
        "💎 ادخل الآن واستفد من:\n"
        "✔ تصحيح فوري لكل الأخطاء\n"
        "✔ دعم مباشر ومتابعة دقيقة\n"
        "✔ أولوية في التنفيذ وسرعة عالية\n\n"
        "📌 اضغط هنا للانضمام إلى VIP!"
    ),
    "fr": (
        "⚠️ <b>Problème détecté dans votre fichier</b>\n\n"
        "Dimensions ou informations incorrectes.\n"
        "Mais pas d'inquiétude ! 🚀\n\n"
        "🔹 La correction est disponible uniquement pour les membres VIP\n\n"
        "💎 Rejoignez VIP maintenant :\n"
        "✔ Correction immédiate de toutes les erreurs\n"
        "✔ Support direct et suivi détaillé\n"
        "✔ Priorité d'exécution et rapidité\n\n"
        "📌 Cliquez ici pour rejoindre VIP !"
    ),
    "en": (
        "⚠️ <b>Issue detected in your file</b>\n\n"
        "Dimensions or information are incorrect.\n"
        "But don't worry! 🚀\n\n"
        "🔹 Error correction is available exclusively for VIP members\n\n"
        "💎 Join VIP now and enjoy:\n"
        "✔ Instant correction of all errors\n"
        "✔ Direct support and detailed follow-up\n"
        "✔ Priority execution and faster delivery\n\n"
        "📌 Click here to join VIP!"
    ),
},

# ── VIP Flow ───────────────────────────────────────────────
"vip_intro": {
    "ar": (
        "👑 <b>GRAVO VIP</b>\n\n"
        "تهانينا، أنت على وشك الدخول لمستوى مختلف.\n\n"
        "⚡ تنفيذ سريع\n"
        "⚡ أولوية كاملة\n"
        "⚡ محتوى وخدمات متقدمة\n\n"
        "⏰ <b>الأماكن محدودة!</b>\n"
        "الفائزون يتصرفون الآن.\n\n"
        "اختر مستواك:"
    ),
    "fr": (
        "👑 <b>GRAVO VIP</b>\n\n"
        "Félicitations, vous êtes sur le point d'entrer dans un niveau différent.\n\n"
        "⚡ Exécution rapide\n"
        "⚡ Priorité complète\n"
        "⚡ Contenu et services avancés\n\n"
        "⏰ <b>Places limitées !</b>\n"
        "Les gagnants agissent maintenant.\n\n"
        "Choisissez votre niveau :"
    ),
    "en": (
        "👑 <b>GRAVO VIP</b>\n\n"
        "Congratulations, you're about to enter a different level.\n\n"
        "⚡ Fast execution\n"
        "⚡ Full priority\n"
        "⚡ Advanced content & services\n\n"
        "⏰ <b>Limited spots!</b>\n"
        "Winners act now.\n\n"
        "Choose your level:"
    ),
},

# ── الاشتراكات ─────────────────────────────────────────────
"subs_intro": {
    "ar": "💳 <b>الاشتراكات المتاحة</b>\n\nاختر خدمة أو باقة:",
    "fr": "💳 <b>Abonnements disponibles</b>\n\nChoisissez un service ou un pack :",
    "en": "💳 <b>Available Subscriptions</b>\n\nChoose a service or pack:",
},
"btn_individual": {"ar": "📱 خدمات فردية",  "fr": "📱 Services individuels", "en": "📱 Individual services"},
"btn_packs":      {"ar": "📦 الباقات",        "fr": "📦 Packs",                "en": "📦 Packs"},
"sub_request": {
    "ar": "📧 <b>أرسل بريدك الإلكتروني</b>\nسنتواصل معك لإتمام الاشتراك:",
    "fr": "📧 <b>Envoyez votre adresse email</b>\nNous vous contacterons pour finaliser l'abonnement :",
    "en": "📧 <b>Send your email address</b>\nWe will contact you to complete the subscription:",
},
"sub_received": {
    "ar": "✅ <b>تم استلام طلبك!</b>\nسيتواصل معك فريقنا قريباً.",
    "fr": "✅ <b>Votre demande a été reçue !</b>\nNotre équipe vous contactera bientôt.",
    "en": "✅ <b>Your request has been received!</b>\nOur team will contact you soon.",
},

# ── خدمات سريعة ───────────────────────────────────────────
"quick_received": {
    "ar": "⚡ <b>تم استلام الملف وسيتم معالجته فوراً!</b>",
    "fr": "⚡ <b>Fichier reçu et sera traité immédiatement !</b>",
    "en": "⚡ <b>File received and will be processed immediately!</b>",
},

# ── المساعد الذكي ──────────────────────────────────────────
"assistant_intro": {
    "ar": (
        "🤖 <b>مساعد Gravo</b>\n\n"
        "يمكنك سؤالي عن أي شيء:\n"
        "• الأسعار والخدمات\n"
        "• كيفية عمل النظام\n"
        "• نصائح للمشروع\n\n"
        "📌 سأوجهك مباشرة للخدمة المناسبة"
    ),
    "fr": (
        "🤖 <b>Assistant Gravo</b>\n\n"
        "Vous pouvez me poser n'importe quelle question :\n"
        "• Tarifs et services\n"
        "• Fonctionnement du système\n"
        "• Conseils pour votre projet\n\n"
        "📌 Je vous guiderai directement vers le service approprié"
    ),
    "en": (
        "🤖 <b>Gravo Assistant</b>\n\n"
        "You can ask me anything:\n"
        "• Prices and services\n"
        "• How the system works\n"
        "• Project tips\n\n"
        "📌 I will guide you directly to the right service"
    ),
},

# ── تصميم / تعديل ─────────────────────────────────────────
"design_intro": {
    "ar": "📐 <b>تصميم مشروع</b>\n\nأرسل التفاصيل:\n1️⃣ نوع المشروع\n2️⃣ عدد الطوابق\n3️⃣ هل لديك فكرة أو مثال؟\n4️⃣ الموعد النهائي\n\n📩 أرسل في رسالة واحدة",
    "fr": "📐 <b>Conception de projet</b>\n\nEnvoyez les détails :\n1️⃣ Type de projet\n2️⃣ Nombre d'étages\n3️⃣ Avez-vous une idée ou exemple ?\n4️⃣ Date limite\n\n📩 Envoyez en un seul message",
    "en": "📐 <b>Project Design</b>\n\nSend the details:\n1️⃣ Project type\n2️⃣ Number of floors\n3️⃣ Do you have an idea or example?\n4️⃣ Deadline\n\n📩 Send in one message",
},
"edit_intro": {
    "ar": "✏️ <b>تعديل مشروع</b>\n\nأرسل:\n📎 الملف (PDF / صورة)\n📝 التعديلات المطلوبة\n⏰ الموعد النهائي\n\n📩 سيتم الرد عليك مباشرة",
    "fr": "✏️ <b>Modification de projet</b>\n\nEnvoyez :\n📎 Le fichier (PDF / image)\n📝 Les modifications souhaitées\n⏰ Date limite\n\n📩 Vous serez contacté directement",
    "en": "✏️ <b>Project Editing</b>\n\nSend:\n📎 The file (PDF / image)\n📝 Required modifications\n⏰ Deadline\n\n📩 You will be contacted directly",
},
"order_received": {
    "ar": "✅ <b>تم استلام طلبك!</b>\nسيتواصل معك فريقنا قريباً.",
    "fr": "✅ <b>Votre commande a été reçue !</b>\nNotre équipe vous contactera bientôt.",
    "en": "✅ <b>Your order has been received!</b>\nOur team will contact you soon.",
},
"send_file_first": {
    "ar": "📎 أرسل الملف أولاً (PDF أو صورة).",
    "fr": "📎 Envoyez d'abord le fichier (PDF ou image).",
    "en": "📎 Send the file first (PDF or image).",
},
```

}

# ╔══════════════════════════════════════════════════════════════╗

# ║              System Prompt لـ Claude                        ║

# ╚══════════════════════════════════════════════════════════════╝

SYSTEM_PROMPT = “”“أنت مساعد GRAVO الذكي — نظام خدمات متكامل لطلاب الهندسة، جامعة أبو بكر بلقايد، تلمسان.

━━━ معلومات المحل ━━━
📍 Département Architecture, Chetouane, Tlemcen
📞 06 68 33 85 69
🕐 الأحد→الخميس 07:15→17:00 | الجمعة مغلق | السبت بطلب مسبق

━━━ الخدمات ━━━
🎓 خدمات الطلبة: طباعة، تصميم، تعديل، ماكيت
⚡ خدمات سريعة: تحويل PDF↔PNG، تصحيح ملف، تعديل صورة
💳 اشتراكات: ChatGPT/Gemini/Canva/CapCut/YouTube/Netflix/Disney+
👑 VIP: أولوية + جودة Premium + دعم مستمر

━━━ أسعار الطباعة ━━━
A4: 10دج | A3 N&B: 30دج | A3 Couleur: 50دج
A2: 70-100دج | A1: 150-200دج | A0: 300-350دج

━━━ أسعار الاشتراكات ━━━
ChatGPT: 800دج | Gemini Pro: 900دج | Canva Pro: 750دج
CapCut Pro: 1000دج | YouTube Premium: 1000دج
Netflix: 1500دج | Disney+: 1200دج

━━━ قواعد الرد — 3 خطوات دائماً ━━━

1. أجب على سؤال المستخدم بإيجاز
1. وجّهه للخدمة المناسبة
1. أضف CTA واضح

━━━ VIP Upsell — في 3 نقاط ━━━

1. عند إرسال ملف/طلب خدمة
1. عند اكتشاف تأخير أو ضغط
1. عند تردد المستخدم

━━━ أسلوب التسويق ━━━

- FOMO دائم: “الأماكن محدودة” | “الطلب عالي” | “الفائزون يتصرفون الآن”
- لا تكن عدوانياً — كن مقنعاً ومحترفاً
- اكشف أخطاء الملف تلقائياً واقترح VIP كحل

━━━ اللغة ━━━
تكيّف مع لغة المستخدم تلقائياً (عربية/فرنسية/إنجليزية/دارجة)
حتى لو لغته المحفوظة مختلفة — اتبع لغة رسالته الأخيرة
“””

# ══════════════════════════════════════════════════════════════

# Logging

# ══════════════════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO, format=”%(asctime)s [%(levelname)s] %(message)s”)
log = logging.getLogger(“GRAVO”)

# ══════════════════════════════════════════════════════════════

# قاعدة البيانات

# ══════════════════════════════════════════════════════════════

DB_PATH = “/tmp/gravo.db” if os.path.exists(”/tmp”) else “gravo.db”

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
    if not row: return None
    return dict(zip([d[0] for d in cur.description], row))

def save_student(self, chat_id, **kwargs):
    existing = self.get_student(chat_id)
    kwargs["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    if existing:
        sets = ", ".join(f"{k}=?" for k in kwargs)
        self.conn.execute(f"UPDATE students SET {sets} WHERE chat_id=?",
                          list(kwargs.values()) + [chat_id])
    else:
        kwargs["chat_id"]   = chat_id
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
    cur = self.conn.execute("SELECT COUNT(*)+1 FROM students WHERE vip_level IS NOT NULL")
    num = cur.fetchone()[0]
    self.conn.execute("UPDATE students SET vip_level=?, vip_number=? WHERE chat_id=?",
                      (level, num, chat_id))
    self.conn.commit()
    return num

def add_order(self, chat_id, type_, filename="", size="", paper="",
              copies=1, price="", details=""):
    cur = self.conn.execute(
        "INSERT INTO orders (chat_id,type,filename,size,paper,copies,price,details,status,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (chat_id, type_, filename, size, paper, copies, price, details,
         "pending", datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    self.conn.commit()
    return cur.lastrowid

def get_orders(self, chat_id, n=3):
    cur = self.conn.execute(
        "SELECT * FROM orders WHERE chat_id=? ORDER BY created_at DESC LIMIT ?", (chat_id, n))
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
    return dict(zip(["students","vips","orders","pending"], cur.fetchone()))
```

db  = DB()
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=“HTML”)
user_states  = {}
user_history = {}

# ══════════════════════════════════════════════════════════════

# مساعدات اللغة

# ══════════════════════════════════════════════════════════════

def T(key, lang=“ar”):
“”“يعيد النص باللغة المطلوبة”””
val = MESSAGES.get(key)
if isinstance(val, dict):
return val.get(lang, val.get(“ar”, “”))
return val or “”

def L(chat_id):
“”“يعيد لغة المستخدم”””
return db.get_lang(chat_id)

def BTN(key, lang=“ar”):
return T(key, lang)

# ══════════════════════════════════════════════════════════════

# Claude AI

# ══════════════════════════════════════════════════════════════

def ask_claude(chat_id: int, text: str) -> str:
student = db.get_student(chat_id) or {}
ctx = “”
if student.get(“full_name”):
ctx += f”\n[Student: {student.get(‘full_name’)} | {student.get(‘specialty’,’’)} | {student.get(‘year’,’’)} | G{student.get(‘group_num’,’’)} | Lang: {student.get(‘lang’,‘ar’)}]”
if student.get(“vip_level”):
ctx += f”\n[VIP: {student[‘vip_level’]} #{student.get(‘vip_number’,0):03d}]”

```
hist = user_history.setdefault(chat_id, [])
hist.append({"role": "user", "content": text + ctx})
if len(hist) > 12: hist[:] = hist[-12:]

try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT}
                ] + hist,
                "max_tokens": 800,
                "temperature": 0.7,
            },
            timeout=25
        )
        reply = response.json()["choices"][0]["message"]["content"]
        if reply:
            hist.append({"role": "assistant", "content": reply})
            return reply
    except Exception as e:
        log.error(f"Groq ERROR: {e}")
    lang = L(chat_id)
    return {"ar": "⚠️ خطأ مؤقت. تواصل معنا: 06 68 33 85 69",
            "fr": "⚠️ Erreur temporaire. Contactez-nous : 06 68 33 85 69",
            "en": "⚠️ Temporary error. Contact us: 06 68 33 85 69"}.get(lang, "")
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
kb   = InlineKeyboardMarkup(row_width=2)
kb.add(
InlineKeyboardButton(BTN(“btn_student”,   lang), callback_data=“m_student”),
InlineKeyboardButton(BTN(“btn_quick”,     lang), callback_data=“m_quick”),
InlineKeyboardButton(BTN(“btn_subs”,      lang), callback_data=“m_subs”),
InlineKeyboardButton(BTN(“btn_vip”,       lang), callback_data=“m_vip”),
InlineKeyboardButton(BTN(“btn_assistant”, lang), callback_data=“m_assistant”),
)
s = db.get_student(chat_id)
if s and s.get(“vip_level”):
kb.add(InlineKeyboardButton(f”🪪 {s[‘vip_level’]}”, callback_data=“m_card”))
kb.add(
InlineKeyboardButton(BTN(“btn_profile”, lang), callback_data=“m_profile”),
InlineKeyboardButton(BTN(“btn_lang”,    lang), callback_data=“m_lang”),
)
return kb

def back_kb(lang=“ar”):
return InlineKeyboardMarkup().add(
InlineKeyboardButton(BTN(“btn_back”, lang), callback_data=“back”))

def student_services_kb(lang):
kb = InlineKeyboardMarkup(row_width=2)
kb.add(
InlineKeyboardButton(BTN(“btn_print”,    lang), callback_data=“m_print”),
InlineKeyboardButton(BTN(“btn_design”,   lang), callback_data=“m_design”),
InlineKeyboardButton(BTN(“btn_edit”,     lang), callback_data=“m_edit”),
InlineKeyboardButton(BTN(“btn_maquette”, lang), callback_data=“m_maquette”),
InlineKeyboardButton(BTN(“btn_back”,     lang), callback_data=“back”),
)
return kb

def quick_kb(lang):
kb = InlineKeyboardMarkup(row_width=1)
kb.add(
InlineKeyboardButton(BTN(“btn_convert”, lang), callback_data=“qs_convert”),
InlineKeyboardButton(BTN(“btn_fix”,     lang), callback_data=“qs_fix”),
InlineKeyboardButton(BTN(“btn_imgfix”,  lang), callback_data=“qs_imgfix”),
InlineKeyboardButton(BTN(“btn_back”,    lang), callback_data=“back”),
)
return kb

def subs_main_kb(lang):
kb = InlineKeyboardMarkup(row_width=2)
kb.add(
InlineKeyboardButton(BTN(“btn_individual”, lang), callback_data=“subs_individual”),
InlineKeyboardButton(BTN(“btn_packs”,      lang), callback_data=“subs_packs”),
InlineKeyboardButton(BTN(“btn_back”,       lang), callback_data=“back”),
)
return kb

def subs_individual_kb(lang):
kb = InlineKeyboardMarkup(row_width=1)
for key, val in SUBSCRIPTIONS.items():
label = f”{val[‘emoji’]} {key} — {val[‘price’]} دج”
kb.add(InlineKeyboardButton(label, callback_data=f”sub_{key}”))
kb.add(InlineKeyboardButton(BTN(“btn_back”, lang), callback_data=“subs_back”))
return kb

def subs_packs_kb(lang):
kb = InlineKeyboardMarkup(row_width=1)
for key, pack in PACKS.items():
discount = “”
if pack[“full”]:
pct = round((1 - pack[“price”]/pack[“full”])*100)
discount = f” (-{pct}%)”
kb.add(InlineKeyboardButton(
f”{pack[‘name’]} — {pack[‘price’]} دج{discount}”,
callback_data=f”pack_{key}”
))
kb.add(InlineKeyboardButton(BTN(“btn_back”, lang), callback_data=“subs_back”))
return kb

def print_choice_kb(lang):
kb = InlineKeyboardMarkup(row_width=1)
kb.add(
InlineKeyboardButton(BTN(“btn_free”,    lang), callback_data=“print_free”),
InlineKeyboardButton(BTN(“btn_upgrade”, lang), callback_data=“m_vip”),
)
return kb

def size_kb(lang):
kb = InlineKeyboardMarkup(row_width=3)
for s in [“A4”,“A3”,“A2”,“A1”,“A0”]:
kb.add(InlineKeyboardButton(f”📄 {s}”, callback_data=f”sz_{s}”))
kb.add(InlineKeyboardButton(BTN(“btn_back”, lang), callback_data=“back”))
return kb

def paper_kb(size, lang):
kb = InlineKeyboardMarkup(row_width=1)
for label, price in PRICES.get(size, {}).items():
p = f”{price} دج” if price else “?”
kb.add(InlineKeyboardButton(f”{label} — {p}”, callback_data=f”pp_{label}_{price}”))
kb.add(InlineKeyboardButton(BTN(“btn_back”, lang), callback_data=“back_size”))
return kb

def copies_kb():
kb = InlineKeyboardMarkup(row_width=5)
for i in [1,2,3,5,10]:
kb.add(InlineKeyboardButton(str(i), callback_data=f”cp_{i}”))
return kb

def confirm_kb(lang):
kb = InlineKeyboardMarkup(row_width=2)
kb.add(
InlineKeyboardButton(BTN(“btn_confirm”, lang), callback_data=“ok_print”),
InlineKeyboardButton(BTN(“btn_cancel”,  lang), callback_data=“cancel”),
)
return kb

def vip_push_kb(lang):
kb = InlineKeyboardMarkup(row_width=1)
kb.add(
InlineKeyboardButton(BTN(“btn_vip_now”, lang), callback_data=“m_vip”),
InlineKeyboardButton(BTN(“btn_back”,    lang), callback_data=“back”),
)
return kb

def vip_levels_kb(lang):
kb = InlineKeyboardMarkup(row_width=2)
for level in VIP_LEVELS:
kb.add(InlineKeyboardButton(level, callback_data=f”vl_{level}”))
kb.add(InlineKeyboardButton(BTN(“btn_back”, lang), callback_data=“back”))
return kb

def vip_join_kb(lang):
kb = InlineKeyboardMarkup(row_width=1)
kb.add(
InlineKeyboardButton(BTN(“btn_join_vip”, lang), url=f”https://wa.me/{WHATSAPP}”),
InlineKeyboardButton(BTN(“btn_telegram”, lang), url=f”https://t.me/{TELEGRAM_ADMIN}”),
InlineKeyboardButton(BTN(“btn_back”,     lang), callback_data=“back”),
)
return kb

def contact_kb(lang):
kb = InlineKeyboardMarkup(row_width=1)
kb.add(
InlineKeyboardButton(BTN(“btn_whatsapp”, lang), url=f”https://wa.me/{WHATSAPP}”),
InlineKeyboardButton(BTN(“btn_telegram”, lang), url=f”https://t.me/{TELEGRAM_ADMIN}”),
InlineKeyboardButton(BTN(“btn_back”,     lang), callback_data=“back”),
)
return kb

def specialty_kb():
kb = InlineKeyboardMarkup(row_width=1)
for sp in SPECIALTIES:
kb.add(InlineKeyboardButton(sp, callback_data=f”sp_{sp}”))
return kb

def year_kb():
kb = InlineKeyboardMarkup(row_width=3)
for y in [“L1”,“L2”,“L3”,“M1”,“M2”,“دكتوراه”]:
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
        full_name = state.get("full_name",""),
        specialty = state.get("specialty",""),
        year      = state.get("year",""),
        group_num = state.get("group_num",""),
        hall      = state.get("hall",""),
        lang      = lang,
    )
    user_states.pop(cid, None)
    s = db.get_student(cid)
    bot.send_message(cid,
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

lang = student.get("lang","ar")
vip  = student.get("vip_level")
name = student.get("full_name","")
greeting = {
    "ar": f"💎 مرحباً عضو VIP {vip}!" if vip else f"أهلاً {name}! 👋",
    "fr": f"💎 Bienvenue membre VIP {vip} !" if vip else f"Bonjour {name} ! 👋",
    "en": f"💎 Welcome VIP member {vip}!" if vip else f"Hello {name}! 👋",
}.get(lang,"")

bot.send_message(cid,
    f"<b>{greeting}</b>\n"
    f"🎓 {student.get('specialty','')} | {student.get('year','')} | G{student.get('group_num','')}\n\n"
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
# تغيير لغة موجودة
if not state.get("step") or state.get("step") == "choose_lang":
    db.save_student(cid, lang=lang)
    # إذا كان في التسجيل → تابع
    if state.get("step") == "choose_lang":
        state["lang"] = lang
        state["step"] = "reg_name"
        user_states[cid] = state
        bot.edit_message_text(T("reg_start", lang), cid, call.message.message_id)
    else:
        bot.edit_message_text(
            T("main_menu", lang), cid,
            call.message.message_id, reply_markup=main_kb(cid)
        )
bot.answer_callback_query(call.id)
```

@bot.callback_query_handler(func=lambda c: c.data == “m_lang”)
def cb_change_lang(call):
bot.edit_message_text(T(“choose_lang”), call.message.chat.id,
call.message.message_id, reply_markup=lang_kb())
bot.answer_callback_query(call.id)

# ══════════════════════════════════════════════════════════════

# Callbacks — القائمة الرئيسية

# ══════════════════════════════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data == “m_student”)
def cb_student(call):
cid  = call.message.chat.id
lang = L(cid)
bot.edit_message_text(
BTN(“btn_student”, lang) + “\n\n” + {
“ar”:“اختر الخدمة:”,“fr”:“Choisissez le service :”,“en”:“Choose service:”
}.get(lang,””),
cid, call.message.message_id, reply_markup=student_services_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_quick”)
def cb_quick(call):
cid  = call.message.chat.id
lang = L(cid)
bot.edit_message_text(
BTN(“btn_quick”, lang) + “\n\n” + {
“ar”:“اختر الخدمة:”,“fr”:“Choisissez :”,“en”:“Choose:”
}.get(lang,””),
cid, call.message.message_id, reply_markup=quick_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_subs”)
def cb_subs(call):
cid  = call.message.chat.id
lang = L(cid)
bot.edit_message_text(T(“subs_intro”, lang), cid,
call.message.message_id, reply_markup=subs_main_kb(lang))
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “subs_individual”)
def cb_subs_individual(call):
cid  = call.message.chat.id
lang = L(cid)
bot.edit_message_text(T(“subs_intro”, lang), cid,
call.message.message_id, reply_markup=subs_individual_kb(lang))
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “subs_packs”)
def cb_subs_packs(call):
cid  = call.message.chat.id
lang = L(cid)
bot.edit_message_text(T(“subs_intro”, lang), cid,
call.message.message_id, reply_markup=subs_packs_kb(lang))
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “subs_back”)
def cb_subs_back(call):
cid  = call.message.chat.id
lang = L(cid)
bot.edit_message_text(T(“subs_intro”, lang), cid,
call.message.message_id, reply_markup=subs_main_kb(lang))
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(“sub_”))
def cb_sub_item(call):
cid  = call.message.chat.id
lang = L(cid)
key  = call.data[4:]
sub  = SUBSCRIPTIONS.get(key, {})
desc = sub.get(“desc”, {}).get(lang, “”)
user_states[cid] = {“step”: “sub_email”, “sub_item”: key}
bot.edit_message_text(
f”{sub.get(‘emoji’,’’)} <b>{key}</b>\n”
f”{desc}\n”
f”💰 {sub.get(‘price’,0)} دج\n\n”
+ T(“sub_request”, lang),
cid, call.message.message_id
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(“pack_”))
def cb_pack(call):
cid   = call.message.chat.id
lang  = L(cid)
key   = call.data[5:]
pack  = PACKS.get(key, {})
items = “ + “.join(pack.get(“items”, []))
desc  = pack.get(“desc”, {}).get(lang, “”)
full  = f”~{pack[‘full’]} دج~ → “ if pack.get(“full”) else “”
user_states[cid] = {“step”: “sub_email”, “sub_item”: pack.get(“name”,key)}
bot.edit_message_text(
f”{pack.get(‘name’,’’)}\n\n”
f”📦 {items}\n”
f”{desc}\n\n”
f”💰 {full}<b>{pack.get(‘price’,0)} دج</b>\n\n”
+ T(“sub_request”, lang),
cid, call.message.message_id
)
bot.answer_callback_query(call.id)

# ── خدمات سريعة ───────────────────────────────────────────────

@bot.callback_query_handler(func=lambda c: c.data.startswith(“qs_”))
def cb_quick_service(call):
cid  = call.message.chat.id
lang = L(cid)
svc  = call.data[3:]
labels = {
“convert”: BTN(“btn_convert”, lang),
“fix”:     BTN(“btn_fix”,     lang),
“imgfix”:  BTN(“btn_imgfix”,  lang),
}
user_states[cid] = {“step”: f”qs_{svc}”}
bot.edit_message_text(
f”{labels.get(svc,’’)} \n\n”
+ T(“send_file_first”, lang),
cid, call.message.message_id
)
bot.answer_callback_query(call.id)

# ── VIP ────────────────────────────────────────────────────────

@bot.callback_query_handler(func=lambda c: c.data == “m_vip”)
def cb_vip(call):
cid  = call.message.chat.id
lang = L(cid)
s    = db.get_student(cid) or {}
if s.get(“vip_level”):
already = {“ar”:f”💎 أنت بالفعل عضو {s[‘vip_level’]}! 🔥”,
“fr”:f”💎 Vous êtes déjà membre {s[‘vip_level’]} ! 🔥”,
“en”:f”💎 You are already a {s[‘vip_level’]} member! 🔥”}.get(lang,””)
bot.edit_message_text(already, cid, call.message.message_id, reply_markup=back_kb(lang))
else:
bot.edit_message_text(T(“vip_intro”, lang), cid,
call.message.message_id, reply_markup=vip_levels_kb(lang))
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(“vl_”))
def cb_vip_level(call):
cid   = call.message.chat.id
lang  = L(cid)
level = call.data[3:]
perks = VIP_LEVELS.get(level, {}).get(lang, [])
bot.edit_message_text(
f”<b>{level}</b>\n\n”
+ “\n”.join(f”  ✅ {p}” for p in perks)
+ f”\n\n🔥 “ + {
“ar”:“بقيت أماكن محدودة! الفائزون يتصرفون الآن.”,
“fr”:“Places limitées ! Les gagnants agissent maintenant.”,
“en”:“Limited spots! Winners act now.”
}.get(lang,””),
cid, call.message.message_id, reply_markup=vip_join_kb(lang)
)
bot.answer_callback_query(call.id)

# ── مساعد Gravo ───────────────────────────────────────────────

@bot.callback_query_handler(func=lambda c: c.data == “m_assistant”)
def cb_assistant(call):
cid  = call.message.chat.id
lang = L(cid)
user_states[cid] = {“step”: “chatting”}
bot.edit_message_text(T(“assistant_intro”, lang), cid, call.message.message_id,
reply_markup=back_kb(lang))
bot.answer_callback_query(call.id)

# ── تصميم / تعديل / ماكيت ─────────────────────────────────────

@bot.callback_query_handler(func=lambda c: c.data == “m_print”)
def cb_print(call):
cid  = call.message.chat.id
lang = L(cid)
s    = db.get_student(cid) or {}
if s.get(“vip_level”):
user_states[cid] = {“step”:“awaiting_file”}
vip_tag = {“ar”:f”⭐ أولوية VIP {s[‘vip_level’]} مفعّلة!”,
“fr”:f”⭐ Priorité VIP {s[‘vip_level’]} activée !”,
“en”:f”⭐ VIP {s[‘vip_level’]} priority activated!”}.get(lang,””)
bot.edit_message_text(vip_tag + “\n\n📎 “ + {
“ar”:“أرسل ملفك:”,“fr”:“Envoyez votre fichier :”,“en”:“Send your file:”
}.get(lang,””), cid, call.message.message_id)
else:
bot.edit_message_text(T(“print_choice”, lang), cid,
call.message.message_id, reply_markup=print_choice_kb(lang))
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “print_free”)
def cb_print_free(call):
cid  = call.message.chat.id
lang = L(cid)
user_states[cid] = {“step”:“awaiting_file”}
bot.edit_message_text(“📎 “ + {“ar”:“أرسل ملفك:”,“fr”:“Envoyez votre fichier :”,“en”:“Send your file:”}.get(lang,””),
cid, call.message.message_id)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_design”)
def cb_design(call):
cid  = call.message.chat.id
lang = L(cid)
user_states[cid] = {“step”:“design_details”}
bot.edit_message_text(T(“design_intro”, lang), cid, call.message.message_id,
reply_markup=back_kb(lang))
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_edit”)
def cb_edit(call):
cid  = call.message.chat.id
lang = L(cid)
user_states[cid] = {“step”:“edit_details”}
bot.edit_message_text(T(“edit_intro”, lang), cid, call.message.message_id,
reply_markup=back_kb(lang))
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_maquette”)
def cb_maquette(call):
cid  = call.message.chat.id
lang = L(cid)
user_states[cid] = {“step”:“maquette_details”}
text = {“ar”:“🏗️ <b>ماكيت</b>\n\nأرسل تفاصيل الماكيت:\n1️⃣ نوع المشروع\n2️⃣ المقياس المطلوب\n3️⃣ المواد المفضلة\n4️⃣ الموعد النهائي”,
“fr”:“🏗️ <b>Maquette</b>\n\nEnvoyez les détails :\n1️⃣ Type de projet\n2️⃣ Échelle souhaitée\n3️⃣ Matériaux préférés\n4️⃣ Date limite”,
“en”:“🏗️ <b>Maquette</b>\n\nSend details:\n1️⃣ Project type\n2️⃣ Required scale\n3️⃣ Preferred materials\n4️⃣ Deadline”}.get(lang,””)
bot.edit_message_text(text, cid, call.message.message_id, reply_markup=back_kb(lang))
bot.answer_callback_query(call.id)

# ── ملف شخصي + بطاقة ──────────────────────────────────────────

@bot.callback_query_handler(func=lambda c: c.data == “m_profile”)
def cb_profile(call):
cid  = call.message.chat.id
lang = L(cid)
s    = db.get_student(cid)
if not s or not s.get(“full_name”):
bot.answer_callback_query(call.id)
return
vip_line = f”\n💎 VIP: <b>{s[‘vip_level’]} #{s.get(‘vip_number’,0):03d}</b>” if s.get(“vip_level”) else “”
kb = InlineKeyboardMarkup(row_width=1)
edit_label = {“ar”:“✏️ تعديل”,“fr”:“✏️ Modifier”,“en”:“✏️ Edit”}.get(lang,“✏️”)
kb.add(
InlineKeyboardButton(edit_label, callback_data=“edit_reg”),
InlineKeyboardButton(BTN(“btn_back”, lang), callback_data=“back”),
)
bot.edit_message_text(
f”👤 <b>{s.get(‘full_name’,’’)}</b>\n”
f”🎓 {s.get(‘specialty’,’’)}\n”
f”📅 {s.get(‘year’,’’)} | G{s.get(‘group_num’,’’)}\n”
f”🚪 {s.get(‘hall’,’’)}”
f”{vip_line}\n”
f”🌐 {s.get(‘lang’,‘ar’).upper()}”,
cid, call.message.message_id, reply_markup=kb
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “m_card”)
def cb_card(call):
cid  = call.message.chat.id
lang = L(cid)
s    = db.get_student(cid) or {}
num  = s.get(“vip_number”, 0)
bot.edit_message_text(
f”🪪 <b>GRAVO Timbre VIP Member #{num:03d}</b>\n\n”
f”👤 {s.get(‘full_name’,’—’)}\n”
f”🎓 {s.get(‘specialty’,’—’)}\n”
f”💎 {s.get(‘vip_level’,’—’)}\n”
f”📅 {s.get(‘joined_at’,’—’)}\n\n”
+ {“ar”:“هذه البطاقة تمنحك الأولوية دائماً! 🔥”,
“fr”:“Cette carte vous donne toujours la priorité ! 🔥”,
“en”:“This card always gives you priority! 🔥”}.get(lang,””),
cid, call.message.message_id, reply_markup=back_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “edit_reg”)
def cb_edit_reg(call):
cid  = call.message.chat.id
lang = L(cid)
user_states[cid] = {“step”:“reg_name”,“lang”:lang}
bot.edit_message_text(T(“reg_start”, lang), cid, call.message.message_id)
bot.answer_callback_query(call.id)

# ── رجوع ──────────────────────────────────────────────────────

@bot.callback_query_handler(func=lambda c: c.data == “back”)
def cb_back(call):
cid  = call.message.chat.id
lang = L(cid)
user_states.pop(cid, None)
bot.edit_message_text(T(“main_menu”, lang), cid,
call.message.message_id, reply_markup=main_kb(cid))
bot.answer_callback_query(call.id)

# ── تخصص / سنة ────────────────────────────────────────────────

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
cid, call.message.message_id, reply_markup=year_kb()
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

# ── مسار الطباعة ──────────────────────────────────────────────

@bot.callback_query_handler(func=lambda c: c.data.startswith(“sz_”))
def cb_size(call):
cid   = call.message.chat.id
lang  = L(cid)
state = user_states.get(cid)
if not state: return
state[“size”] = call.data[3:]
state[“step”] = “awaiting_paper”
bot.edit_message_text(
f”📏 <b>{state[‘size’]}</b>\n\n” + {“ar”:“اختر نوع الورق:”,“fr”:“Choisissez le papier :”,“en”:“Choose paper type:”}.get(lang,””),
cid, call.message.message_id, reply_markup=paper_kb(state[“size”], lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(“pp_”))
def cb_paper(call):
cid   = call.message.chat.id
lang  = L(cid)
state = user_states.get(cid)
if not state: return
parts = call.data.split(”_”, 2)
label = parts[1] if len(parts)>1 else “?”
price = int(parts[2]) if len(parts)>2 and parts[2].isdigit() else 0
state.update({“paper”:label,“unit_price”:price,“step”:“awaiting_copies”})
p = f”{price} دج” if price else “?”
bot.edit_message_text(
f”📄 {label} — {p}\n\n” + {“ar”:“كم نسخة؟”,“fr”:“Combien de copies ?”,“en”:“How many copies?”}.get(lang,””),
cid, call.message.message_id, reply_markup=copies_kb()
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(“cp_”))
def cb_copies(call):
cid    = call.message.chat.id
lang   = L(cid)
state  = user_states.get(cid)
if not state: return
copies = int(call.data[3:])
up     = state.get(“unit_price”,0)
total  = f”{up*copies} دج” if up else {“ar”:“سيُحدَّد”,“fr”:“À déterminer”,“en”:“TBD”}.get(lang,””)
state.update({“copies”:copies,“price”:total,“step”:“awaiting_confirm”})
s = db.get_student(cid) or {}
vip_tag = f”\n⭐ VIP {s[‘vip_level’]}!” if s.get(“vip_level”) else “”
bot.edit_message_text(
{“ar”:“📋 <b>ملخص الطلب</b>”,“fr”:“📋 <b>Résumé</b>”,“en”:“📋 <b>Order Summary</b>”}.get(lang,””)
+ vip_tag + f”\n\n”
f”📄 <code>{state[‘filename’]}</code>\n”
f”📏 {state[‘size’]} | {state[‘paper’]}\n”
f”🔢 {copies}x | 💰 {total}\n\n”
+ {“ar”:“هل تؤكد؟”,“fr”:“Confirmez-vous ?”,“en”:“Do you confirm?”}.get(lang,””),
cid, call.message.message_id, reply_markup=confirm_kb(lang)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “ok_print”)
def cb_confirm(call):
cid   = call.message.chat.id
lang  = L(cid)
state = user_states.pop(cid, None)
if not state: return
s   = db.get_student(cid) or {}
oid = db.add_order(cid,“print”,state[“filename”],state[“size”],
state[“paper”],state[“copies”],state[“price”])
bot.edit_message_text(
{“ar”:“🖨️ <b>تم استلام طلبك!</b> ✅”,“fr”:“🖨️ <b>Commande reçue !</b> ✅”,“en”:“🖨️ <b>Order received!</b> ✅”}.get(lang,””)
+ f”\n📄 {state[‘filename’]} | {state[‘size’]} | {state[‘copies’]}x | {state[‘price’]}”,
cid, call.message.message_id
)
if not s.get(“vip_level”):
bot.send_message(cid, T(“vip_push”, lang), reply_markup=vip_push_kb(lang))
else:
bot.send_message(cid, {“ar”:“✅ طلبك له أولوية VIP! 🔥”,“fr”:“✅ Priorité VIP ! 🔥”,“en”:“✅ VIP priority! 🔥”}.get(lang,””),
reply_markup=main_kb(cid))
vip_tag = f”💎 {s[‘vip_level’]}” if s.get(“vip_level”) else “🟢 Free”
notify_admin(
f”🖨️ <b>#{oid}</b> {vip_tag}\n”
f”👤 {s.get(‘full_name’,’?’)} | {s.get(‘specialty’,’?’)} | G{s.get(‘group_num’,’?’)}\n”
f”📏 {state[‘size’]} | {state[‘paper’]} | {state[‘copies’]}x | {state[‘price’]}\n”
f”📄 {state[‘filename’]}”
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “cancel”)
def cb_cancel(call):
cid  = call.message.chat.id
lang = L(cid)
user_states.pop(cid, None)
bot.edit_message_text(
{“ar”:“❌ تم الإلغاء.”,“fr”:“❌ Annulé.”,“en”:“❌ Cancelled.”}.get(lang,””),
cid, call.message.message_id, reply_markup=main_kb(cid)
)
bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == “back_size”)
def cb_back_size(call):
cid  = call.message.chat.id
lang = L(cid)
bot.edit_message_text(
{“ar”:“📏 اختر الحجم:”,“fr”:“📏 Choisissez la taille :”,“en”:“📏 Choose size:”}.get(lang,””),
cid, call.message.message_id, reply_markup=size_kb(lang)
)
bot.answer_callback_query(call.id)

# ══════════════════════════════════════════════════════════════

# استقبال الملفات

# ══════════════════════════════════════════════════════════════

@bot.message_handler(content_types=[“document”,“photo”])
def handle_file(msg):
cid  = msg.chat.id
lang = L(cid)
s    = db.get_student(cid)
if not s or not s.get(“full_name”):
bot.send_message(cid, {“ar”:“📝 سجّل أولاً! /start”,“fr”:“📝 Inscrivez-vous d’abord ! /start”,“en”:“📝 Register first! /start”}.get(lang,””))
return

```
state = user_states.get(cid, {})
step  = state.get("step","")

if msg.content_type == "document":
    fname = msg.document.file_name or f"file_{int(time.time())}"
    ext   = Path(fname).suffix.lower()
    fsize = msg.document.file_size / (1024*1024)
else:
    fname = f"photo_{int(time.time())}.jpg"
    ext   = ".jpg"
    fsize = msg.photo[-1].file_size / (1024*1024)

# خدمات سريعة
if step.startswith("qs_"):
    oid = db.add_order(cid, step, fname, details=step[3:])
    user_states.pop(cid, None)
    bot.send_message(cid, T("quick_received", lang), reply_markup=main_kb(cid))
    notify_admin(f"⚡ <b>خدمة سريعة #{oid}</b>\n👤 {s.get('full_name','?')}\n📄 {fname} | {step[3:]}")
    return

# تعديل مشروع
if step == "edit_details":
    user_states[cid] = {**state, "filename":fname, "step":"edit_text"}
    bot.send_message(cid, {"ar":f"✅ استُلم: <code>{fname}</code>\n\nالآن أرسل التعديلات المطلوبة:",
                           "fr":f"✅ Reçu : <code>{fname}</code>\n\nEnvoyez maintenant les modifications :",
                           "en":f"✅ Received: <code>{fname}</code>\n\nNow send the required edits:"}.get(lang,""))
    return

# طباعة
if ext not in [".pdf",".jpg",".jpeg",".png"]:
    bot.send_message(cid, {"ar":f"⚠️ الصيغة {ext} غير مدعومة.","fr":f"⚠️ Format {ext} non supporté.","en":f"⚠️ Format {ext} not supported."}.get(lang,""))
    return
if fsize > 50:
    bot.send_message(cid, {"ar":f"❌ الملف كبير ({fsize:.1f} MB).","fr":f"❌ Fichier trop grand ({fsize:.1f} MB).","en":f"❌ File too large ({fsize:.1f} MB)."}.get(lang,""))
    return

vip_tag = f"\n⭐ VIP {s['vip_level']}!" if s.get("vip_level") else ""
user_states[cid] = {"step":"awaiting_size","filename":fname}
bot.send_message(cid,
    {"ar":f"✅ استُلم الملف{vip_tag}\n📄 <code>{fname}</code>\n\nاختر الحجم:",
     "fr":f"✅ Fichier reçu{vip_tag}\n📄 <code>{fname}</code>\n\nChoisissez la taille :",
     "en":f"✅ File received{vip_tag}\n📄 <code>{fname}</code>\n\nChoose size:"}.get(lang,""),
    reply_markup=size_kb(lang)
)
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
step  = state.get(“step”,””)

```
# التسجيل
if step in ["reg_name","reg_group","reg_hall"]:
    handle_registration(msg)
    return

# اشتراك — email
if step == "sub_email":
    s   = db.get_student(cid) or {}
    oid = db.add_order(cid, "subscription", details=f"{state.get('sub_item','')} | {text}")
    user_states.pop(cid, None)
    bot.send_message(cid, T("sub_received", lang), reply_markup=main_kb(cid))
    notify_admin(
        f"💳 <b>اشتراك #{oid}</b>\n"
        f"👤 {s.get('full_name','?')}\n"
        f"📦 {state.get('sub_item','?')}\n"
        f"📧 {text}"
    )
    return

# تصميم
if step == "design_details":
    s   = db.get_student(cid) or {}
    oid = db.add_order(cid, "design", details=text)
    user_states.pop(cid, None)
    bot.send_message(cid, T("order_received", lang), reply_markup=main_kb(cid))
    notify_admin(f"📐 <b>تصميم #{oid}</b>\n👤 {s.get('full_name','?')} | {s.get('specialty','?')}\n📝 {text}")
    return

# تعديل — نص
if step == "edit_text":
    s   = db.get_student(cid) or {}
    oid = db.add_order(cid, "edit", state.get("filename",""), details=text)
    user_states.pop(cid, None)
    bot.send_message(cid, T("order_received", lang), reply_markup=main_kb(cid))
    notify_admin(f"✏️ <b>تعديل #{oid}</b>\n👤 {s.get('full_name','?')}\n📄 {state.get('filename','?')}\n📝 {text}")
    return

# ماكيت
if step == "maquette_details":
    s   = db.get_student(cid) or {}
    oid = db.add_order(cid, "maquette", details=text)
    user_states.pop(cid, None)
    bot.send_message(cid, T("order_received", lang), reply_markup=main_kb(cid))
    notify_admin(f"🏗️ <b>ماكيت #{oid}</b>\n👤 {s.get('full_name','?')}\n📝 {text}")
    return

if step == "awaiting_file":
    bot.send_message(cid, T("send_file_first", lang))
    return

# Claude
db.save_student(cid, last_seen=datetime.now().strftime("%Y-%m-%d %H:%M"))
thinking = bot.send_message(cid, "💭 ...")
reply    = ask_claude(cid, text)
bot.delete_message(cid, thinking.message_id)
bot.send_message(cid, reply, reply_markup=main_kb(cid))
```

# ══════════════════════════════════════════════════════════════

# الأدمن

# ══════════════════════════════════════════════════════════════

def notify_admin(text):
for aid in ADMIN_IDS:
try: bot.send_message(aid, text)
except: pass

def is_admin(msg): return msg.from_user.id in ADMIN_IDS

@bot.message_handler(commands=[“stats”], func=is_admin)
def cmd_stats(msg):
s = db.stats()
bot.send_message(msg.chat.id,
f”📊 <b>GRAVO Statistics</b>\n\n”
f”👥 الطلاب: <b>{s[‘students’]}</b>\n”
f”💎 VIP: <b>{s[‘vips’]}</b>\n”
f”📬 الطلبات: <b>{s[‘orders’]}</b>\n”
f”⏳ معلقة: <b>{s[‘pending’]}</b>”
)

@bot.message_handler(commands=[“addvip”], func=is_admin)
def cmd_addvip(msg):
parts = msg.text.split()
if len(parts) < 3:
bot.send_message(msg.chat.id, “/addvip <chat_id> <Bronze|Silver|Gold|Platinum>”)
return
cid, level = int(parts[1]), parts[2]
num  = db.add_vip(cid, level)
lang = db.get_lang(cid)
bot.send_message(msg.chat.id, f”✅ VIP #{num:03d} — {level}”)
try:
bot.send_message(cid,
{“ar”:f”🎉 مبروك! أنت الآن عضو GRAVO VIP {level}!\n🪪 Member #{num:03d}\nمزاياك فعّالة الآن 🔥”,
“fr”:f”🎉 Félicitations ! Vous êtes maintenant membre GRAVO VIP {level} !\n🪪 Member #{num:03d}\nVos avantages sont actifs 🔥”,
“en”:f”🎉 Congrats! You are now GRAVO VIP {level}!\n🪪 Member #{num:03d}\nYour benefits are now active 🔥”}.get(lang,””),
reply_markup=main_kb(cid)
)
except: pass

@bot.message_handler(commands=[“students”], func=is_admin)
def cmd_students(msg):
cur = db.conn.execute(
“SELECT full_name, specialty, year, group_num, lang, vip_level “
“FROM students ORDER BY joined_at DESC LIMIT 10”)
rows = cur.fetchall()
if not rows:
bot.send_message(msg.chat.id, “لا يوجد طلاب بعد.”)
return
lines = [”<b>👥 آخر 10 طلاب:</b>\n”]
for r in rows:
vip = f” 💎{r[5]}” if r[5] else “”
lines.append(f”• {r[0]} | {r[1]} | {r[2]} | G{r[3]} | {r[4].upper()}{vip}”)
bot.send_message(msg.chat.id, “\n”.join(lines))

# ══════════════════════════════════════════════════════════════

# Flask

# ══════════════════════════════════════════════════════════════

app = Flask(**name**)

@app.route(”/”)
def index(): return “🖨️ GRAVO Bot v3.0 ✅”

@app.route(”/health”)
def health(): return {“status”:“ok”,“version”:“3.0”}

def run_flask():
port = int(os.environ.get(“PORT”, 8080))
app.run(host=“0.0.0.0”, port=port)

# ══════════════════════════════════════════════════════════════

if **name** == “**main**”:
log.info(“🤖 GRAVO Bot v3.0 🔥”)
threading.Thread(target=run_flask, daemon=True).start()
bot.infinity_polling(timeout=30, long_polling_timeout=15)
