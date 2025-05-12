import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from a .env file if it exists

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE") # Replace with your token
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "YOUR_ADMIN_TELEGRAM_ID")) # Replace with your Telegram User ID
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot_database.db") # SQLite database file

# Optional: Freelance Categories (can be loaded from JSON/YAML too)
FREELANCE_CATEGORIES = {
    "Writing & Content Creation": [
        "Article Writing", "Blog Writing", "Copywriting", "Technical Writing",
        "SEO Content Writing", "Script Writing (YouTube, Ads)", "Translation",
        "Resume & Cover Letter Writing"
    ],
    "Graphic Design & Creative": [
        "Logo Design", "Poster/Flyer Design", "Social Media Post Design",
        "UI/UX Design", "Web Design", "Infographics", "Presentation Design",
        "T-Shirt & Merchandise Design"
    ],
    "Web Development & Programming": [
        "Frontend Development", "Backend Development", "Full-Stack Development",
        "WordPress Development", "Shopify/E-commerce Development", "App Development",
        "Bot Development", "API Integration"
    ],
     "Digital Marketing": [
        "SEO", "SMM", "SEM", "Email Marketing", "Affiliate Marketing",
        "Influencer Marketing", "Marketing Strategy", "Analytics"
    ],
    "Video & Animation": [
        "Video Editing", "Animation", "Explainer Videos", "Whiteboard Animation",
        "Motion Graphics", "YouTube Video Editing", "Reels/Shorts Editing",
        "Intro/Outro Creation"
    ],
    "Audio & Music": [
        "Voice Over", "Podcast Editing", "Audio Mixing/Mastering",
        "Music Composition", "Sound Effects", "Background Score"
    ],
    "Business & Admin Support": [
        "Virtual Assistant", "Data Entry", "Web Research", "Project Management",
        "Customer Support", "Email Handling", "CRM Management", "Lead Generation"
    ],
    "Finance & Legal": [
        "Accounting & Bookkeeping", "Financial Analysis", "Business Planning",
        "Tax Consulting", "Legal Writing", "Contract Drafting"
    ],
     "Data Science & Analytics": [
        "Data Analysis", "Machine Learning", "AI Projects", "Business Intelligence",
        "Data Visualization", "Data Entry & Scraping"
    ],
     "Education & Coaching": [
        "Online Tutoring", "Test Preparation", "Language Teaching",
        "Life Coaching", "Career Counseling", "Technical Training"
    ]
    # Add other main categories and sub-categories as needed
}

MAX_PROFILE_PHOTOS = 3
REQUEST_MESSAGE_LIMIT = 200