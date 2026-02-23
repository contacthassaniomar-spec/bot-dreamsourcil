import os
from typing import Dict, Any, List

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

# =========================
# ENV
# =========================
# Accepte TOKEN, et si tu avais mis JETON avant, ça marche aussi.
TOKEN = os.getenv("TOKEN") or os.getenv("JETON")

# ID de TON compte Telegram (chat id admin) pour recevoir les preuves
ID_CHAT_ADMIN = os.getenv("ID_CHAT_ADMIN")  # ex: "8453472234"

# Lien PayPal (mettre ton lien de paiement / ou ton linktree / ou un lien par formation si tu veux)
PAYPAL_LINK = os.getenv("PAYPAL_LINK", "https://www.paypal.com/")  # <-- remplace si besoin

REGLES = (
    "📌 *Règles importantes*\n"
    "• L’acompte bloque la place.\n"
    "• Le solde doit être payé avant le jour J.\n"
    "• En cas d’empêchement, merci de prévenir au plus tôt.\n"
)

# =========================
# DATA
# =========================
FORMATIONS: Dict[str, Dict[str, Any]] = {
    "henna_2j": {
        "titre": "Henna Brow — 2 jours",
        "details": [
            "Brow Mapping",
            "Préparation du sourcil",
            "Application du henné",
            "Retouches & conseils",
        ],
        "prix": 1290,
        "acompte": 390,
        "dates": "Sur demande (contactez la formatrice)",
    },
    "browlift_2j": {
        "titre": "Browlift — 2 jours",
        "details": [
            "Diagnostic",
            "Browlift complet",
            "Finitions",
            "Conseils entretien",
        ],
        "prix": 1290,
        "acompte": 390,
        "dates": "Sur demande (contactez la formatrice)",
    },
    "ultime_4j": {
        "titre": "Formation Ultime — 4 jours",
        "details": [
            "Mapping",
            "Décoloration surplus",
            "Teinture / Hybrid",
            "Browlift",
            "Business / réseaux",
        ],
        "prix": 2590,
        "acompte": 790,
        "dates": "27 → 30 avril 2026\n27 → 30 juillet 2026",
    },
}

# =========================
# HELPERS
# =========================
def menu_formations_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Henna Brow (2j)", callback_data="formation_henna_2j")],
        [InlineKeyboardButton("✨ Browlift (2j)", callback_data="formation_browlift_2j")],
        [InlineKeyboardButton("👑 Formation Ultime (4j)", callback_data="formation_ultime_4j")],
        [InlineKeyboardButton("📅 Dates", callback_data="menu_dates")],
        [InlineKeyboardButton("📩 Contact", callback_data="menu_contact")],
    ])


def retour_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Retour menu", callback_data="menu_formations")]
    ])


# =========================
# COMMANDS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 *Bienvenue sur le bot Dream Sourcil*\n\n"
        "Choisissez une rubrique :",
        reply_markup=menu_formations_kb(),
        parse_mode=ParseMode.MARKDOWN,
    )


# =========================
# VIEWS
# =========================
async def afficher_formation(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str) -> None:
    query = update.callback_query
    await query.answer()

    f = FORMATIONS[key]

    texte = (
        f"✨ *{f['titre']}*\n\n"
        f"✅ *Inclus :*\n" + "\n".join([f"• {x}" for x in f["details"]]) + "\n\n"
        f"💶 *Prix :* {f['prix']}€\n"
        f"💳 *Acompte (30%) :* {f['acompte']}€\n"
        f"📅 *Dates :*\n{f['dates']}\n\n"
        f"{REGLES}"
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💳 Payer l’acompte ({f['acompte']}€)", url=PAYPAL_LINK)],
        [InlineKeyboardButton(f"💰 Payer en intégral ({f['prix']}€)", url=PAYPAL_LINK)],
        [InlineKeyboardButton("✅ J’ai déjà payé — envoyer ma preuve", callback_data=f"paid_{key}")],
        [InlineKeyboardButton("🕒 S’inscrire sur liste d’attente", callback_data=f"waitlist_{key}")],
        [InlineKeyboardButton("⬅️ Retour", callback_data="menu_formations")],
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
        "• Formation Ultime : 27 → 30 avril 2026\n"
        "• Formation Ultime : 27 → 30 juillet 2026\n\n"
        "Les formations 2 jours sont sur demande : contactez la formatrice."
    )

    await query.edit_message_text(
        texte,
        reply_markup=retour_menu_kb(),
        parse_mode=ParseMode.MARKDOWN,
    )


async def menu_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    texte = (
        "📩 *Contact*\n\n"
        "Pour réserver une date, poser une question ou confirmer un paiement :\n"
        "• Instagram : @dreamsourcil_marseille\n"
        "• Email : dreamsourcil.marseille@gmail.com"
    )

    await query.edit_message_text(
        texte,
        reply_markup=retour_menu_kb(),
        parse_mode=ParseMode.MARKDOWN,
    )


# =========================
# CALLBACKS
# =========================
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data

    if data == "menu_formations":
        await query.answer()
        await query.edit_message_text(
            "Choisissez une formation :",
            reply_markup=menu_formations_kb(),
        )
        return

    if data == "menu_dates":
        await menu_dates(update, context)
        return

    if data == "menu_contact":
        await menu_contact(update, context)
        return

    if data.startswith("formation_"):
        # formation_henna_2j => henna_2j
        key = data.replace("formation_", "")
        await afficher_formation(update, context, key)
        return

    if data.startswith("paid_"):
        key = data.replace("paid_", "")
        context.user_data["paid_key"] = key
        await query.answer()
        await query.edit_message_text(
            "✅ Merci !\n\n"
            "Veuillez maintenant *envoyer la preuve de paiement* :\n"
            "• une *capture* (photo) OU\n"
            "• un *reçu PDF*\n\n"
            "⚠️ Assurez-vous que le *montant*, le *nom* et la *formation* soient visibles.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=retour_menu_kb(),
        )
        return

    if data.startswith("waitlist_"):
        await query.answer()
        await query.edit_message_text(
            "🕒 D’accord ! Vous êtes noté(e) pour la liste d’attente.\n\n"
            "📩 La formatrice vous recontactera dès qu’une place se libère.",
            reply_markup=retour_menu_kb(),
        )
        return

    await query.answer()


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

    # admin
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

    # photo
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await context.bot.send_photo(
            chat_id=chat_id_admin,
            photo=file_id,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
        )

    # document (pdf)
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

    # confirmation user
    await update.message.reply_text(
        "✅ Merci ! Preuve bien reçue.\n"
        "La formatrice a été notifiée et reviendra vers vous pour la confirmation finale. 🤍"
    )

    # reset
    context.user_data.pop("paid_key", None)


# =========================
# MAIN
# =========================
def main() -> None:
    if not TOKEN:
        raise RuntimeError("TOKEN manquant. Ajoute la variable d'environnement TOKEN (ou JETON) sur Railway.")

    app = Application.builder().token(TOKEN).build()

    # commands
    app.add_handler(CommandHandler("start", start))

    # callbacks
    app.add_handler(CallbackQueryHandler(on_callback))

    # proof receiver
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.PDF, send_proof))

    app.run_polling()


if __name__ == "__main__":
    main()
