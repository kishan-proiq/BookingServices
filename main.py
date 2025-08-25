from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from datetime import datetime, timedelta
import random

from models.booking import Booking, BookingCreate, BookingUpdate, BookingResponse
from models.user import User, UserCreate, UserResponse
from models.service import Service, ServiceCreate, ServiceResponse
from database import engine, get_db
from crud import booking_crud, user_crud, service_crud
from utils.data_generator import generate_test_data
from utils.log_reader import read_logs
from utils.logger import configure_logging

# Create database tables
from models import Base
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Booking Services API",
    description="A comprehensive booking services API with proper HTTP status codes",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = configure_logging()

@app.middleware("http")
async def log_requests(request: Request, call_next):
	start = datetime.utcnow()
	try:
		response = await call_next(request)
		elapsed_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
		logger.info(
			f"HTTPRequest - {request.method} {request.url.path} - {response.status_code} - {elapsed_ms}ms"
		)
		return response
	except Exception as exc:
		elapsed_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
		logger.exception(
			f"APIError - Unhandled exception - {request.method} {request.url.path} - {elapsed_ms}ms"
		)
		raise

@app.on_event("startup")
async def startup_event():
    """Initialize test data on startup"""
    logger.info("Application startup initiated")
    await generate_test_data()
    logger.info("Application startup completed")

@app.get("/", response_model=dict)
async def root():
    """Root endpoint - returns API information"""
    payload = {
        "message": "Welcome to Booking Services API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "users": "/users",
            "services": "/services", 
            "bookings": "/bookings",
            "docs": "/docs"
        }
    }
    logger.info("Root endpoint accessed")
    return payload

# User endpoints
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db=Depends(get_db)):
    """Create a new user - Returns 201 on success"""
    try:
        db_user = await user_crud.create_user(db=db, user=user)
        logger.info(f"User created - id={db_user.id} email={db_user.email}")
        return db_user
    except Exception as e:
        logger.error(f"DatabaseError - Failed to create user - email={user.email} - error={e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )

@app.get("/users/", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    """Get all users - Returns 200 on success"""
    users = await user_crud.get_users(db=db, skip=skip, limit=limit)
    if not users:
        logger.warning("No users found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found"
        )
    return users

@app.get("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db=Depends(get_db)):
    """Get user by ID - Returns 200 on success, 404 if not found"""
    user = await user_crud.get_user(db=db, user_id=user_id)
    if not user:
        logger.error(f"LogicError - User not found - id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user

@app.put("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: UserCreate, db=Depends(get_db)):
    """Update user - Returns 200 on success, 404 if not found"""
    db_user = await user_crud.update_user(db=db, user_id=user_id, user=user)
    if not db_user:
        logger.error(f"LogicError - User not found for update - id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    logger.info(f"User updated - id={db_user.id}")
    return db_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db=Depends(get_db)):
    """Delete user - Returns 204 on success, 404 if not found"""
    success = await user_crud.delete_user(db=db, user_id=user_id)
    if not success:
        logger.error(f"LogicError - User not found for delete - id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    logger.info(f"User deleted - id={user_id}")
    return {"message": "User deleted successfully"}

# Service endpoints
@app.post("/services/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(service: ServiceCreate, db=Depends(get_db)):
    """Create a new service - Returns 201 on success"""
    try:
        db_service = await service_crud.create_service(db=db, service=service)
        logger.info(f"Service created - id={db_service.id} name={db_service.name}")
        return db_service
    except Exception as e:
        logger.error(f"DatabaseError - Failed to create service - name={service.name} - error={e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create service: {str(e)}"
        )

@app.get("/services/", response_model=List[ServiceResponse], status_code=status.HTTP_200_OK)
async def get_services(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    """Get all services - Returns 200 on success"""
    services = await service_crud.get_services(db=db, skip=skip, limit=limit)
    if not services:
        logger.warning("No services found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No services found"
        )
    return services

@app.get("/services/{service_id}", response_model=ServiceResponse, status_code=status.HTTP_200_OK)
async def get_service(service_id: int, db=Depends(get_db)):
    """Get service by ID - Returns 200 on success, 404 if not found"""
    service = await service_crud.get_service(db=db, service_id=service_id)
    if not service:
        logger.error(f"LogicError - Service not found - id={service_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID {service_id} not found"
        )
    return service

# Booking endpoints
@app.post("/bookings/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(booking: BookingCreate, db=Depends(get_db)):
    """Create a new booking - Returns 201 on success"""
    try:
        # Validate user and service exist
        user = await user_crud.get_user(db=db, user_id=booking.user_id)
        if not user:
            logger.error(f"LogicError - User not found (booking) - id={booking.user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {booking.user_id} not found"
            )
        
        service = await service_crud.get_service(db=db, service_id=booking.service_id)
        if not service:
            logger.error(f"LogicError - Service not found (booking) - id={booking.service_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with ID {booking.service_id} not found"
            )
        
        db_booking = await booking_crud.create_booking(db=db, booking=booking)
        logger.info(f"Booking created - id={db_booking.id} user_id={db_booking.user_id} service_id={db_booking.service_id}")
        return db_booking
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DatabaseError - Failed to create booking - user_id={booking.user_id} service_id={booking.service_id} - error={e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create booking: {str(e)}"
        )

@app.get("/bookings/", response_model=List[BookingResponse], status_code=status.HTTP_200_OK)
async def get_bookings(
    skip: int = 0, 
    limit: int = 100, 
    user_id: Optional[int] = None,
    service_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db=Depends(get_db)
):
    """Get all bookings with optional filters - Returns 200 on success"""
    bookings = await booking_crud.get_bookings(
        db=db, 
        skip=skip, 
        limit=limit,
        user_id=user_id,
        service_id=service_id,
        status_filter=status_filter
    )
    if not bookings:
        logger.warning("No bookings found for given criteria")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No bookings found with the specified criteria"
        )
    return bookings

@app.get("/bookings/{booking_id}", response_model=BookingResponse, status_code=status.HTTP_200_OK)
async def get_booking(booking_id: int, db=Depends(get_db)):
    """Get booking by ID - Returns 200 on success, 404 if not found"""
    booking = await booking_crud.get_booking(db=db, booking_id=booking_id)
    if not booking:
        logger.error(f"LogicError - Booking not found - id={booking_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    return booking

@app.put("/bookings/{booking_id}", response_model=BookingResponse, status_code=status.HTTP_200_OK)
async def update_booking(booking_id: int, booking: BookingUpdate, db=Depends(get_db)):
    """Update booking - Returns 200 on success, 404 if not found"""
    db_booking = await booking_crud.update_booking(db=db, booking_id=booking_id, booking=booking)
    if not db_booking:
        logger.error(f"LogicError - Booking not found for update - id={booking_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    logger.info(f"Booking updated - id={db_booking.id}")
    return db_booking

@app.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(booking_id: int, db=Depends(get_db)):
    """Delete booking - Returns 204 on success, 404 if not found"""
    success = await booking_crud.delete_booking(db=db, booking_id=booking_id)
    if not success:
        logger.error(f"LogicError - Booking not found for delete - id={booking_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    logger.info(f"Booking deleted - id={booking_id}")
    return {"message": "Booking deleted successfully"}

@app.patch("/bookings/{booking_id}/status", response_model=BookingResponse, status_code=status.HTTP_200_OK)
async def update_booking_status(booking_id: int, status: str, db=Depends(get_db)):
    """Update booking status - Returns 200 on success, 404 if not found"""
    valid_statuses = ["pending", "confirmed", "cancelled", "completed"]
    if status not in valid_statuses:
        logger.error(f"ValidationError - Invalid booking status - status={status}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    db_booking = await booking_crud.update_booking_status(db=db, booking_id=booking_id, status=status)
    if not db_booking:
        logger.error(f"LogicError - Booking not found for status update - id={booking_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    logger.info(f"Booking status updated - id={db_booking.id} status={db_booking.status}")
    return db_booking

# Statistics endpoints
@app.get("/stats/bookings", status_code=status.HTTP_200_OK)
async def get_booking_stats(db=Depends(get_db)):
    """Get booking statistics - Returns 200 on success"""
    stats = await booking_crud.get_booking_stats(db=db)
    logger.info("Stats requested - bookings")
    return stats

@app.get("/stats/services", status_code=status.HTTP_200_OK)
async def get_service_stats(db=Depends(get_db)):
    """Get service statistics - Returns 200 on success"""
    stats = await service_crud.get_service_stats(db=db)
    logger.info("Stats requested - services")
    return stats

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint - Returns 200 if healthy"""
    payload = {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    logger.info("Health check OK")
    return payload

# Logs endpoint (reads dummy_logs.log for testing/log review)
@app.get("/logs", status_code=status.HTTP_200_OK)
async def get_logs(
    level: Optional[str] = None,
    query: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
):
    """Return lines from dummy_logs.log with optional level filter and pagination."""
    lines, total = read_logs(level=level, query=query, offset=offset, limit=limit)
    if not lines:
        # Still 200 for observability tools; include total for clarity
        return {"total": total, "offset": offset, "limit": limit, "lines": []}
    return {"total": total, "offset": offset, "limit": limit, "lines": lines}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
