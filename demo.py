#!/usr/bin/env python3
"""
Demo script for the Booking Services API
This script demonstrates how to use the API endpoints
"""
import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000"

def print_response(response, description):
    """Print formatted API response"""
    print(f"\n{'='*50}")
    print(f"{description}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def demo_health_check():
    """Demo health check endpoint"""
    print("Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check Response")

def demo_root_endpoint():
    """Demo root endpoint"""
    print("Testing Root Endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "Root Endpoint Response")

def demo_user_operations():
    """Demo user CRUD operations"""
    print("Testing User Operations...")
    
    # Create a user
    user_data = {
        "email": "demo.user@example.com",
        "username": "demouser",
        "full_name": "Demo User",
        "phone": "555-0123"
    }
    
    print("Creating user...")
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    print_response(response, "Create User Response")
    
    if response.status_code == 201:
        user_id = response.json()["id"]
        
        # Get user by ID
        print("Getting user by ID...")
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        print_response(response, "Get User Response")
        
        # Update user
        update_data = {
            "email": "updated.demo@example.com",
            "username": "updateduser",
            "full_name": "Updated Demo User",
            "phone": "555-9999"
        }
        print("Updating user...")
        response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data)
        print_response(response, "Update User Response")
        
        return user_id
    
    return None

def demo_service_operations():
    """Demo service CRUD operations"""
    print("Testing Service Operations...")
    
    # Create a service
    service_data = {
        "name": "Demo Massage Service",
        "description": "A relaxing demo massage service for testing",
        "price": 79.99,
        "duration_minutes": 60,
        "category": "Beauty & Wellness",
        "is_available": True
    }
    
    print("Creating service...")
    response = requests.post(f"{BASE_URL}/services/", json=service_data)
    print_response(response, "Create Service Response")
    
    if response.status_code == 201:
        service_id = response.json()["id"]
        
        # Get service by ID
        print("Getting service by ID...")
        response = requests.get(f"{BASE_URL}/services/{service_id}")
        print_response(response, "Get Service Response")
        
        return service_id
    
    return None

def demo_booking_operations(user_id, service_id):
    """Demo booking CRUD operations"""
    if not user_id or not service_id:
        print("Cannot create booking without user and service IDs")
        return None
    
    print("Testing Booking Operations...")
    
    # Create a booking
    tomorrow = datetime.utcnow() + timedelta(days=1)
    start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=60)
    
    booking_data = {
        "user_id": user_id,
        "service_id": service_id,
        "booking_date": tomorrow.date().isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_price": 79,
        "notes": "Demo booking for testing purposes"
    }
    
    print("Creating booking...")
    response = requests.post(f"{BASE_URL}/bookings/", json=booking_data)
    print_response(response, "Create Booking Response")
    
    if response.status_code == 201:
        booking_id = response.json()["id"]
        
        # Get booking by ID
        print("Getting booking by ID...")
        response = requests.get(f"{BASE_URL}/bookings/{booking_id}")
        print_response(response, "Get Booking Response")
        
        # Update booking status
        print("Updating booking status...")
        response = requests.patch(f"{BASE_URL}/bookings/{booking_id}/status?status=confirmed")
        print_response(response, "Update Booking Status Response")
        
        return booking_id
    
    return None

def demo_statistics():
    """Demo statistics endpoints"""
    print("Testing Statistics Endpoints...")
    
    # Get booking statistics
    print("Getting booking statistics...")
    response = requests.get(f"{BASE_URL}/stats/bookings")
    print_response(response, "Booking Statistics Response")
    
    # Get service statistics
    print("Getting service statistics...")
    response = requests.get(f"{BASE_URL}/stats/services")
    print_response(response, "Service Statistics Response")

def demo_filtering_and_pagination():
    """Demo filtering and pagination"""
    print("Testing Filtering and Pagination...")
    
    # Get users with pagination
    print("Getting users with pagination...")
    response = requests.get(f"{BASE_URL}/users/?skip=0&limit=5")
    print_response(response, "Users with Pagination Response")
    
    # Get services with pagination
    print("Getting services with pagination...")
    response = requests.get(f"{BASE_URL}/services/?skip=0&limit=5")
    print_response(response, "Services with Pagination Response")

def demo_error_handling():
    """Demo error handling scenarios"""
    print("Testing Error Handling...")
    
    # Try to get non-existent user
    print("Getting non-existent user...")
    response = requests.get(f"{BASE_URL}/users/99999")
    print_response(response, "Non-existent User Response")
    
    # Try to get non-existent service
    print("Getting non-existent service...")
    response = requests.get(f"{BASE_URL}/services/99999")
    print_response(response, "Non-existent Service Response")
    
    # Try to get non-existent booking
    print("Getting non-existent booking...")
    response = requests.get(f"{BASE_URL}/bookings/99999")
    print_response(response, "Non-existent Booking Response")

def main():
    """Main demo function"""
    print("🚀 Booking Services API Demo")
    print("Make sure the API server is running on http://localhost:8000")
    print("Press Enter to continue...")
    input()
    
    try:
        # Test basic endpoints
        demo_health_check()
        demo_root_endpoint()
        
        # Test CRUD operations
        user_id = demo_user_operations()
        service_id = demo_service_operations()
        booking_id = demo_booking_operations(user_id, service_id)
        
        # Test statistics
        demo_statistics()
        
        # Test filtering and pagination
        demo_filtering_and_pagination()
        
        # Test error handling
        demo_error_handling()
        
        print("\n🎉 Demo completed successfully!")
        print(f"Created User ID: {user_id}")
        print(f"Created Service ID: {service_id}")
        print(f"Created Booking ID: {booking_id}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error during demo: {e}")

if __name__ == "__main__":
    main()
