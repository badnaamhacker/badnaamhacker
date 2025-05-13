import uuid
import re

def generate_unique_id(prefix="U"):
    """Generates a short, unique ID."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def is_valid_name(name):
    """Checks if the name is potentially valid (doesn't start with @ or look like a phone number)."""
    if not name or name.startswith('@'):
        return False
    # Basic check for sequence of digits (might need refinement)
    if re.fullmatch(r'\+?\d[\d\s-]{7,}', name): # Check for phone-like patterns
         return False
    return True

def is_valid_age(age_text):
    """Checks if age is a number between 18 and 99."""
    try:
        age = int(age_text)
        return 18 <= age <= 99
    except ValueError:
        return False

def format_profile_for_display(profile_data, profile_type="dating"):
    """Formats profile data into a readable string."""
    # This needs to be implemented based on how you store data
    # Example:
    text = f"👤 **{profile_data.get('name', 'N/A')}** ({profile_data.get('age', 'N/A')})\n"
    text += f"🚻 Gender: {profile_data.get('gender', 'N/A')}\n"
    text += f"🌍 Country: {profile_data.get('custom_country') or profile_data.get('country', 'N/A')}\n"
    if 'bio' in profile_data and profile_data['bio']:
         text += f"📝 Bio: {profile_data['bio']}\n"
    # Add Freelancer specific fields if profile_type == 'freelancer'
    # Add Client specific fields if profile_type == 'client'
    if 'unique_bot_id' in profile_data:
        text += f"\n🆔 Unique ID: `{profile_data['unique_bot_id']}` (For reporting)"
    return text

def get_file_id_from_message(message):
    """Extracts the highest resolution photo file_id from a message."""
    if message.photo:
        return message.photo[-1].file_id
    # Add checks for other media types if needed (documents, video for portfolio?)
    return None