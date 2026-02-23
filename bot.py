import os
import logging
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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# =========================
# CONFIG (Railway Variables)
# =========================
TOKEN = os.environ.get("TOKEN", "").strip()
PAYPAL_LINK = os.environ.get("PAYPAL_LINK", "").strip()
ID_CHAT_ADMIN = os.environ.get("ID_CHAT_ADMIN", "").strip()

# Safety: convert admin id if present
CHAT_ID_ADMIN = int(ID_CHAT_ADMIN) if ID_CHAT_ADMIN.isdigit() else 0


# =========================
# DATA: Formations
# =========================
# Tu peux modifier ici tes infos tranquillement
FORMATIONS: Dict[str, Dict[str, Any]] = {
    "henna_2j": {
        "titre": "Henna Brow Sans épilation — 2 jours",
        "prix": 1290,
        "acompte": 387,  # 30%
        "dates": [
            "• 27 → 28 avril 2026",
            "• 27 → 28 juillet 2026",
        ],
        "details": [
            "Brow Mapping",
            "Technique Henna Brow",
            "Décoloration du surplus",
            "Photos + corrections",
        ],
    },
    "browlift_2j": {
        "titre": "Browlift Sans épilation — 2 jours",
        "prix": 1390,
        "acompte": 417,  # 30%
        "dates": [
            "• Sur demande (contacte la formatrice)",
        ],
        "details": [
            "Brow Mapping",
            "Browlift (diagnostic + protocole)",
            "Teinture hybride",
            "Décoloration du surplus",
        ],
    },
    "ultime_4j": {
        "titre": "Formation Ultime — 4 jours",
        "prix": 2490,
        "acompte": 747,  # 30%
        "dates": [
            "• 27 → 30 avril 2026",
            "• 27 → 30 juillet 2026",
        ],
        "details": [
            "Mapping + Décoloration",
            "Henna Brow",
            "Browlift + teinture hybride",
            "Module business + organisation",
        ],
    },
    "ultime_sans_henna_4j": {
        "titre": "Ultime Sans Henna — 4 jours",
        "prix": 2190,
        "acompte": 657,  # 30%
        "dates": [
            "• Sur demande (contacte la formatrice)",
        ],
        "details": [
            "Mapping + Décoloration",
            "Browlift + teinture hybride",
            "Business / organisation",
        ],
    },
}

REGLES = (
    "📌 *Règles importantes*\n"
    "• Acompte obligatoire pour bloquer la place.\n"
    "• Le solde doit être réglé avant la formation.\n"
    "• Places limitées.\n"
)


# =========================
# UI: Keyboards
# =========================
def kb_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎓 Formations", callback_data="menu_formations")],
            [InlineKeyboardButton("📅 Prochaines dates", callback_data="menu_dates")],
            [InlineKeyboardButton("📩 Contact", callback_data="menu_contact")],
        ]
    )


def kb_formations_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Henna Brow (2j)", callback_data="formation:henna_2j")],
            [InlineKeyboardButton("Browlift (2j)", callback_data="formation:browlift_2j")],
            [InlineKeyboardButton("Ultime (4j)", callback_data="formation:ultime_4j")],
            [InlineKeyboardButton("Ultime sans Henna (4j)", callback_data="formation:ultime_sans_henna_4j")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="back_main")],
        ]
    )


def kb_back_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour menu", callback_data="back_main")]])


def kb_formation_actions(key: str) -> InlineKeyboardMarkup:
    f = FORMATIONS[key]
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"💳 Payer l’acompte ({f['acompte']}€)", url=PAYPAL_LINK)] if PAYPAL_LINK else [],
            [InlineKeyboardButton(f"💳 Payer en intégral ({f['prix']}€)", url=PAYPAL_LINK)] if PAYPAL_LINK else [],
            [InlineKeyboardButton("✅ J’ai déjà payé — envoyer ma preuve", callback_data=f"paid:{key}")],
            [InlineKeyboardButton("🕒 S’inscrire sur liste d’attente", callback_data=f"waitlist:{key}")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="menu_formations")],
        ]
    )


# =========================
# Handlers
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "✨ *Bienvenue chez Dream Sourcil*\n\nChoisissez une option :",
        reply_markup=kb_main_menu(),
        parse_mode=ParseMode.MARKDOWN,
    )


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "back_main":
        await query.edit_message_text(
            "✨ *Menu principal*\n\nChoisissez une option :",
            reply_markup=kb_main_menu(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "menu_formations":
        await query.edit_message_text(
            "🎓 *Formations Dream Sourcil*\n\nSélectionnez une formation :",
            reply_markup=kb_formations_menu(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "menu_dates":
        txt = (
            "📅 *Prochaines dates*\n\n"
            "• Formation Ultime : 27 → 30 avril 2026\n"
            "• Formation Ultime : 27 → 30 juillet 2026\n\n"
            "Les formations 2 jours sont sur demande : contactez la formatrice."
        )
        await query.edit_message_text(txt, reply_markup=kb_back_main(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "menu_contact":
        txt = (
            "📩 *Contact*\n\n"
            "Pour toute question, vous pouvez écrire ici.\n"
            "Ou contacter Dream Sourcil via Instagram : @dreamsourcil_marseille"
        )
        await query.edit_message_text(txt, reply_markup=kb_back_main(), parse_mode=ParseMode.MARKDOWN)
        return

    if data.startswith("formation:"):
        key = data.split(":", 1)[1].strip()
        if key not in FORMATIONS:
            await query.edit_message_text("❌ Formation introuvable.", reply_markup=kb_formations_menu())
            return

        f = FORMATIONS[key]
        details_lines: List[str] = [f"• {x}" for x in f["details"]]
        dates_lines: List[str] = f["dates"]

        texte = (
            f"✨ *{f['titre']}*\n\n"
            f"✅ *Inclus :*\n" + "\n".join(details_lines) + "\n\n"
            f"💶 *Prix :* {f['prix']}€\n"
            f"💳 *Acompte (30%) :* {f['acompte']}€\n\n"
            f"📅 *Dates :*\n" + "\n".join(dates_lines) + "\n\n"
            + REGLES
        )

        await query.edit_message_text(
            texte,
            reply_markup=kb_formation_actions(key),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return

    if data.startswith("paid:"):
        key = data.split(":", 1)[1].strip()
        context.user_data["paid_key"] = key

        await query.edit_message_text(
            "📸 Merci !\n\n"
            "Veuillez maintenant envoyer la **preuve de paiement** (capture PayPal ou reçu PDF).\n\n"
            "⚠️ Assurez-vous que le **montant**, le **nom** et la **formation** soient visibles.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data=f"formation:{key}")]]),
        )
        return

    if data.startswith("waitlist:"):
        key = data.split(":", 1)[1].strip()
        f = FORMATIONS.get(key, {})
        titre = f.get("titre", "cette formation")

        # Ici tu peux ajouter plus tard un stockage (Google Sheet, DB, etc.)
        await query.edit_message_text(
            f"🕒 *Liste d’attente*\n\n"
            f"Votre demande pour *{titre}* a bien été prise en compte.\n"
            "La formatrice vous recontactera si une place se libère. 🤍",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb_back_main(),
        )
        return


async def send_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    User sends photo or PDF after clicking 'paid:...'
    We forward to admin chat_id with caption.
    """
    key = context.user_data.get("paid_key")
    if not key:
        await update.message.reply_text(
            "⚠️ Pour envoyer une preuve, ouvrez d’abord une formation puis cliquez sur :\n"
            "✅ *J’ai déjà payé — envoyer ma preuve*",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if not CHAT_ID_ADMIN:
        await update.message.reply_text("⚠️ Admin non configuré (ID_CHAT_ADMIN manquant).")
        return

    user = update.effective_user
    f = FORMATIONS.get(key, {"titre": key})

    caption = (
        "✅ *Preuve de paiement reçue*\n"
        f"👤 Nom : {user.first_name or ''} {user.last_name or ''}\n"
        f"🆔 User ID : `{user.id}`\n"
        f"🎓 Formation : *{f.get('titre','')}*\n"
    )

    # Photo
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await context.bot.send_photo(
            chat_id=CHAT_ID_ADMIN,
            photo=file_id,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
        )

    # Document (PDF)
    elif update.message.document:
        file_id = update.message.document.file_id
        await context.bot.send_document(
            chat_id=CHAT_ID_ADMIN,
            document=file_id,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await update.message.reply_text("⚠️ Merci d’envoyer une capture (photo) ou un reçu (PDF).")
        return

    await update.message.reply_text(
        "✅ Merci ! Preuve bien reçue.\n"
        "La formatrice a été notifiée et reviendra vers vous pour la confirmation finale. 🤍"
    )

    # reset
    context.user_data.pop("paid_key", None)


def main() -> None:
    if not TOKEN:
        raise RuntimeError("TOKEN manquant. Ajoute la variable d’environnement TOKEN sur Railway.")

    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))

    # Callbacks
    app.add_handler(CallbackQueryHandler(on_callback))

    # Proof receiver (photo or pdf)
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.PDF, send_proof))

    app.run_polling()


if __name__ == "__main__":
    main()
