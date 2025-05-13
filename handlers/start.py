import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from database import get_or_create_user, get_db, get_dating_profile, get_freelancer_profile # etc
from keyboards import get_main_menu_keyboard, get_profile_type_choice_keyboard, get_dating_profile_menu_keyboard, get_freelancer_role_choice_keyboard # etc
from config import ADMIN_USER_ID

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user_data = update.effective_user.to_dict()
    db_session = next(get_db())
    user = get_or_create_user(db_session, user_data)
    db_session.close()

    if not user: # Should not happen unless banned, but check anyway
        await update.message.reply_text("Sorry, you cannot use this bot.")
        return

    logger.info(f"User {user.telegram_id} ({user.username}) started the bot.")

    welcome_text = (
        f"Welcome to ConnectSphere Bot, {update.effective_user.first_name}! 👋\n\n"
        "I can help you connect with new people (❤️ Dating) or find/post freelancing opportunities (💼 Freelancing).\n\n"
        "Use the buttons below to get started."
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu_keyboard())

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles 'main_menu' callback to show the main menu."""
    query = update.callback_query
    await query.answer()
    welcome_text = "🏠 Main Menu:\nChoose an option:"
    await query.edit_message_text(text=welcome_text, reply_markup=get_main_menu_keyboard())

async def profile_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles 'profile_menu' callback."""
    query = update.callback_query
    await query.answer()
    # Check if user has any profile already (optional, maybe direct to choice)
    text = "Select the type of profile you want to manage or create:"
    await query.edit_message_text(text=text, reply_markup=get_profile_type_choice_keyboard())

async def freelancer_role_choice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles 'freelancer_role_choice' callback."""
    query = update.callback_query
    await query.answer()
    text = "Are you looking to offer your services or hire someone?"
    await query.edit_message_text(text=text, reply_markup=get_freelancer_role_choice_keyboard())


# --- Settings/Help (Placeholder) ---
async def settings_help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles 'settings_help' callback."""
    query = update.callback_query
    await query.answer()
    text = (
        "⚙️ **Settings & Help**\n\n"
        "Available Commands:\n"
        "`/delete` - Delete your profile(s).\n"
        "`/report <message>` - Report an issue or a user to the admin.\n"
        "`/start` - Show the main menu.\n\n"
        "Use the main menu buttons to navigate profiles."
        # Add privacy policy link, contact info etc.
    )
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data='main_menu')]]),
        parse_mode='Markdown'
    )


# --- Handlers Registration ---
start_handler = CommandHandler('start', start)
main_menu_handler = CallbackQueryHandler(main_menu_callback, pattern='^main_menu$')
profile_menu_handler = CallbackQueryHandler(profile_menu_callback, pattern='^profile_menu$')
freelancer_role_choice_handler = CallbackQueryHandler(freelancer_role_choice_callback, pattern='^freelancer_role_choice$')
settings_help_handler = CallbackQueryHandler(settings_help_callback, pattern='^settings_help$')

# Export handlers to be added in bot.py
HANDLERS = [start_handler, main_menu_handler, profile_menu_handler, freelancer_role_choice_handler, settings_help_handler]