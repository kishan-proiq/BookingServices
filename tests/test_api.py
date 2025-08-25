import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import tempfile

from main import app
from database import get_db, Base
from models.user import User, UserCreate
from models.service import Service, ServiceCreate
from models.booking import Booking, BookingCreate

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

class TestHealthCheck:
    def test_health_check(self):
        """Test health check endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

class TestRootEndpoint:
    def test_root_endpoint(self):
        """Test root endpoint returns 200 with API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data

class TestUserEndpoints:
    def test_create_user_success(self, test_db):
        """Test creating a user returns 201"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "phone": "1234567890"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data

    def test_create_user_duplicate_email(self, test_db):
        """Test creating user with duplicate email returns 400"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser1",
            "full_name": "Test User 1",
            "phone": "1234567890"
        }
        # Create first user
        client.post("/users/", json=user_data)
        
        # Try to create second user with same email
        user_data["username"] = "testuser2"
        response = client.post("/users/", json=user_data)
        assert response.status_code == 400

    def test_get_users_empty(self, test_db):
        """Test getting users when none exist returns 404"""
        response = client.get("/users/")
        assert response.status_code == 404
        assert "No users found" in response.json()["detail"]

    def test_get_users_with_data(self, test_db):
        """Test getting users returns 200 with data"""
        # Create a user first
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "phone": "1234567890"
        }
        client.post("/users/", json=user_data)
        
        response = client.get("/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == user_data["email"]

    def test_get_user_by_id_success(self, test_db):
        """Test getting user by ID returns 200"""
        # Create a user first
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "phone": "1234567890"
        }
        create_response = client.post("/users/", json=user_data)
        user_id = create_response.json()["id"]
        
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id

    def test_get_user_by_id_not_found(self, test_db):
        """Test getting non-existent user returns 404"""
        response = client.get("/users/999")
        assert response.status_code == 404
        assert "User with ID 999 not found" in response.json()["detail"]

    def test_update_user_success(self, test_db):
        """Test updating user returns 200"""
        # Create a user first
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "phone": "1234567890"
        }
        create_response = client.post("/users/", json=user_data)
        user_id = create_response.json()["id"]
        
        # Update user
        update_data = {
            "email": "updated@example.com",
            "username": "updateduser",
            "full_name": "Updated User",
            "phone": "0987654321"
        }
        response = client.put(f"/users/{user_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == update_data["email"]

    def test_update_user_not_found(self, test_db):
        """Test updating non-existent user returns 404"""
        update_data = {
            "email": "updated@example.com",
            "username": "updateduser",
            "full_name": "Updated User"
        }
        response = client.put("/users/999", json=update_data)
        assert response.status_code == 404

    def test_delete_user_success(self, test_db):
        """Test deleting user returns 204"""
        # Create a user first
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "phone": "1234567890"
        }
        create_response = client.post("/users/", json=user_data)
        user_id = create_response.json()["id"]
        
        response = client.delete(f"/users/{user_id}")
        assert response.status_code == 204

    def test_delete_user_not_found(self, test_db):
        """Test deleting non-existent user returns 404"""
        response = client.delete("/users/999")
        assert response.status_code == 404

class TestServiceEndpoints:
    def test_create_service_success(self, test_db):
        """Test creating a service returns 201"""
        service_data = {
            "name": "Test Service",
            "description": "A test service",
            "price": 99.99,
            "duration_minutes": 60,
            "category": "Test",
            "is_available": True
        }
        response = client.post("/services/", json=service_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == service_data["name"]
        assert data["price"] == service_data["price"]

    def test_get_services_empty(self, test_db):
        """Test getting services when none exist returns 404"""
        response = client.get("/services/")
        assert response.status_code == 404

    def test_get_services_with_data(self, test_db):
        """Test getting services returns 200 with data"""
        # Create a service first
        service_data = {
            "name": "Test Service",
            "description": "A test service",
            "price": 99.99,
            "duration_minutes": 60,
            "category": "Test",
            "is_available": True
        }
        client.post("/services/", json=service_data)
        
        response = client.get("/services/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_service_by_id_success(self, test_db):
        """Test getting service by ID returns 200"""
        # Create a service first
        service_data = {
            "name": "Test Service",
            "description": "A test service",
            "price": 99.99,
            "duration_minutes": 60,
            "category": "Test",
            "is_available": True
        }
        create_response = client.post("/services/", json=service_data)
        service_id = create_response.json()["id"]
        
        response = client.get(f"/services/{service_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == service_id

    def test_get_service_by_id_not_found(self, test_db):
        """Test getting non-existent service returns 404"""
        response = client.get("/services/999")
        assert response.status_code == 404

class TestBookingEndpoints:
    def test_create_booking_success(self, test_db):
        """Test creating a booking returns 201"""
        # Create user and service first
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "phone": "1234567890"
        }
        user_response = client.post("/users/", json=user_data)
        user_id = user_response.json()["id"]
        
        service_data = {
            "name": "Test Service",
            "description": "A test service",
            "price": 99.99,
            "duration_minutes": 60,
            "category": "Test",
            "is_available": True
        }
        service_response = client.post("/services/", json=service_data)
        service_id = service_response.json()["id"]
        
        # Create booking
        from datetime import datetime, timedelta
        booking_date = datetime.utcnow() + timedelta(days=1)
        start_time = booking_date.replace(hour=10, minute=0)
        end_time = start_time + timedelta(minutes=60)
        
        booking_data = {
            "user_id": user_id,
            "service_id": service_id,
            "booking_date": booking_date.isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_price": 99,
            "notes": "Test booking"
        }
        
        response = client.post("/bookings/", json=booking_data)
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == user_id
        assert data["service_id"] == service_id

    def test_create_booking_user_not_found(self, test_db):
        """Test creating booking with non-existent user returns 404"""
        # Create service first
        service_data = {
            "name": "Test Service",
            "description": "A test service",
            "price": 99.99,
            "duration_minutes": 60,
            "category": "Test",
            "is_available": True
        }
        service_response = client.post("/services/", json=service_data)
        service_id = service_response.json()["id"]
        
        # Try to create booking with non-existent user
        from datetime import datetime, timedelta
        booking_date = datetime.utcnow() + timedelta(days=1)
        start_time = booking_date.replace(hour=10, minute=0)
        end_time = start_time + timedelta(minutes=60)
        
        booking_data = {
            "user_id": 999,  # Non-existent user
            "service_id": service_id,
            "booking_date": booking_date.isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_price": 99
        }
        
        response = client.post("/bookings/", json=booking_data)
        assert response.status_code == 404
        assert "User with ID 999 not found" in response.json()["detail"]

    def test_get_bookings_empty(self, test_db):
        """Test getting bookings when none exist returns 404"""
        response = client.get("/bookings/")
        assert response.status_code == 404

    def test_get_bookings_with_data(self, test_db):
        """Test getting bookings returns 200 with data"""
        # Create user, service, and booking first
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "phone": "1234567890"
        }
        user_response = client.post("/users/", json=user_data)
        user_id = user_response.json()["id"]
        
        service_data = {
            "name": "Test Service",
            "description": "A test service",
            "price": 99.99,
            "duration_minutes": 60,
            "category": "Test",
            "is_available": True
        }
        service_response = client.post("/services/", json=service_data)
        service_id = service_response.json()["id"]
        
        from datetime import datetime, timedelta
        booking_date = datetime.utcnow() + timedelta(days=1)
        start_time = booking_date.replace(hour=10, minute=0)
        end_time = start_time + timedelta(minutes=60)
        
        booking_data = {
            "user_id": user_id,
            "service_id": service_id,
            "booking_date": booking_date.isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_price": 99
        }
        client.post("/bookings/", json=booking_data)
        
        response = client.get("/bookings/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_booking_by_id_success(self, test_db):
        """Test getting booking by ID returns 200"""
        # Create user, service, and booking first
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "phone": "1234567890"
        }
        user_response = client.post("/users/", json=user_data)
        user_id = user_response.json()["id"]
        
        service_data = {
            "name": "Test Service",
            "description": "A test service",
            "price": 99.99,
            "duration_minutes": 60,
            "category": "Test",
            "is_available": True
        }
        service_response = client.post("/services/", json=service_data)
        service_id = service_response.json()["id"]
        
        from datetime import datetime, timedelta
        booking_date = datetime.utcnow() + timedelta(days=1)
        start_time = booking_date.replace(hour=10, minute=0)
        end_time = start_time + timedelta(minutes=60)
        
        booking_data = {
            "user_id": user_id,
            "service_id": service_id,
            "booking_date": booking_date.isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_price": 99
        }
        create_response = client.post("/bookings/", json=booking_data)
        booking_id = create_response.json()["id"]
        
        response = client.get(f"/bookings/{booking_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == booking_id

    def test_get_booking_by_id_not_found(self, test_db):
        """Test getting non-existent booking returns 404"""
        response = client.get("/bookings/999")
        assert response.status_code == 404

    def test_update_booking_status_success(self, test_db):
        """Test updating booking status returns 200"""
        # Create user, service, and booking first
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "phone": "1234567890"
        }
        user_response = client.post("/users/", json=user_data)
        user_id = user_response.json()["id"]
        
        service_data = {
            "name": "Test Service",
            "description": "A test service",
            "price": 99.99,
            "duration_minutes": 60,
            "category": "Test",
            "is_available": True
        }
        service_response = client.post("/services/", json=service_data)
        service_id = service_response.json()["id"]
        
        from datetime import datetime, timedelta
        booking_date = datetime.utcnow() + timedelta(days=1)
        start_time = booking_date.replace(hour=10, minute=0)
        end_time = start_time + timedelta(minutes=60)
        
        booking_data = {
            "user_id": user_id,
            "service_id": service_id,
            "booking_date": booking_date.isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_price": 99
        }
        create_response = client.post("/bookings/", json=booking_data)
        booking_id = create_response.json()["id"]
        
        # Update status
        response = client.patch(f"/bookings/{booking_id}/status?status=confirmed")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"

    def test_update_booking_status_invalid(self, test_db):
        """Test updating booking status with invalid status returns 400"""
        response = client.patch("/bookings/1/status?status=invalid_status")
        assert response.status_code == 400
        assert "Invalid status" in response.json()["detail"]

class TestStatisticsEndpoints:
    def test_get_booking_stats(self, test_db):
        """Test getting booking statistics returns 200"""
        response = client.get("/stats/bookings")
        assert response.status_code == 200
        data = response.json()
        assert "total_bookings" in data
        assert "status_distribution" in data

    def test_get_service_stats(self, test_db):
        """Test getting service statistics returns 200"""
        response = client.get("/stats/services")
        assert response.status_code == 200
        data = response.json()
        assert "total_services" in data
        assert "category_distribution" in data

if __name__ == "__main__":
    pytest.main([__file__])
