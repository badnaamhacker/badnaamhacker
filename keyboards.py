from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# --- Main Menu ---
def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ Create / View Profile ✨", callback_data='profile_menu')],
        # Maybe add Browse options directly here later
        [InlineKeyboardButton("⚙️ Settings & Help", callback_data='settings_help')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_profile_type_choice_keyboard():
     keyboard = [
        [InlineKeyboardButton("❤️ Dating Profile", callback_data='create_dating_profile_start')],
        [InlineKeyboardButton("💼 Freelancer Profile", callback_data='freelancer_role_choice')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='main_menu')],
    ]
     return InlineKeyboardMarkup(keyboard)

# --- Dating ---
def get_gender_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("👨 Male", callback_data='gender_male'),
            InlineKeyboardButton("👩 Female", callback_data='gender_female'),
            InlineKeyboardButton("⚧️ Other", callback_data='gender_other'),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_country_keyboard():
     keyboard = [
        [InlineKeyboardButton("🇮🇳 India", callback_data='country_india')],
        [InlineKeyboardButton("🌍 Other Country", callback_data='country_other')],
    ]
     return InlineKeyboardMarkup(keyboard)

def get_skip_keyboard(callback_data='skip_step'):
     return InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Skip this step", callback_data=callback_data)]])

def get_dating_profile_menu_keyboard(profile_exists=True):
    keyboard = []
    if profile_exists:
        keyboard.extend([
            [InlineKeyboardButton("👤 My Dating Profile", callback_data='view_dating_profile')],
            [InlineKeyboardButton("✏️ Edit Dating Profile", callback_data='edit_dating_profile_start')],
            [InlineKeyboardButton("💖 Browse Profiles", callback_data='browse_dating_start')],
            [InlineKeyboardButton("🗑️ Delete Dating Profile", callback_data='delete_dating_profile_confirm')],
        ])
    else:
         keyboard.append([InlineKeyboardButton("➕ Create Dating Profile", callback_data='create_dating_profile_start')])

    keyboard.append([InlineKeyboardButton("🔙 Back to Profile Choice", callback_data='profile_menu')])
    return InlineKeyboardMarkup(keyboard)


def get_dating_browse_preference_keyboard():
     keyboard = [
        [
            InlineKeyboardButton("👨 Show Male", callback_data='browse_pref_male'),
            InlineKeyboardButton("👩 Show Female", callback_data='browse_pref_female'),
            InlineKeyboardButton("🌈 Show Any", callback_data='browse_pref_any'),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data='dating_profile_menu')],
    ]
     return InlineKeyboardMarkup(keyboard)

def get_dating_browse_action_keyboard(current_profile_id):
    # current_profile_id is needed for callback data if required
    keyboard = [
        [
            InlineKeyboardButton("❤️ Like & Request", callback_data=f'like_{current_profile_id}'),
            InlineKeyboardButton("👎 Dislike", callback_data=f'dislike_{current_profile_id}'),
            InlineKeyboardButton("🆕 Next", callback_data='browse_next_dating'),
        ],
        [
             InlineKeyboardButton("🔄 Change Preference", callback_data='browse_dating_start'),
             InlineKeyboardButton("🔙 Back to Menu", callback_data='dating_profile_menu'),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_like_accept_reject_keyboard(liker_id, liked_id):
     keyboard = [
        [
            InlineKeyboardButton("✅ Accept Request", callback_data=f'accept_{liker_id}_{liked_id}'),
            InlineKeyboardButton("❌ Reject Request", callback_data=f'reject_{liker_id}_{liked_id}'),
        ]
    ]
     return InlineKeyboardMarkup(keyboard)


# --- Freelancer ---
def get_freelancer_role_choice_keyboard():
     keyboard = [
        [InlineKeyboardButton("🛠️ I Want to Work (Freelancer)", callback_data='create_freelancer_profile_start')],
        [InlineKeyboardButton("💰 I Want to Hire (Client)", callback_data='create_client_profile_start')],
        [InlineKeyboardButton("🔙 Back", callback_data='profile_menu')],
    ]
     return InlineKeyboardMarkup(keyboard)

# --- Add keyboards for Freelancer profile creation steps (categories, experience) ---
# --- Add keyboards for Freelancer browsing preferences and actions ---
# --- Add keyboards for Client profile creation steps ---

# --- Common ---
def get_confirmation_keyboard(yes_callback='confirm_yes', no_callback='confirm_no'):
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes", callback_data=yes_callback),
            InlineKeyboardButton("❌ No", callback_data=no_callback),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_button(callback_data='main_menu'):
     return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=callback_data)]])

# --- Admin ---
def get_admin_panel_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 Statistics", callback_data='admin_stats')],
        [InlineKeyboardButton("📢 Broadcast Message", callback_data='admin_broadcast_start')],
        [InlineKeyboardButton("👤 User Management", callback_data='admin_user_manage_start')],
        [InlineKeyboardButton("🚩 View Reports", callback_data='admin_view_reports')],
        [InlineKeyboardButton("🚪 Exit Admin Panel", callback_data='admin_exit')],
    ]
    return InlineKeyboardMarkup(keyboard)

# --- Add more keyboards as needed ---