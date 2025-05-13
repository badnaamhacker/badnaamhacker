from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, JSON, Float, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func
import datetime
import logging

from config import DATABASE_URL
from utils import generate_unique_id

logger = logging.getLogger(__name__)

Base = declarative_base()

# --- Models ---

class User(Base):
    __tablename__ = 'users'
    telegram_id = Column(Integer, primary_key=True, unique=True, autoincrement=False) # Telegram's User ID
    username = Column(String, nullable=True)
    first_name = Column(String)
    last_name = Column(String, nullable=True)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    dating_profile = relationship("DatingProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    freelancer_profile = relationship("FreelancerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    client_profile = relationship("ClientProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sent_likes = relationship("DatingLike", foreign_keys="DatingLike.liker_user_id", back_populates="liker", cascade="all, delete-orphan")
    received_likes = relationship("DatingLike", foreign_keys="DatingLike.liked_user_id", back_populates="liked", cascade="all, delete-orphan")
    sent_reports = relationship("Report", foreign_keys="Report.reporter_user_id", back_populates="reporter", cascade="all, delete-orphan")
    # received_reports relationship might be complex if needed

class DatingProfile(Base):
    __tablename__ = 'dating_profiles'
    profile_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.telegram_id'), unique=True, nullable=False) # One profile per user
    unique_bot_id = Column(String, unique=True, nullable=False, default=lambda: generate_unique_id("D"))
    name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    country = Column(String, nullable=False)
    custom_country = Column(String, nullable=True) # If country is 'Other'
    bio = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    city = Column(String, nullable=True) # Store city name if location sharing isn't used/preferred
    photo_file_ids = Column(JSON, nullable=True) # Store list of Telegram file IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="dating_profile")

class FreelancerProfile(Base):
    __tablename__ = 'freelancer_profiles'
    profile_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.telegram_id'), unique=True, nullable=False)
    unique_bot_id = Column(String, unique=True, nullable=False, default=lambda: generate_unique_id("F"))
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    country = Column(String, nullable=False)
    custom_country = Column(String, nullable=True)
    categories = Column(JSON, nullable=False) # List of selected categories/sub-categories
    skills_portfolio = Column(Text, nullable=True)
    rate = Column(String, nullable=True) # e.g., "$50/hour", "Project-based"
    experience = Column(String, nullable=True) # e.g., "Entry", "Intermediate", "Expert"
    photo_file_ids = Column(JSON, nullable=True) # Portfolio examples? or just profile pics
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="freelancer_profile")

class ClientProfile(Base):
    __tablename__ = 'client_profiles'
    profile_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.telegram_id'), unique=True, nullable=False)
    unique_bot_id = Column(String, unique=True, nullable=False, default=lambda: generate_unique_id("C"))
    name_company = Column(String, nullable=False)
    country = Column(String, nullable=False)
    custom_country = Column(String, nullable=True)
    project_details = Column(Text, nullable=False)
    budget = Column(String, nullable=True)
    timeline = Column(String, nullable=True)
    required_category = Column(JSON, nullable=False) # Can be multiple
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="client_profile")

class DatingLike(Base):
    __tablename__ = 'dating_likes'
    like_id = Column(Integer, primary_key=True)
    liker_user_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    liked_user_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    request_message = Column(Text, nullable=True)
    status = Column(String, default='pending') # pending, accepted, rejected
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    liker = relationship("User", foreign_keys=[liker_user_id], back_populates="sent_likes")
    liked = relationship("User", foreign_keys=[liked_user_id], back_populates="received_likes")


class Report(Base):
    __tablename__ = 'reports'
    report_id = Column(Integer, primary_key=True)
    reporter_user_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    reported_user_unique_id = Column(String, nullable=True) # Store the unique D_, F_, C_ ID
    report_message = Column(Text, nullable=False)
    status = Column(String, default='new') # new, resolved
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    reporter = relationship("User", foreign_keys=[reporter_user_id], back_populates="sent_reports")


# --- Database Setup ---
engine = create_engine(DATABASE_URL) #, echo=True) # Add echo=True for debugging SQL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Creates database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/checked.")

# --- CRUD Operations (Examples - Add more as needed) ---

def get_db():
    """Dependency function to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_user(db, user_data: dict):
    """Gets user by telegram_id or creates a new one."""
    user = db.query(User).filter(User.telegram_id == user_data['id']).first()
    if not user:
        user = User(
            telegram_id=user_data['id'],
            username=user_data.get('username'),
            first_name=user_data['first_name'],
            last_name=user_data.get('last_name')
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user: {user.telegram_id}")
    elif user.is_banned: # Check if banned on retrieval
        return None # Don't return banned users
    else: # Update username/name if changed
        updated = False
        if user.username != user_data.get('username'):
            user.username = user_data.get('username')
            updated = True
        if user.first_name != user_data.get('first_name'):
             user.first_name = user_data.get('first_name')
             updated = True
        if user.last_name != user_data.get('last_name'):
             user.last_name = user_data.get('last_name')
             updated = True
        if updated:
            db.commit()
            db.refresh(user)
    return user

def get_dating_profile(db, user_id):
    return db.query(DatingProfile).filter(DatingProfile.user_id == user_id).first()

def get_freelancer_profile(db, user_id):
     return db.query(FreelancerProfile).filter(FreelancerProfile.user_id == user_id).first()

def get_client_profile(db, user_id):
     return db.query(ClientProfile).filter(ClientProfile.user_id == user_id).first()

def save_dating_profile(db, user_id, profile_data):
    profile = get_dating_profile(db, user_id)
    if profile: # Update existing
        for key, value in profile_data.items():
            setattr(profile, key, value)
        profile.updated_at = datetime.datetime.now(datetime.timezone.utc)
    else: # Create new
        profile = DatingProfile(user_id=user_id, **profile_data)
        db.add(profile)
    db.commit()
    db.refresh(profile)
    logger.info(f"Saved/Updated Dating Profile for user {user_id}")
    return profile

# --- Add similar save/update functions for FreelancerProfile, ClientProfile ---
# --- Add functions for creating Likes, Reports, fetching profiles for browsing, etc. ---

def delete_profile(db, user_id, profile_type):
    deleted = False
    if profile_type == 'dating':
        profile = get_dating_profile(db, user_id)
        if profile:
            db.delete(profile)
            deleted = True
    elif profile_type == 'freelancer':
        profile = get_freelancer_profile(db, user_id)
        if profile:
            db.delete(profile)
            deleted = True
    # Add 'client' if needed
    if deleted:
        db.commit()
        logger.info(f"Deleted {profile_type} profile for user {user_id}")
    return deleted

def save_report(db, reporter_id, message, reported_unique_id=None):
    report = Report(
        reporter_user_id=reporter_id,
        report_message=message,
        reported_user_unique_id=reported_unique_id
    )
    db.add(report)
    db.commit()
    logger.info(f"Report saved from user {reporter_id}")
    return report

# Add functions for Admin Panel: get_stats, broadcast, manage_user, get_reports