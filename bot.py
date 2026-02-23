import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = os.environ.get("JETON_BOT_TELEGRAM")

if not TOKEN or ":" not in TOKEN or len(TOKEN) < 30:
    raise RuntimeError(f"TOKEN invalide ou vide (len={0 if not TOKEN else len(TOKEN)})")

PAYPAL_LINK = "https://www.paypal.com/paypalme/DreamSourCilFR"

# --- Textes / règles ---
REGLES = (
    "📌 Modalités :\n"
    "• Acompte : 30% pour réserver votre place\n"
    "• Solde : à régler avant le jour J\n"
    "• Fin des réservations : 15 jours avant la date\n"
    "• 2 places maximum par formation\n\n"
    "✅ Sur PayPal, saisissez exactement le montant indiqué.\n"
    "📝 Note PayPal : Nom + Formation + Date"
)

FORMATIONS = {
    "henna_2j": {
        "titre": "Maîtriser la Prestation Henna Brow (2 jours)",
        "prix": 990,
        "acompte": 297,
        "dates": "Dates sur demande (contactez la formatrice).",
        "details": [
            "Brow Mapping (décoloration OU épilation cire)",
            "Colorimétrie Henné",
            "Pratique sur plusieurs modèles",
        ],
    },
    "browlift_2j": {
        "titre": "Maîtriser la Prestation Browlift (2 jours)",
        "prix": 1190,
        "acompte": 357,
        "dates": "Dates sur demande (contactez la formatrice).",
        "details": [
            "Brow Mapping",
            "Teinture Hybride",
            "Décoloration OU épilation cire",
            "Pratique sur plusieurs modèles",
        ],
    },
    "ultime_4j": {
        "titre": "Formation Ultime Dream Sourcil (4 jours)",
        "prix": 1790,
        "acompte": 537,
        "dates": "27 → 30 avril 2026\n27 → 30 juillet 2026",
        "details": [
            "Restructuration simple (décoloration OU épilation cire)",
            "Browlift restructuration",
            "Browlift + teinture + restructuration",
            "Prestation Henna Brow",
            "Prestation Teinture Hybride",
            "Module Marketing (attirer & fidéliser vos premières clientes)",
        ],
    },
    "ultime_sans_henna_4j": {
        "titre": "Formation Ultime (sans Henna Brow) (4 jours)",
        "prix": 1500,
        "acompte": 450,
        "dates": "27 → 30 avril 2026\n27 → 30 juillet 2026",
        "details": [
            "Techniques + module Marketing (hors Henna Brow)",
        ],
    },
}

# --- Menus ---
def menu_principal():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📚 Formations", callback_data="menu_formations")],
            [InlineKeyboardButton("📅 Prochaines dates", callback_data="menu_dates")],
            [InlineKeyboardButton("💳 Paiement / Acompte", callback_data="menu_paiement")],
            [InlineKeyboardButton("📋 Liste d’attente", callback_data="menu_waitlist")],
            [InlineKeyboardButton("📩 Contacter la formatrice", callback_data="menu_contact")],
        ]
    )

def bouton_retour_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour au menu", callback_data="menu")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bienvenue sur le bot *Dream Sourcil Formations*.\n\n"
        "Choisissez une rubrique ci-dessous :",
        reply_markup=menu_principal(),
        parse_mode="Markdown",
    )

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🏠 *Menu principal*\n\nChoisissez une rubrique :",
        reply_markup=menu_principal(),
        parse_mode="Markdown",
    )

# --- Formations ---
async def menu_formations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Henna Brow (2 jours) – 990€", callback_data="formation_henna_2j")],
            [InlineKeyboardButton("Browlift (2 jours) – 1190€", callback_data="formation_browlift_2j")],
            [InlineKeyboardButton("Formation Ultime (4 jours) – 1790€", callback_data="formation_ultime_4j")],
            [InlineKeyboardButton("Ultime sans Henna (4 jours) – 1500€", callback_data="formation_ultime_sans_henna_4j")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="menu")],
        ]
    )
    await query.edit_message_text(
        "📚 *Formations Dream Sourcil*\n\nSélectionnez une formation :",
        reply_markup=kb,
        parse_mode="Markdown",
    )

async def afficher_formation(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str):
    query = update.callback_query
    await query.answer()
    f = FORMATIONS[key]

    texte = (
        f"✨ *{f['titre']}*\n\n"
        "✅ Inclus :\n" + "\n".join([f"• {x}" for x in f["details"]]) + "\n\n"
        f"💶 Prix : *{f['prix']}€*\n"
        f"💳 Acompte (30%) : *{f['acompte']}€*\n\n"
        f"📅 Dates :\n{f['dates']}\n\n"
        f"{REGLES}"
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💳 Payer l’acompte ({f['acompte']}€)", url=PAYPAL_LINK)],
        [InlineKeyboardButton(f"💳 Payer en intégral ({f['prix']}€)", url=PAYPAL_LINK)],
        [InlineKeyboardButton("🗒 S’inscrire sur liste d’attente", callback_data=f"waitlist_{key}")],
        [InlineKeyboardButton("⬅️ Retour", callback_data="menu_formations")],
    ])
    
    await query.edit_message_text(texte, reply_markup=kb, parse_mode="Markdown")

async def formation_henna_2j(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await afficher_formation(update, context, "henna_2j")

async def formation_browlift_2j(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await afficher_formation(update, context, "browlift_2j")

async def formation_ultime_4j(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await afficher_formation(update, context, "ultime_4j")

async def formation_ultime_sans_henna_4j(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await afficher_formation(update, context, "ultime_sans_henna_4j")

# --- Dates / Paiement / Contact ---
async def menu_dates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📅 *Prochaines dates*\n\n"
        "• Formation Ultime : 27 → 30 avril 2026\n"
        "• Formation Ultime : 27 → 30 juillet 2026\n\n"
        "Les formations 2 jours sont sur demande : contactez la formatrice.",
        reply_markup=bouton_retour_menu(),
        parse_mode="Markdown",
    )

async def menu_paiement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "💳 *Paiement / Acompte*\n\n"
        "Vous pouvez régler :\n"
        "• l’acompte (30%)\n"
        "• ou le paiement intégral\n\n"
        f"➡️ Paiement via PayPal : {PAYPAL_LINK}\n\n"
        "✅ Pensez à indiquer en note : Nom + Formation + Date.",
        reply_markup=bouton_retour_menu(),
        parse_mode="Markdown",
    )

async def menu_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📩 *Contacter la formatrice*\n\n"
        "Pour réserver une formation 2 jours (date sur demande) ou poser une question,\n"
        "envoyez un message ici sur Telegram ou contactez Dream Sourcil.",
        reply_markup=bouton_retour_menu(),
        parse_mode="Markdown",
    )

# --- Liste d’attente (version simple : confirmation uniquement) ---
async def menu_waitlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📋 *Liste d’attente*\n\n"
        "Pour vous inscrire, ouvrez une formation puis cliquez sur :\n"
        "“S’inscrire sur liste d’attente”.",
        reply_markup=bouton_retour_menu(),
        parse_mode="Markdown",
    )

async def waitlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    key = query.data.replace("waitlist_", "")
    user = query.from_user

    username_line = (
        f"🔗 Username : @{user.username}\n" if user.username else "🔗 Username : (aucun)\n"
    )

    ID_CHAT_ADMIN = os.environ.get("ID_CHAT_ADMIN")

    # 1) Message à TOI (admin)
    if ID_CHAT_ADMIN:
        await context.bot.send_message(
            chat_id=int(ID_CHAT_ADMIN),
            text=(
                "📄 Nouvelle inscription – Liste d'attente\n\n"
                f"👤 Nom : {user.first_name or ''} {user.last_name or ''}\n"
                f"{username_line}"
                f"🎓 Formation : {key}\n"
                f"🆔 User ID : {user.id}"
            )
        )

    # 2) Message à la cliente + bouton retour menu
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Retour au menu", callback_data="menu")]
    ])

    await query.edit_message_text(
        "✅ Merci ! Vous êtes bien inscrite sur la *liste d'attente*.\n\n"
        "La formatrice vous recontactera dès qu'une place se libère ou qu'une nouvelle date est ouverte.",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Votre chat_id est : {update.effective_chat.id}"
    )

async def paid_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    key = query.data.replace("paid_", "")
    context.user_data["paid_key"] = key

    await query.edit_message_text(
        "✅ Paiement en cours\n\n"
        "📌 Merci d’envoyer ici :\n"
        "• une *capture d’écran* PayPal\n"
        "OU\n"
        "• le *PDF du reçu*\n\n"
        "Dès réception, je confirme et la formatrice est notifiée. 🤍",
        parse_mode="Markdown",
    )


async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get("paid_key")
    if not key:
        await update.message.reply_text(
            "⚠️ Pour envoyer une preuve, ouvre d’abord une formation puis clique sur :\n"
            "✅ J’ai payé (envoyer la preuve)"
        )
        return

    user = update.effective_user
    username = f"@{user.username}" if user.username else "(aucun)"
    first = user.first_name or ""
    last = user.last_name or ""
    full_name = (first + " " + last).strip()

    ID_CHAT_ADMIN = os.environ.get("ID_CHAT_ADMIN")

    caption = (
        "💳 *Preuve de paiement reçue*\n\n"
        f"👤 Nom : {full_name}\n"
        f"🔗 Username : {username}\n"
        f"📚 Formation : `{key}`\n"
        f"🆔 User ID : `{user.id}`"
    )

    # Envoi à l’admin si ID_CHAT_ADMIN est bien défini
    if ID_CHAT_ADMIN:
        chat_id_admin = int(ID_CHAT_ADMIN)

        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            await context.bot.send_photo(
                chat_id=chat_id_admin,
                photo=file_id,
                caption=caption,
                parse_mode="Markdown",
            )
        elif update.message.document:
            file_id = update.message.document.file_id
            await context.bot.send_document(
                chat_id=chat_id_admin,
                document=file_id,
                caption=caption,
                parse_mode="Markdown",
            )

async def send_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id_admin = int(os.environ.get("ID_CHAT_ADMIN", "0"))
    user = update.effective_user
    key = context.user_data.get("paid_key")

    # sécurité : admin pas configuré
    if not chat_id_admin:
        await update.message.reply_text("⚠️ Admin non configuré (ID_CHAT_ADMIN manquant).")
        return

    # sécurité : pas de formation liée
    if not key:
        await update.message.reply_text("⚠️ Je n’ai pas retrouvé la formation liée à votre paiement. Merci de recliquer sur le menu Paiement.")
        return

    caption = (
        "✅ *Preuve de paiement reçue*\n"
        f"👤 Nom : {user.first_name or ''} {user.last_name or ''}\n"
        f"🆔 User ID : `{user.id}`\n"
    )

    # Photo
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await context.bot.send_photo(
            chat_id=chat_id_admin,
            photo=file_id,
            caption=caption,
            parse_mode="Markdown",
        )

    # Document
    elif update.message.document:
        file_id = update.message.document.file_id
        await context.bot.send_document(
            chat_id=chat_id_admin,
            document=file_id,
            caption=caption,
            parse_mode="Markdown",
        )

    await update.message.reply_text(
        "✅ Merci ! Preuve bien reçue.\n"
        "La formatrice a été notifiée et reviendra vers vous pour la confirmation finale. 🤍"
    )

    # reset
    context.user_data.pop("paid_key", None)


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("myid", myid))

    application.add_handler(CallbackQueryHandler(show_menu, pattern="^menu$"))
    application.add_handler(CallbackQueryHandler(menu_formations, pattern="^menu_formations$"))
    application.add_handler(CallbackQueryHandler(menu_dates, pattern="^menu_dates$"))
    application.add_handler(CallbackQueryHandler(menu_paiement, pattern="^menu_paiement$"))
    application.add_handler(CallbackQueryHandler(menu_waitlist, pattern="^menu_waitlist$"))
    application.add_handler(CallbackQueryHandler(menu_contact, pattern="^menu_contacts$"))

    application.add_handler(CallbackQueryHandler(formation_henna_2j, pattern="^formation_henna_2j$"))
    application.add_handler(CallbackQueryHandler(formation_browlift_2j, pattern="^formation_browlift_2j$"))
    application.add_handler(CallbackQueryHandler(formation_ultime_4j, pattern="^formation_ultime_4j$"))
    application.add_handler(CallbackQueryHandler(formation_ultime_sans_henna_4j, pattern="^formation_ultime_sans_henna_4j$"))

    application.add_handler(CallbackQueryHandler(waitlist, pattern="^waitlist_"))
    

    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, send_proof))

    application.run_polling()


if __name__ == "__main__":
    main()
