from faker import Faker
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from models.service import Service
from models.booking import Booking, BookingStatus
from datetime import datetime, timedelta
import random
import asyncio
import logging

fake = Faker()

# Service categories and sample data
SERVICE_CATEGORIES = [
    "Healthcare", "Beauty & Wellness", "Fitness", "Education", 
    "Technology", "Home Services", "Automotive", "Entertainment",
    "Professional Services", "Food & Dining", "Travel", "Shopping"
]

SERVICE_NAMES = {
    "Healthcare": [
        "Doctor Consultation", "Dental Checkup", "Physiotherapy", "Massage Therapy",
        "Eye Examination", "Blood Test", "Vaccination", "Health Screening"
    ],
    "Beauty & Wellness": [
        "Haircut & Styling", "Facial Treatment", "Manicure & Pedicure", "Spa Massage",
        "Makeup Application", "Hair Coloring", "Skin Treatment", "Nail Art"
    ],
    "Fitness": [
        "Personal Training", "Yoga Class", "Pilates Session", "Swimming Lesson",
        "Dance Class", "Boxing Training", "CrossFit Session", "Meditation Class"
    ],
    "Education": [
        "Tutoring Session", "Language Class", "Music Lesson", "Art Workshop",
        "Cooking Class", "Photography Lesson", "Coding Bootcamp", "Test Preparation"
    ],
    "Technology": [
        "Computer Repair", "Software Installation", "Website Development", "Data Recovery",
        "Network Setup", "IT Consultation", "Hardware Upgrade", "Virus Removal"
    ],
    "Home Services": [
        "House Cleaning", "Plumbing Service", "Electrical Work", "Gardening",
        "Painting", "Carpentry", "Moving Service", "Security Installation"
    ],
    "Automotive": [
        "Car Wash", "Oil Change", "Tire Rotation", "Brake Service",
        "Engine Tune-up", "Car Detailing", "Battery Replacement", "AC Service"
    ],
    "Entertainment": [
        "Event Planning", "Photography", "Videography", "DJ Service",
        "Live Music", "Party Decoration", "Catering", "Entertainment Booking"
    ],
    "Professional Services": [
        "Legal Consultation", "Accounting Service", "Marketing Consultation", "HR Services",
        "Business Planning", "Financial Advisory", "Tax Preparation", "Insurance Services"
    ],
    "Food & Dining": [
        "Catering Service", "Food Delivery", "Cooking Class", "Wine Tasting",
        "Restaurant Booking", "Chef Service", "Food Photography", "Recipe Development"
    ],
    "Travel": [
        "Travel Planning", "Hotel Booking", "Flight Booking", "Tour Guide",
        "Car Rental", "Travel Insurance", "Visa Services", "Adventure Tours"
    ],
    "Shopping": [
        "Personal Shopping", "Gift Wrapping", "Product Consultation", "Shopping Assistant",
        "Fashion Styling", "Interior Design", "Jewelry Consultation", "Electronics Setup"
    ]
}

async def generate_users(db: Session, count: int = 1000) -> list:
    """Generate fake users"""
    users = []
    for i in range(count):
        user = User(
            email=fake.unique.email(),
            username=fake.unique.user_name(),
            full_name=fake.name(),
            phone=fake.phone_number(),
            is_active=random.choice([True, True, True, False])  # 75% active
        )
        users.append(user)
    
    db.add_all(users)
    db.commit()
    logging.getLogger("BookingServicesAPI").info(f"DataGen: users generated - count={len(users)}")
    return users

async def generate_services(db: Session, count: int = 500) -> list:
    """Generate fake services"""
    services = []
    for i in range(count):
        category = random.choice(SERVICE_CATEGORIES)
        service_names = SERVICE_NAMES.get(category, ["Generic Service"])
        name = random.choice(service_names)
        
        service = Service(
            name=f"{name} #{i+1}",
            description=fake.text(max_nb_chars=200),
            price=round(random.uniform(20, 500), 2),
            duration_minutes=random.choice([30, 45, 60, 90, 120, 180]),
            category=category,
            is_available=random.choice([True, True, True, False])  # 75% available
        )
        services.append(service)
    
    db.add_all(services)
    db.commit()
    logging.getLogger("BookingServicesAPI").info(f"DataGen: services generated - count={len(services)}")
    return services

async def generate_bookings(db: Session, users: list, services: list, count: int = 5000) -> list:
    """Generate fake bookings"""
    bookings = []
    
    # Generate bookings over the last 2 years
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=730)
    
    for i in range(count):
        # Random user and service
        user = random.choice(users)
        service = random.choice(services)
        
        # Random booking date within range
        days_offset = random.randint(0, 730)
        booking_date = start_date + timedelta(days=days_offset)
        
        # Random time within the day (9 AM to 6 PM)
        hour = random.randint(9, 18)
        minute = random.choice([0, 15, 30, 45])
        start_time = booking_date.replace(hour=hour, minute=minute)
        
        # End time based on service duration
        end_time = start_time + timedelta(minutes=service.duration_minutes)
        
        # Random status with weighted distribution
        status_weights = {
            "completed": 0.4,
            "confirmed": 0.3,
            "pending": 0.2,
            "cancelled": 0.1
        }
        status = random.choices(
            list(status_weights.keys()),
            weights=list(status_weights.values())
        )[0]
        
        # Calculate total price (service price + random variation)
        price_variation = random.uniform(0.8, 1.2)
        total_price = int(service.price * price_variation)
        
        booking = Booking(
            user_id=user.id,
            service_id=service.id,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            status=status,
            notes=fake.text(max_nb_chars=100) if random.random() < 0.3 else None,
            total_price=total_price
        )
        bookings.append(booking)
    
    db.add_all(bookings)
    db.commit()
    logging.getLogger("BookingServicesAPI").info(f"DataGen: bookings generated - count={len(bookings)}")
    return bookings

async def generate_test_data():
    """Generate comprehensive test data for the application"""
    logging.getLogger("BookingServicesAPI").info("DataGen: starting")
    
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            logging.getLogger("BookingServicesAPI").info("DataGen: existing data detected, skipping")
            return
        
        # Generate data
        users = await generate_users(db, count=1000)
        services = await generate_services(db, count=500)
        bookings = await generate_bookings(db, users, services, count=5000)
        
        logging.getLogger("BookingServicesAPI").info("DataGen: completed successfully")
        logging.getLogger("BookingServicesAPI").info(f"DataGen: totals users={len(users)} services={len(services)} bookings={len(bookings)}")
        
    except Exception as e:
        logging.getLogger("BookingServicesAPI").error(f"DataGen: error generating data - {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(generate_test_data())
