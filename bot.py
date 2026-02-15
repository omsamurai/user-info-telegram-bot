import os
import logging
from datetime import datetime, UTC

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in .env file")

# Configure logging: show only errors
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.ERROR
)

# Silence noisy loggers from telegram/httpx
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("telegram").setLevel(logging.CRITICAL)

BOT_INFO = {
    "name": "User Info Bot",
    "version": "1.0.0",
    "language": "Python",
    "developer_name": "Om",
    "developer_link": "https://t.me/unseen_crafts",
    "github_link": "https://github.com/omsamurai/user-info-telegram-bot/"
}

EMOJI = {
    "user": "5785435816612335146",
    "info": "5988080534075477912",
    "help": "5368324170671202288",
    "robot": "5787226908169081139",
    "question_mark": "5956290878367599999",
    "done": "5987621191618138109",
    "time": "5956332612564815461",
    "thank_you": "5850366771416009517",
    "send": "5879725711857553047",
    "circle": "5879893730978173215",
    "eyes": "5877296091807878935",
    "pen": "5877275733662896581",
    "alien": "5877556353941114265"
}

async def safe_reply(update: Update, text: str, **kwargs):
    if update.message:
        await update.message.reply_text(text, reply_to_message_id=update.message.message_id, **kwargs)
    else:
        await update.effective_chat.send_message(text, **kwargs)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f'<tg-emoji emoji-id="{EMOJI["robot"]}">🤖</tg-emoji> <b>Welcome!</b>'
    await safe_reply(update, text, parse_mode="HTML")

    explore_text = (
        f'<tg-emoji emoji-id="{EMOJI["eyes"]}">👀</tg-emoji> '
        f'Use <b>/help</b> command to explore'
    )
    await update.effective_chat.send_message(explore_text, parse_mode="HTML")

async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f'<tg-emoji emoji-id="{EMOJI["user"]}">👤</tg-emoji> <b>Your Info</b>\n\n'
        f'<b>ID:</b> <code>{user.id}</code>\n'
        f'<b>Name:</b> {user.full_name}\n'
        f'<b>Username:</b> @{user.username if user.username else "Not set"}\n'
        f'<b>Bot:</b> {"Yes" if user.is_bot else "No"}\n'
        f'<b>Language:</b> {user.language_code or "Unknown"}\n\n'
        f'<tg-emoji emoji-id="{EMOJI["time"]}">⏳</tg-emoji> <b>Time:</b> {datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")} UTC'
    )
    await safe_reply(update, text, parse_mode="HTML")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = (
            f'<tg-emoji emoji-id="{EMOJI["info"]}">ℹ️</tg-emoji> <b>About This Bot</b>\n\n'
            f'<tg-emoji emoji-id="{EMOJI["circle"]}">⚪️</tg-emoji> <b>Name:</b> {BOT_INFO["name"]}\n'
            f'<tg-emoji emoji-id="{EMOJI["circle"]}">⚪️</tg-emoji> <b>Version:</b> {BOT_INFO["version"]}\n'
            f'<tg-emoji emoji-id="{EMOJI["circle"]}">⚪️</tg-emoji> <b>Language:</b> {BOT_INFO["language"]}'
        )

        keyboard = [
            [InlineKeyboardButton("👤 Developer", url=BOT_INFO["developer_link"])],
            [InlineKeyboardButton("💻 GitHub", url=BOT_INFO["github_link"])]
        ]

        if update.message:
            await update.message.reply_text(
                text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard),
                reply_to_message_id=update.message.message_id
            )
        else:
            await update.effective_chat.send_message(
                text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception:
        logging.exception("Error in /about command")
        fallback = "⚠️ Something went wrong while showing bot info."
        await safe_reply(update, fallback)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f'<tg-emoji emoji-id="{EMOJI["question_mark"]}">❕</tg-emoji> <b>Need Help</b>\n\n'
        "<b>Available Commands</b>\n"
        f'/start — Start the bot\n'
        f'/me — Show your basic user info\n'
        f'/about — About the bot\n'
        f'/help — Show this help message\n\n'
        f'<tg-emoji emoji-id="{EMOJI["thank_you"]}">🙏🏻</tg-emoji> Thank you for using our bot!'
    )
    await safe_reply(update, text, parse_mode="HTML")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.exception("Update %s caused error", update)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("⚠️ An unexpected error occurred. Please try again later.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("me", me))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("help", help_command))

    app.add_error_handler(error_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
