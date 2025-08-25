from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_
from typing import List, Optional
from models.service import Service, ServiceCreate, ServiceUpdate
from models.booking import Booking
import logging

logger = logging.getLogger("BookingServicesAPI")

async def create_service(db: Session, service: ServiceCreate) -> Service:
    """Create a new service"""
    db_service = Service(
        name=service.name,
        description=service.description,
        price=service.price,
        duration_minutes=service.duration_minutes,
        category=service.category,
        is_available=service.is_available
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    logger.info(f"DB: service created - id={db_service.id} name={db_service.name}")
    return db_service

async def get_service(db: Session, service_id: int) -> Optional[Service]:
    """Get service by ID"""
    svc = db.query(Service).filter(Service.id == service_id).first()
    logger.debug(f"DB: service fetch - id={service_id} found={bool(svc)}")
    return svc

async def get_services(db: Session, skip: int = 0, limit: int = 100) -> List[Service]:
    """Get all services with pagination"""
    items = db.query(Service).offset(skip).limit(limit).all()
    logger.debug(f"DB: services fetched - count={len(items)} skip={skip} limit={limit}")
    return items

async def get_services_by_category(db: Session, category: str, skip: int = 0, limit: int = 100) -> List[Service]:
    """Get services by category"""
    return db.query(Service).filter(Service.category == category).offset(skip).limit(limit).all()

async def get_available_services(db: Session, skip: int = 0, limit: int = 100) -> List[Service]:
    """Get only available services"""
    return db.query(Service).filter(Service.is_available == True).offset(skip).limit(limit).all()

async def update_service(db: Session, service_id: int, service: ServiceUpdate) -> Optional[Service]:
    """Update service"""
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if db_service:
        for field, value in service.dict(exclude_unset=True).items():
            setattr(db_service, field, value)
        db.commit()
        db.refresh(db_service)
        logger.info(f"DB: service updated - id={db_service.id}")
    return db_service

async def delete_service(db: Session, service_id: int) -> bool:
    """Delete service"""
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if db_service:
        db.delete(db_service)
        db.commit()
        logger.info(f"DB: service deleted - id={service_id}")
        return True
    return False

async def search_services(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Service]:
    """Search services by name or description"""
    search_term = f"%{query}%"
    return db.query(Service).filter(
        and_(
            Service.is_available == True,
            or_(
                Service.name.ilike(search_term),
                Service.description.ilike(search_term)
            )
        )
    ).offset(skip).limit(limit).all()

async def get_service_stats(db: Session) -> dict:
    """Get service statistics"""
    total_services = db.query(Service).count()
    available_services = db.query(Service).filter(Service.is_available == True).count()
    
    # Get category distribution
    category_stats = db.query(
        Service.category,
        func.count(Service.id).label('count')
    ).group_by(Service.category).all()
    
    # Get price range
    price_stats = db.query(
        func.min(Service.price).label('min_price'),
        func.max(Service.price).label('max_price'),
        func.avg(Service.price).label('avg_price')
    ).first()
    
    return {
        "total_services": total_services,
        "available_services": available_services,
        "unavailable_services": total_services - available_services,
        "category_distribution": {cat: count for cat, count in category_stats},
        "price_range": {
            "min": float(price_stats.min_price) if price_stats.min_price else 0,
            "max": float(price_stats.max_price) if price_stats.max_price else 0,
            "average": float(price_stats.avg_price) if price_stats.avg_price else 0
        }
    }
