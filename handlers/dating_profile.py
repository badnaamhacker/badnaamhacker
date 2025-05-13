import logging
from telegram import Update, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CommandHandler,
)

from database import get_db, get_or_create_user, save_dating_profile, get_dating_profile, delete_profile
from keyboards import (
    get_gender_keyboard, get_country_keyboard, get_skip_keyboard,
    get_dating_profile_menu_keyboard, get_confirmation_keyboard, get_back_button
)
from utils import is_valid_name, is_valid_age, format_profile_for_display, get_file_id_from_message
from config import MAX_PROFILE_PHOTOS

logger = logging.getLogger(__name__)

# States for ConversationHandler
(ASK_NAME, ASK_GENDER, ASK_AGE, ASK_COUNTRY, ASK_CUSTOM_COUNTRY, ASK_BIO,
 ASK_LOCATION, ASK_PHOTOS, CONFIRM_SAVE) = range(9)
EDIT_CHOICE, EDIT_FIELD = range(9, 11) # For editing

# --- Profile Creation Conversation ---

async def create_dating_profile_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the dating profile creation conversation."""
    query = update.callback_query
    user_id = update.effective_user.id
    context.user_data['profile_data'] = {'photos': []} # Initialize profile data and photos list
    context.user_data['edit_mode'] = False

    db = next(get_db())
    existing_profile = get_dating_profile(db, user_id)
    db.close()

    if existing_profile:
        await query.answer("You already have a dating profile.")
        await query.edit_message_text(
            text="You already have a Dating Profile. What would you like to do?",
            reply_markup=get_dating_profile_menu_keyboard(profile_exists=True)
        )
        return ConversationHandler.END # Or redirect to view/edit

    await query.answer()
    await query.edit_message_text(
        text="Okay, let's create your Dating Profile! ❤️\n\n"
             "First, please tell me your name.\n"
             "(Use your real first name or a nickname. Avoid using your full name, @username, or mobile number for privacy.)"
    )
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the name and asks for gender."""
    name = update.message.text.strip()
    if not is_valid_name(name):
        await update.message.reply_text(
            "⚠️ Please enter a valid name. Avoid using '@' symbols or phone numbers.\nWhat is your name?"
        )
        return ASK_NAME # Stay in the same state

    context.user_data['profile_data']['name'] = name
    logger.info(f"User {update.effective_user.id} entered name: {name}")
    await update.message.reply_text(
        f"Got it, {name}!\nNow, please select your gender:",
        reply_markup=get_gender_keyboard()
    )
    return ASK_GENDER

async def ask_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the gender and asks for age."""
    query = update.callback_query
    await query.answer()
    gender = query.data.split('_')[1] # e.g., 'gender_male' -> 'male'
    context.user_data['profile_data']['gender'] = gender.capitalize()
    logger.info(f"User {update.effective_user.id} selected gender: {gender}")

    await query.edit_message_text(
        text="Thanks! Now, please enter your age (must be between 18 and 99)."
    )
    return ASK_AGE

async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the age and asks for country."""
    age_text = update.message.text.strip()
    if not is_valid_age(age_text):
        await update.message.reply_text(
            "⚠️ Invalid age. Please enter a number between 18 and 99."
        )
        return ASK_AGE # Stay in the same state

    context.user_data['profile_data']['age'] = int(age_text)
    logger.info(f"User {update.effective_user.id} entered age: {age_text}")
    await update.message.reply_text(
        "Great! Which country are you from?",
        reply_markup=get_country_keyboard()
    )
    return ASK_COUNTRY

async def ask_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores country or asks for custom country name."""
    query = update.callback_query
    await query.answer()
    country_choice = query.data.split('_')[1] # 'country_india' or 'country_other'

    if country_choice == 'india':
        context.user_data['profile_data']['country'] = 'India'
        context.user_data['profile_data']['custom_country'] = None
        logger.info(f"User {update.effective_user.id} selected country: India")
        # Move to next step (Bio)
        await query.edit_message_text(
            text="Perfect. Now, tell us a little about yourself! (Optional)\n"
                 "Write a short bio (max 200 characters). You can type /skip to skip this.",
             reply_markup=get_skip_keyboard('skip_bio')
        )
        return ASK_BIO
    else: # Ask for custom country
        context.user_data['profile_data']['country'] = 'Other'
        logger.info(f"User {update.effective_user.id} selected Other country.")
        await query.edit_message_text(
            text="Okay, please type the name of your country:"
        )
        return ASK_CUSTOM_COUNTRY

async def ask_custom_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the custom country name."""
    custom_country = update.message.text.strip()
    if not custom_country:
         await update.message.reply_text("Please enter a valid country name.")
         return ASK_CUSTOM_COUNTRY

    context.user_data['profile_data']['custom_country'] = custom_country
    logger.info(f"User {update.effective_user.id} entered custom country: {custom_country}")
    # Move to next step (Bio)
    await update.message.reply_text(
        text="Perfect. Now, tell us a little about yourself! (Optional)\n"
             "Write a short bio (max 200 characters). You can type /skip to skip this.",
         reply_markup=get_skip_keyboard('skip_bio')
    )
    return ASK_BIO

async def ask_bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the bio (if provided) and asks for location."""
    bio = update.message.text.strip()
    if len(bio) > 200: # Assuming config.REQUEST_MESSAGE_LIMIT is 200
        await update.message.reply_text(
            f"⚠️ Your bio is too long (max 200 characters). Please shorten it or type /skip."
        )
        return ASK_BIO

    context.user_data['profile_data']['bio'] = bio
    logger.info(f"User {update.effective_user.id} entered bio (length {len(bio)}).")

    # Ask for Location
    await update.message.reply_text(
        "Next, please share your location. This helps connect you with people nearby.\n"
        "You can use the 'Send Location' button (provides more accuracy) or just type your City name.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📍 Send My Location", request_location=True)
            # We can add a skip button here too if location is optional
            # InlineKeyboardButton("➡️ Skip Location", callback_data='skip_location')
        ]]))
    return ASK_LOCATION

async def skip_bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the bio step."""
    query = update.callback_query
    await query.answer("Bio skipped.")
    context.user_data['profile_data']['bio'] = None
    logger.info(f"User {update.effective_user.id} skipped bio.")

    # Ask for Location
    await query.edit_message_text( # Use edit_message_text if called from skip button
        text="Next, please share your location. This helps connect you with people nearby.\n"
             "You can use the 'Send Location' button (provides more accuracy) or just type your City name.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📍 Send My Location", request_location=True)
            # InlineKeyboardButton("➡️ Skip Location", callback_data='skip_location')
        ]]))
    return ASK_LOCATION

async def ask_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the location (coordinates or city name) and asks for photos."""
    message = update.message
    location = message.location
    city_name = message.text # If user typed city name

    if location:
        context.user_data['profile_data']['latitude'] = location.latitude
        context.user_data['profile_data']['longitude'] = location.longitude
        # Optional: Reverse geocode to get city name from coordinates (needs external library like geopy)
        context.user_data['profile_data']['city'] = "Near provided location" # Placeholder
        logger.info(f"User {update.effective_user.id} shared coordinates: {location.latitude}, {location.longitude}")
    elif city_name:
        context.user_data['profile_data']['latitude'] = None
        context.user_data['profile_data']['longitude'] = None
        context.user_data['profile_data']['city'] = city_name.strip().title()
        logger.info(f"User {update.effective_user.id} entered city: {city_name.strip()}")
    else:
        await update.message.reply_text("Invalid input. Please send your location using the button or type your city name.")
        return ASK_LOCATION

    # Ask for Photos
    await update.message.reply_text(
        f"Almost done! Please upload 1 to {MAX_PROFILE_PHOTOS} photos for your profile.\n"
        f"Send them one by one. When you're finished, type /donephotos or just send the last one.",
        reply_markup=ReplyKeyboardRemove() # Remove location button if it was a reply keyboard
    )
    return ASK_PHOTOS


async def ask_photos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collects profile photos."""
    message = update.message
    user_data = context.user_data
    file_id = get_file_id_from_message(message)

    if file_id:
        if len(user_data['profile_data']['photos']) < MAX_PROFILE_PHOTOS:
            user_data['profile_data']['photos'].append(file_id)
            remaining = MAX_PROFILE_PHOTOS - len(user_data['profile_data']['photos'])
            logger.info(f"User {update.effective_user.id} added photo {len(user_data['profile_data']['photos'])}/{MAX_PROFILE_PHOTOS}. File ID: {file_id[:10]}...") # Log truncated ID

            if remaining > 0:
                await message.reply_text(
                    f"Photo {len(user_data['profile_data']['photos'])} received! You can add {remaining} more, or type /donephotos."
                )
                return ASK_PHOTOS # Stay in state to receive more photos
            else:
                await message.reply_text("Maximum photos received!")
                # Fall through to confirmation automatically after max photos
        else:
             await message.reply_text(f"You've already added the maximum of {MAX_PROFILE_PHOTOS} photos. Type /donephotos to continue.")
             # If max photos already reached, proceed to confirmation
             # This part might need refinement based on desired UX

    elif message.text and message.text.lower() == '/donephotos':
         if not user_data['profile_data']['photos']:
              await message.reply_text("You haven't added any photos yet. Please send at least one photo or type /skipphotos (if allowed).")
              # Add skip photos logic if desired
              return ASK_PHOTOS
         # Fall through to confirmation if /donephotos is typed
    else:
        await message.reply_text("Please send a photo or type /donephotos when finished.")
        return ASK_PHOTOS # Stay in state

    # --- Confirmation Step ---
    # (This part executes if max photos are reached or /donephotos is used)
    logger.info(f"User {update.effective_user.id} finished photo upload. Photos: {len(user_data['profile_data']['photos'])}")

    profile_summary = "Looks great! Here's your profile preview:\n\n"
    # Need to fetch the data correctly from user_data['profile_data']
    # Example (needs adjustment based on actual data structure):
    pd = user_data['profile_data']
    temp_display_data = {
         'name': pd.get('name'), 'age': pd.get('age'), 'gender': pd.get('gender'),
         'country': pd.get('country'), 'custom_country': pd.get('custom_country'),
         'bio': pd.get('bio'), 'city': pd.get('city', 'Location Set'),
         'photo_count': len(pd.get('photos', []))
    }
    profile_summary += f"👤 Name: {temp_display_data['name']}\n"
    profile_summary += f"🎂 Age: {temp_display_data['age']}\n"
    profile_summary += f"🚻 Gender: {temp_display_data['gender']}\n"
    profile_summary += f"🌍 Country: {temp_display_data.get('custom_country') or temp_display_data['country']}\n"
    if temp_display_data['bio']:
         profile_summary += f"📝 Bio: {temp_display_data['bio']}\n"
    profile_summary += f📍 Location: {temp_display_data['city']}\n"
    profile_summary += f"🖼️ Photos: {temp_display_data['photo_count']}\n\n"
    profile_summary += "Do you want to save this profile?"

    # Send preview photo if available
    if pd.get('photos'):
        try:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=pd['photos'][0], # Send the first photo as preview
                caption=profile_summary,
                reply_markup=get_confirmation_keyboard('save_dating_profile', 'cancel_dating_creation')
            )
        except Exception as e:
            logger.error(f"Error sending profile preview photo for user {update.effective_user.id}: {e}")
            # Fallback to text message if photo fails
            await update.message.reply_text(
                profile_summary,
                reply_markup=get_confirmation_keyboard('save_dating_profile', 'cancel_dating_creation')
            )
    else: # No photos uploaded
         await update.message.reply_text(
             profile_summary,
             reply_markup=get_confirmation_keyboard('save_dating_profile', 'cancel_dating_creation')
         )

    return CONFIRM_SAVE


async def save_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the profile data to the database."""
    query = update.callback_query
    await query.answer("Saving...")
    user_id = update.effective_user.id
    profile_data = context.user_data.get('profile_data', {})

    # Prepare data for DB (adjust keys to match model)
    db_data = {
        'name': profile_data.get('name'),
        'gender': profile_data.get('gender'),
        'age': profile_data.get('age'),
        'country': profile_data.get('country'),
        'custom_country': profile_data.get('custom_country'),
        'bio': profile_data.get('bio'),
        'latitude': profile_data.get('latitude'),
        'longitude': profile_data.get('longitude'),
        'city': profile_data.get('city'),
        'photo_file_ids': profile_data.get('photos') # Save list directly if using JSON
    }

    try:
        db = next(get_db())
        # Ensure user exists before saving profile
        user = get_or_create_user(db, update.effective_user.to_dict())
        if not user:
             raise Exception("User not found or banned.")

        saved_profile = save_dating_profile(db, user_id, db_data)
        db.close()
        logger.info(f"Dating profile saved successfully for user {user_id}. Unique ID: {saved_profile.unique_bot_id}")

        await query.edit_message_text(
            text=f"✅ Your Dating Profile has been created successfully!\nUnique ID: `{saved_profile.unique_bot_id}`\n\n"
                 f"What would you like to do next?",
            reply_markup=get_dating_profile_menu_keyboard(profile_exists=True),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error saving dating profile for user {user_id}: {e}")
        await query.edit_message_text(
            text="❌ An error occurred while saving your profile. Please try again later or contact support.",
            reply_markup=get_back_button('profile_menu') # Back to profile type choice
        )

    context.user_data.pop('profile_data', None) # Clean up user_data
    context.user_data.pop('edit_mode', None)
    return ConversationHandler.END


async def cancel_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the profile creation process."""
    query = update.callback_query
    await query.answer("Creation cancelled.")
    logger.info(f"User {update.effective_user.id} cancelled dating profile creation.")
    context.user_data.pop('profile_data', None)
    context.user_data.pop('edit_mode', None)
    await query.edit_message_text(
        text="Profile creation cancelled. What would you like to do?",
        reply_markup=get_profile_type_choice_keyboard() # Back to profile type choice
    )
    return ConversationHandler.END

async def timeout_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles conversation timeout."""
    user_id = context.user_data.get('_user_id_for_timeout') # Need to store user_id reliably
    if user_id:
         logger.warning(f"Conversation timed out for user {user_id}")
         context.user_data.pop('profile_data', None)
         context.user_data.pop('edit_mode', None)
         try:
              # Try sending a message if possible
              await context.bot.send_message(chat_id=user_id, text="Profile creation timed out. Please start again if you wish.")
         except Exception as e:
              logger.error(f"Failed to send timeout message to user {user_id}: {e}")
    # No return value needed for TIMEOUT state handler

# --- View Profile ---
async def view_dating_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
     query = update.callback_query
     user_id = update.effective_user.id
     db = next(get_db())
     profile = get_dating_profile(db, user_id)
     db.close()

     if not profile:
         await query.answer("Profile not found.", show_alert=True)
         await query.edit_message_text(
             text="You don't seem to have a dating profile yet.",
             reply_markup=get_dating_profile_menu_keyboard(profile_exists=False)
         )
         return

     await query.answer()
     # Format profile data for display using the utility function
     profile_dict = {c.name: getattr(profile, c.name) for c in profile.__table__.columns} # Convert SQLAlchemy object to dict
     profile_text = format_profile_for_display(profile_dict, profile_type="dating")

     if profile.photo_file_ids:
         try:
             await context.bot.send_photo(
                 chat_id=query.message.chat_id,
                 photo=profile.photo_file_ids[0], # Show first photo
                 caption="✨ **Your Dating Profile** ✨\n\n" + profile_text,
                 parse_mode='Markdown',
                 reply_markup=get_dating_profile_menu_keyboard(profile_exists=True)
             )
             # Delete the original message with the button after sending the photo
             await query.delete_message()
         except Exception as e:
              logger.error(f"Error sending profile photo for view {user_id}: {e}")
              # Fallback to text if photo fails
              await query.edit_message_text(
                   text="✨ **Your Dating Profile** ✨\n\n" + profile_text,
                   parse_mode='Markdown',
                   reply_markup=get_dating_profile_menu_keyboard(profile_exists=True)
              )
     else:
          await query.edit_message_text(
              text="✨ **Your Dating Profile** ✨\n\n" + profile_text,
              parse_mode='Markdown',
              reply_markup=get_dating_profile_menu_keyboard(profile_exists=True)
          )

# --- Delete Profile ---
async def delete_dating_profile_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="⚠️ **Are you absolutely sure?**\nDeleting your dating profile is p