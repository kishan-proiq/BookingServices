from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_
from typing import List, Optional
from datetime import datetime, timedelta
from models.booking import Booking, BookingCreate, BookingUpdate, BookingStatus
from models.user import User
from models.service import Service
import logging

logger = logging.getLogger("BookingServicesAPI")

async def create_booking(db: Session, booking: BookingCreate) -> Booking:
    """Create a new booking"""
    db_booking = Booking(
        user_id=booking.user_id,
        service_id=booking.service_id,
        booking_date=booking.booking_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        notes=booking.notes,
        total_price=booking.total_price
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    logger.info(f"DB: booking created - id={db_booking.id} user_id={db_booking.user_id} service_id={db_booking.service_id}")
    return db_booking

async def get_booking(db: Session, booking_id: int) -> Optional[Booking]:
    """Get booking by ID"""
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    logger.debug(f"DB: booking fetch - id={booking_id} found={bool(b)}")
    return b

async def get_bookings(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None,
    service_id: Optional[int] = None,
    status_filter: Optional[str] = None
) -> List[Booking]:
    """Get all bookings with optional filters"""
    query = db.query(Booking)
    
    if user_id:
        query = query.filter(Booking.user_id == user_id)
    if service_id:
        query = query.filter(Booking.service_id == service_id)
    if status_filter:
        query = query.filter(Booking.status == status_filter)
    
    items = query.offset(skip).limit(limit).all()
    logger.debug(f"DB: bookings fetched - count={len(items)} skip={skip} limit={limit}")
    return items

async def get_bookings_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Booking]:
    """Get all bookings for a specific user"""
    return db.query(Booking).filter(Booking.user_id == user_id).offset(skip).limit(limit).all()

async def get_bookings_by_service(db: Session, service_id: int, skip: int = 0, limit: int = 100) -> List[Booking]:
    """Get all bookings for a specific service"""
    return db.query(Booking).filter(Booking.service_id == service_id).offset(skip).limit(limit).all()

async def get_bookings_by_date_range(
    db: Session, 
    start_date: datetime, 
    end_date: datetime,
    skip: int = 0, 
    limit: int = 100
) -> List[Booking]:
    """Get bookings within a date range"""
    return db.query(Booking).filter(
        and_(
            Booking.booking_date >= start_date,
            Booking.booking_date <= end_date
        )
    ).offset(skip).limit(limit).all()

async def update_booking(db: Session, booking_id: int, booking: BookingUpdate) -> Optional[Booking]:
    """Update booking"""
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if db_booking:
        for field, value in booking.dict(exclude_unset=True).items():
            setattr(db_booking, field, value)
        db.commit()
        db.refresh(db_booking)
        logger.info(f"DB: booking updated - id={db_booking.id}")
    return db_booking

async def update_booking_status(db: Session, booking_id: int, status: str) -> Optional[Booking]:
    """Update booking status"""
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if db_booking:
        db_booking.status = status
        db.commit()
        db.refresh(db_booking)
        logger.info(f"DB: booking status updated - id={db_booking.id} status={db_booking.status}")
    return db_booking

async def delete_booking(db: Session, booking_id: int) -> bool:
    """Delete booking"""
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if db_booking:
        db.delete(db_booking)
        db.commit()
        logger.info(f"DB: booking deleted - id={booking_id}")
        return True
    return False

async def check_availability(
    db: Session, 
    service_id: int, 
    start_time: datetime, 
    end_time: datetime,
    exclude_booking_id: Optional[int] = None
) -> bool:
    """Check if a service is available for a given time slot"""
    query = db.query(Booking).filter(
        and_(
            Booking.service_id == service_id,
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]),
            or_(
                and_(
                    Booking.start_time < end_time,
                    Booking.end_time > start_time
                )
            )
        )
    )
    
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    conflicting_bookings = query.count()
    return conflicting_bookings == 0

async def get_booking_stats(db: Session) -> dict:
    """Get booking statistics"""
    total_bookings = db.query(Booking).count()
    
    # Status distribution
    status_stats = db.query(
        Booking.status,
        func.count(Booking.id).label('count')
    ).group_by(Booking.status).all()
    
    # Monthly trends (last 12 months)
    current_date = datetime.utcnow()
    monthly_stats = []
    for i in range(12):
        month_start = current_date.replace(day=1) - timedelta(days=i*30)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        month_count = db.query(Booking).filter(
            and_(
                Booking.booking_date >= month_start,
                Booking.booking_date <= month_end
            )
        ).count()
        
        monthly_stats.append({
            "month": month_start.strftime("%Y-%m"),
            "count": month_count
        })
    
    # Revenue stats
    revenue_stats = db.query(
        func.sum(Booking.total_price).label('total_revenue'),
        func.avg(Booking.total_price).label('avg_booking_value')
    ).filter(Booking.status == BookingStatus.COMPLETED).first()
    
    return {
        "total_bookings": total_bookings,
        "status_distribution": {status: count for status, count in status_stats},
        "monthly_trends": monthly_stats,
        "revenue": {
            "total": float(revenue_stats.total_revenue) if revenue_stats.total_revenue else 0,
            "average_per_booking": float(revenue_stats.avg_booking_value) if revenue_stats.avg_booking_value else 0
        }
    }

async def get_user_booking_history(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Booking]:
    """Get complete booking history for a user"""
    return db.query(Booking).filter(
        and_(
            Booking.user_id == user_id,
            Booking.status.in_([BookingStatus.COMPLETED, BookingStatus.CANCELLED])
        )
    ).order_by(Booking.booking_date.desc()).offset(skip).limit(limit).all()
