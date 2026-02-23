import os
from typing import Dict, Any

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ✅ OpenAI (Agent IA)
from openai import OpenAI

# =========================
# ENV
# =========================
TOKEN = os.getenv("TOKEN") or os.getenv("JETON")
ID_CHAT_ADMIN = os.getenv("ID_CHAT_ADMIN")  # ex: "8453472234"

# ✅ OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ✅ Ton vrai lien PayPal (par défaut)
PAYPAL_LINK_DEFAULT = os.getenv("PAYPAL_LINK", "https://paypal.me/DreamSourCilFR")

# ✅ Liens réseaux sociaux
INSTAGRAM_LINK = "https://www.instagram.com/dreamsourcil_marseille?igsh=MW9xN2pkdjIxbDFzMw%3D%3D&utm_source=qr"
TIKTOK_LINK = "https://www.tiktok.com/@dreamsourcil.marseille?_r=1&_t=ZG-94AjxonEL0i"

REGLES = (
    "📌 *Règles importantes*\n"
    "• L’acompte bloque la place.\n"
    "• Le solde doit être payé avant le jour J.\n"
    "• En cas d’empêchement, merci de prévenir au plus tôt.\n"
)

# =========================
# BASE DE CONNAISSANCE (IA)
# =========================
# 👉 Ici tu peux enrichir au fil du temps (infos, matériel, adresse, horaires, etc.)
KNOWLEDGE_BASE = """
Dream Sourcil Formation (Marseille).
Objectif: informer sur les formations, dates, tarifs, modalités de paiement (acompte/solde),
et orienter vers la formatrice si nécessaire.

Formations:
1) Maîtriser la Prestation Henna Brow — 2 jours (990€ / acompte 297€)
- Brow Mapping (avec décoloration OU épilation cire)
- Colorimétrie Henné
- Pratique sur plusieurs modèles
Dates: pas de dates fixes — contacter la formatrice.

2) Maîtriser la Prestation Browlift — 2 jours (1190€ / acompte 357€)
- Brow Mapping + Teinture Hybride
- Décoloration OU épilation cire
- Pratique sur plusieurs modèles
Dates: pas de dates fixes — contacter la formatrice.

3) Formation Ultime Dream Sourcil — 4 jours (1790€ / acompte 537€)
- Restructuration simple (décoloration OU épilation cire)
- Browlift Restructuration
- Browlift + Teinture + Restructuration
- Prestation Henna Brow
- Prestation Teinture Hybride
- Module Marketing : attirer & fidéliser ses premières clientes
Dates: 27→30 avril 2026 / 27→30 juillet 2026

4) Formation Ultime — 4 jours (Sans module Henna Brow) (1500€ / acompte 450€)
- Restructuration simple (décoloration OU épilation cire)
- Browlift Restructuration
- Browlift + Teinture + Restructuration
- Prestation Teinture Hybride
- Module Marketing : attirer & fidéliser ses premières clientes
Dates: 27→30 avril 2026 / 27→30 juillet 2026
"""

SYSTEM_PROMPT = f"""
Tu es l'assistante IA officielle de Dream Sourcil Formation.
Ton rôle: répondre aux questions des clientes de manière claire, polie, professionnelle et chaleureuse.

Règles:
- Réponses courtes et utiles. Si la question est floue, poser UNE seule question.
- Ne jamais inventer des infos. Si tu ne sais pas: dire "Je te confirme avec la formatrice" et proposer le bouton Contact.
- Ne jamais demander de données sensibles (CB, mots de passe).
- Pour le paiement: rappeler acompte/solde et renvoyer vers les boutons PayPal.
- Si la cliente demande une réservation: expliquer la marche à suivre (payer acompte / envoyer preuve / liste d’attente).
- Si besoin humain: orienter vers "📩 Contacter la formatrice".

Connaissance:
{KNOWLEDGE_BASE}
"""

# =========================
# DATA
# =========================
FORMATIONS: Dict[str, Dict[str, Any]] = {
    "henna_2j": {
        "titre": "Maîtriser la Prestation Henna Brow — 2 jours",
        "details": [
            "Brow Mapping (avec décoloration OU épilation cire)",
            "Colorimétrie Henné",
            "Pratique sur plusieurs modèles",
        ],
        "prix": 990,
        "acompte": 297,
        "dates": "Pas de dates fixes — contactez la formatrice.",
    },
    "browlift_2j": {
        "titre": "Maîtriser la Prestation Browlift — 2 jours",
        "details": [
            "Brow Mapping + Teinture Hybride",
            "Décoloration OU épilation cire",
            "Pratique sur plusieurs modèles",
        ],
        "prix": 1190,
        "acompte": 357,
        "dates": "Pas de dates fixes — contactez la formatrice.",
    },
    "ultime_4j": {
        "titre": "Formation Ultime Dream Sourcil — 4 jours",
        "details": [
            "Restructuration simple (décoloration OU épilation cire)",
            "Browlift Restructuration",
            "Browlift + Teinture + Restructuration",
            "Prestation Henna Brow",
            "Prestation Teinture Hybride",
            "Module Marketing : attirer & fidéliser ses premières clientes",
        ],
        "prix": 1790,
        "acompte": 537,
        "dates": "27 → 30 avril 2026\n27 → 30 juillet 2026",
    },
    "ultime_4j_sans_henna": {
        "titre": "Formation Ultime Dream Sourcil — 4 jours (Sans module Henna Brow)",
        "details": [
            "Restructuration simple (décoloration OU épilation cire)",
            "Browlift Restructuration",
            "Browlift + Teinture + Restructuration",
            "Prestation Teinture Hybride",
            "Module Marketing : attirer & fidéliser ses premières clientes",
        ],
        "prix": 1500,
        "acompte": 450,
        "dates": "27 → 30 avril 2026\n27 → 30 juillet 2026",
    },
}

# =========================
# MENUS
# =========================
def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Formations", callback_data="menu_formations")],
        [InlineKeyboardButton("📅 Prochaines dates", callback_data="main_dates")],
        [InlineKeyboardButton("💳 Paiement / Acompte", callback_data="main_paiement")],
        [InlineKeyboardButton("📋 Liste d’attente", callback_data="main_waitlist")],
        [InlineKeyboardButton("📩 Contacter la formatrice", callback_data="main_contact")],
        [InlineKeyboardButton("📱 Mes réseaux sociaux", callback_data="main_socials")],
        [InlineKeyboardButton("🤖 Assistant IA", callback_data="main_ai")],  # ✅ AJOUT IA
    ])


def menu_formations_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Henna Brow (2j)", callback_data="formation_henna_2j")],
        [InlineKeyboardButton("✨ Browlift (2j)", callback_data="formation_browlift_2j")],
        [InlineKeyboardButton("👑 Formation Ultime (4j)", callback_data="formation_ultime_4j")],
        [InlineKeyboardButton("👑 Ultime (4j) — sans Henna", callback_data="formation_ultime_4j_sans_henna")],
        [InlineKeyboardButton("⬅️ Retour menu principal", callback_data="main_menu")],
    ])


def retour_menu_principal_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Retour menu principal", callback_data="main_menu")]
    ])


def retour_menu_formations_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Retour formations", callback_data="menu_formations")]
    ])


def menu_socials_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Instagram", url=INSTAGRAM_LINK)],
        [InlineKeyboardButton("🎵 TikTok", url=TIKTOK_LINK)],
        [InlineKeyboardButton("⬅️ Retour menu principal", callback_data="main_menu")],
    ])


def menu_ai_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Contacter la formatrice", callback_data="main_contact")],
        [InlineKeyboardButton("⬅️ Retour menu principal", callback_data="main_menu")],
    ])

# =========================
# COMMANDS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 *Bienvenue sur le bot Dream Sourcil Formation.*\n\n"
        "Choisissez une rubrique ci-dessous :",
        reply_markup=main_menu_kb(),
        parse_mode=ParseMode.MARKDOWN,
    )

# =========================
# VIEWS
# =========================
async def afficher_formation(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str) -> None:
    query = update.callback_query
    await query.answer()

    f = FORMATIONS[key]
    paypal_link = f.get("paypal_link") or PAYPAL_LINK_DEFAULT

    texte = (
        f"✨ *{f['titre']}*\n\n"
        f"✅ *Inclus :*\n" + "\n".join([f"• {x}" for x in f["details"]]) + "\n\n"
        f"💶 *Prix :* {f['prix']}€\n"
        f"💳 *Acompte :* {f['acompte']}€\n"
        f"📅 *Dates :*\n{f['dates']}\n\n"
        f"{REGLES}"
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💳 Payer l’acompte ({f['acompte']}€)", url=paypal_link)],
        [InlineKeyboardButton(f"💰 Payer en intégral ({f['prix']}€)", url=paypal_link)],
        [InlineKeyboardButton("✅ J’ai déjà payé — envoyer ma preuve", callback_data=f"paid_{key}")],
        [InlineKeyboardButton("🕒 S’inscrire sur liste d’attente", callback_data=f"waitlist_{key}")],
        [InlineKeyboardButton("⬅️ Retour formations", callback_data="menu_formations")],
    ])

    await query.edit_message_text(
        texte,
        reply_markup=kb,
        parse_mode=ParseMode.MARKDOWN,
    )


async def menu_dates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    texte = (
        "📅 *Prochaines dates*\n\n"
        "• Formation Ultime Dream Sourcil (4j) : 27 → 30 avril 2026\n"
        "• Formation Ultime Dream Sourcil (4j) : 27 → 30 juillet 2026\n\n"
        "Les formations *2 jours* n’ont pas de date fixe : contactez la formatrice."
    )

    await query.edit_message_text(
        texte,
        reply_markup=retour_menu_principal_kb(),
        parse_mode=ParseMode.MARKDOWN,
    )

# =========================
# ADMIN NOTIFS
# =========================
async def notify_admin_waitlist(context: ContextTypes.DEFAULT_TYPE, user, key: str) -> None:
    if not ID_CHAT_ADMIN:
        return

    chat_id_admin = int(ID_CHAT_ADMIN)
    f = FORMATIONS.get(key, {"titre": key})

    msg = (
        "📋 *Liste d’attente — nouvelle demande*\n"
        f"👤 Nom : {user.first_name or ''} {user.last_name or ''}\n"
        f"🆔 User ID : `{user.id}`\n"
        f"📚 Formation : *{f.get('titre', key)}*\n"
    )
    if user.username:
        msg += f"🔗 Username : @{user.username}\n"

    await context.bot.send_message(
        chat_id=chat_id_admin,
        text=msg,
        parse_mode=ParseMode.MARKDOWN,
    )


async def notify_admin_contact(context: ContextTypes.DEFAULT_TYPE, user, message_text: str) -> None:
    if not ID_CHAT_ADMIN:
        return

    msg = (
        "📩 *Nouveau message — Contact formation*\n"
        f"👤 Nom : {user.first_name or ''} {user.last_name or ''}\n"
        f"🆔 User ID : `{user.id}`\n"
    )
    if user.username:
        msg += f"🔗 Username : @{user.username}\n"
    msg += f"\n💬 *Message :*\n{message_text}"

    await context.bot.send_message(
        chat_id=int(ID_CHAT_ADMIN),
        text=msg,
        parse_mode=ParseMode.MARKDOWN,
    )

# =========================
# AGENT IA - helper
# =========================
async def ai_answer(user_text: str) -> str:
    """
    Génère une réponse IA à partir de la base de connaissance.
    """
    if not client:
        return "⚠️ L’assistant IA n’est pas encore configuré. Merci de contacter la formatrice."

    try:
        resp = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
        )
        # Le SDK renvoie généralement le texte via output_text
        text = getattr(resp, "output_text", None)
        if text:
            return text.strip()
        # fallback si output_text n'existe pas
        return "Je n’ai pas réussi à générer une réponse. Peux-tu reformuler ?"
    except Exception:
        return "⚠️ Petit souci technique avec l’IA. Tu peux utiliser “Contacter la formatrice”."

# =========================
# CALLBACKS
# =========================
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "main_menu":
        # On coupe les modes
        context.user_data["contact_mode"] = False
        context.user_data["ai_mode"] = False

        await query.edit_message_text(
            "👋 *Bienvenue sur le bot Dream Sourcil Formation.*\n\n"
            "Choisissez une rubrique ci-dessous :",
            reply_markup=main_menu_kb(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "menu_formations":
        context.user_data["contact_mode"] = False
        context.user_data["ai_mode"] = False
        await query.edit_message_text(
            "Choisissez une formation :",
            reply_markup=menu_formations_kb(),
        )
        return

    if data == "main_dates":
        await menu_dates(update, context)
        return

    if data == "main_paiement":
        await query.edit_message_text(
            "💳 *Paiement / Acompte*\n\n"
            "👉 Pour payer :\n"
            "1) Cliquez sur *📚 Formations*\n"
            "2) Choisissez votre formation\n"
            "3) Cliquez sur *Payer l’acompte* ou *Payer en intégral*\n\n"
            "✅ Si vous avez déjà payé : cliquez sur *J’ai déjà payé — envoyer ma preuve*.",
            reply_markup=retour_menu_principal_kb(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "main_waitlist":
        await query.edit_message_text(
            "📋 *Liste d’attente*\n\n"
            "👉 Pour vous inscrire :\n"
            "1) Cliquez sur *📚 Formations*\n"
            "2) Choisissez la formation\n"
            "3) Cliquez sur *🕒 S’inscrire sur liste d’attente*.",
            reply_markup=retour_menu_principal_kb(),
        )
        return

    if data == "main_socials":
        await query.edit_message_text(
            "📱 *Mes réseaux sociaux*\n\n"
            "Retrouvez Dream Sourcil ici :",
            reply_markup=menu_socials_kb(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # ✅ IA
    if data == "main_ai":
        context.user_data["contact_mode"] = False
        context.user_data["ai_mode"] = True

        await query.edit_message_text(
            "🤖 *Assistant IA Dream Sourcil*\n\n"
            "Pose ta question ici (tarifs, contenu, dates, paiement, etc.).\n"
            "Je te réponds immédiatement.\n\n"
            "📌 À tout moment, tu peux aussi contacter la formatrice.",
            reply_markup=menu_ai_kb(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # ✅ CONTACT: la cliente écrit un message -> envoyé à l'ADMIN
    if data == "main_contact":
        context.user_data["ai_mode"] = False
        context.user_data["contact_mode"] = True
        await query.edit_message_text(
            "📩 *Contacter la formatrice*\n\n"
            "Écris ton message ici (question, réservation, confirmation de paiement…).\n\n"
            "✅ Dès que tu l’envoies, je le transmets directement à la formatrice.",
            reply_markup=retour_menu_principal_kb(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data.startswith("formation_"):
        key = data.replace("formation_", "")
        await afficher_formation(update, context, key)
        return

    if data.startswith("paid_"):
        key = data.replace("paid_", "")
        context.user_data["paid_key"] = key
        await query.edit_message_text(
            "✅ Merci !\n\n"
            "Veuillez maintenant *envoyer la preuve de paiement* :\n"
            "• une *capture* (photo) OU\n"
            "• un *reçu PDF*\n\n"
            "⚠️ Assurez-vous que le *montant*, le *nom* et la *formation* soient visibles.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=retour_menu_formations_kb(),
        )
        return

    if data.startswith("waitlist_"):
        key = data.replace("waitlist_", "")
        user = update.effective_user

        await notify_admin_waitlist(context, user, key)

        await query.edit_message_text(
            "🕒 D’accord ! Vous êtes noté(e) sur la liste d’attente.\n\n"
            "📩 La formatrice vous recontactera dès qu’une place se libère.",
            reply_markup=retour_menu_formations_kb(),
        )
        return

# =========================
# TEXT ROUTER (IA ou CONTACT)
# =========================
async def handle_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Route les messages texte:
    - si ai_mode => répond via IA
    - sinon si contact_mode => envoie à l'admin
    - sinon => ignore
    """
    user_text = (update.message.text or "").strip()
    if not user_text:
        return

    # IA
    if context.user_data.get("ai_mode"):
        answer = await ai_answer(user_text)
        await update.message.reply_text(
            answer,
            reply_markup=menu_ai_kb(),
        )
        return

    # Contact (admin)
    if context.user_data.get("contact_mode"):
        context.user_data["contact_mode"] = False

        if not ID_CHAT_ADMIN:
            await update.message.reply_text("⚠️ Admin non configuré (ID_CHAT_ADMIN manquant).")
            return

        user = update.effective_user
        await notify_admin_contact(context, user, user_text)

        await update.message.reply_text(
            "✅ Merci ! Ton message a bien été transmis à la formatrice. 🤍",
            reply_markup=retour_menu_principal_kb(),
        )
        return

# =========================
# PROOF RECEIVER
# =========================
async def send_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    key = context.user_data.get("paid_key")
    if not key:
        await update.message.reply_text(
            "⚠️ Pour envoyer une preuve, ouvrez d’abord une formation puis cliquez sur :\n"
            "✅ *J’ai déjà payé — envoyer ma preuve*",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if not ID_CHAT_ADMIN:
        await update.message.reply_text("⚠️ Admin non configuré (ID_CHAT_ADMIN manquant).")
        return

    chat_id_admin = int(ID_CHAT_ADMIN)
    user = update.effective_user
    f = FORMATIONS.get(key, {"titre": key})

    caption = (
        "✅ *Preuve de paiement reçue*\n"
        f"👤 Nom : {user.first_name or ''} {user.last_name or ''}\n"
        f"🆔 User ID : `{user.id}`\n"
        f"📚 Formation : *{f.get('titre', key)}*\n"
    )

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await context.bot.send_photo(
            chat_id=chat_id_admin,
            photo=file_id,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
        )
    elif update.message.document:
        file_id = update.message.document.file_id
        await context.bot.send_document(
            chat_id=chat_id_admin,
            document=file_id,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await update.message.reply_text("⚠️ Merci d’envoyer une *photo* ou un *PDF*.")
        return

    await update.message.reply_text(
        "✅ Merci ! Preuve bien reçue.\n"
        "La formatrice a été notifiée et reviendra vers vous pour la confirmation finale. 🤍"
    )

    context.user_data.pop("paid_key", None)

# =========================
# MAIN
# =========================
def main() -> None:
    if not TOKEN:
        raise RuntimeError("TOKEN manquant. Ajoute la variable d'environnement TOKEN (ou JETON) sur Railway.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_callback))

    # preuves paiement (photo/pdf)
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.PDF, send_proof))

    # ✅ texte: routeur (IA ou Contact)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_router))

    app.run_polling()


if __name__ == "__main__":
    main()
