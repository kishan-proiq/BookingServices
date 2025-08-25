# Booking Services API

A comprehensive FastAPI-based booking services application with proper HTTP status codes and a large dataset for testing purposes.

## Features

- **Complete CRUD Operations**: Full Create, Read, Update, Delete operations for users, services, and bookings
- **Proper HTTP Status Codes**: 
  - 200: Success responses
  - 201: Created successfully
  - 204: Deleted successfully
  - 400: Bad request
  - 404: Not found
  - 500: Internal server error
- **Large Test Dataset**: Automatically generates 1000+ users, 500+ services, and 5000+ bookings
- **Comprehensive API**: RESTful endpoints with filtering, pagination, and statistics
- **Database Support**: SQLite for development/testing, PostgreSQL ready for production
- **Full Test Suite**: Comprehensive test coverage for all endpoints

## Project Structure

```
BookingServices/
├── main.py                 # FastAPI application entry point
├── database.py            # Database configuration and session management
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── models/               # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── base.py          # Base model class
│   ├── user.py          # User model and schemas
│   ├── service.py       # Service model and schemas
│   └── booking.py       # Booking model and schemas
├── crud/                 # Database CRUD operations
│   ├── __init__.py
│   ├── user_crud.py     # User database operations
│   ├── service_crud.py  # Service database operations
│   └── booking_crud.py  # Booking database operations
├── utils/                # Utility functions
│   ├── __init__.py
│   └── data_generator.py # Test data generation
└── tests/                # Test suite
    ├── __init__.py
    └── test_api.py      # API endpoint tests
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BookingServices
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- **Interactive API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative API Docs**: `http://localhost:8000/redoc` (ReDoc)

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### Users
- `POST /users/` - Create a new user (201)
- `GET /users/` - Get all users (200)
- `GET /users/{user_id}` - Get user by ID (200/404)
- `PUT /users/{user_id}` - Update user (200/404)
- `DELETE /users/{user_id}` - Delete user (204/404)

### Services
- `POST /services/` - Create a new service (201)
- `GET /services/` - Get all services (200)
- `GET /services/{service_id}` - Get service by ID (200/404)

### Bookings
- `POST /bookings/` - Create a new booking (201)
- `GET /bookings/` - Get all bookings with filters (200)
- `GET /bookings/{booking_id}` - Get booking by ID (200/404)
- `PUT /bookings/{booking_id}` - Update booking (200/404)
- `DELETE /bookings/{booking_id}` - Delete booking (204/404)
- `PATCH /bookings/{booking_id}/status` - Update booking status (200/404)

### Statistics
- `GET /stats/bookings` - Get booking statistics (200)
- `GET /stats/services` - Get service statistics (200)

## HTTP Status Codes

The API follows RESTful conventions with proper HTTP status codes:

- **200 OK**: Successful GET, PUT, PATCH requests
- **201 Created**: Successful POST requests
- **204 No Content**: Successful DELETE requests
- **400 Bad Request**: Invalid request data or parameters
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side errors

## Test Data Generation

The application automatically generates comprehensive test data on startup:

- **1000 Users**: With realistic names, emails, and phone numbers
- **500 Services**: Across 12 different categories
- **5000 Bookings**: Spanning 2 years with realistic scheduling

### Service Categories
- Healthcare
- Beauty & Wellness
- Fitness
- Education
- Technology
- Home Services
- Automotive
- Entertainment
- Professional Services
- Food & Dining
- Travel
- Shopping

## Testing

Run the comprehensive test suite:

```bash
pytest tests/ -v
```

The test suite covers:
- All API endpoints
- Success and failure scenarios
- HTTP status code validation
- Data validation
- Error handling

## Database

### Development (Default)
- **SQLite**: In-memory database for development and testing
- **File**: `test.db` for persistent storage

### Production
- **PostgreSQL**: Set `DATABASE_URL` environment variable
- **MySQL**: Modify database.py for MySQL support

## Environment Variables

```bash
# Database configuration
DATABASE_URL=postgresql://user:password@localhost/dbname

# For development (default)
DATABASE_URL=sqlite:///./test.db
```

## Usage Examples

### Create a User
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "phone": "1234567890"
  }'
```

### Create a Service
```bash
curl -X POST "http://localhost:8000/services/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Professional Massage",
    "description": "Relaxing therapeutic massage",
    "price": 89.99,
    "duration_minutes": 60,
    "category": "Beauty & Wellness",
    "is_available": true
  }'
```

### Create a Booking
```bash
curl -X POST "http://localhost:8000/bookings/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "service_id": 1,
    "booking_date": "2024-01-15T00:00:00",
    "start_time": "2024-01-15T10:00:00",
    "end_time": "2024-01-15T11:00:00",
    "total_price": 89,
    "notes": "First time customer"
  }'
```

### Get Bookings with Filters
```bash
# Get all bookings
curl "http://localhost:8000/bookings/"

# Get bookings for a specific user
curl "http://localhost:8000/bookings/?user_id=1"

# Get bookings for a specific service
curl "http://localhost:8000/bookings/?service_id=1"

# Get bookings with status filter
curl "http://localhost:8000/bookings/?status_filter=confirmed"

# Pagination
curl "http://localhost:8000/bookings/?skip=0&limit=10"
```

## Performance Features

- **Pagination**: All list endpoints support skip/limit pagination
- **Filtering**: Bookings can be filtered by user, service, and status
- **Database Indexing**: Proper indexes on frequently queried fields
- **Efficient Queries**: Optimized SQL queries with proper joins

## Error Handling

The API provides detailed error messages:

```json
{
  "detail": "User with ID 999 not found"
}
```

Common error scenarios:
- Resource not found (404)
- Invalid request data (400)
- Duplicate entries (400)
- Validation errors (400)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or issues:
1. Check the API documentation at `/docs`
2. Review the test cases for usage examples
3. Open an issue in the repository

## Future Enhancements

- Authentication and authorization
- Rate limiting
- Caching layer
- Webhook notifications
- Payment integration
- Email notifications
- Mobile app support
- Admin dashboard
