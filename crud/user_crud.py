from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from models.user import User, UserCreate, UserUpdate
from models.booking import Booking
import logging

logger = logging.getLogger("BookingServicesAPI")

async def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"DB: user created - id={db_user.id} email={db_user.email}")
    return db_user

async def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        logger.debug(f"DB: user fetched - id={user_id}")
    else:
        logger.debug(f"DB: user not found - id={user_id}")
    return user

async def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

async def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

async def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination"""
    users = db.query(User).offset(skip).limit(limit).all()
    logger.debug(f"DB: users fetched - count={len(users)} skip={skip} limit={limit}")
    return users

async def update_user(db: Session, user_id: int, user: UserCreate) -> Optional[User]:
    """Update user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        for field, value in user.dict().items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
        logger.info(f"DB: user updated - id={db_user.id}")
    return db_user

async def delete_user(db: Session, user_id: int) -> bool:
    """Delete user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        logger.info(f"DB: user deleted - id={user_id}")
        return True
    return False

async def get_users_with_bookings(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get users with their booking count"""
    return db.query(User).offset(skip).limit(limit).all()

async def get_user_stats(db: Session) -> dict:
    """Get user statistics"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    users_with_bookings = db.query(User).join(Booking).distinct().count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "users_with_bookings": users_with_bookings,
        "inactive_users": total_users - active_users
    }
