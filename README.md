# Student Platform API

A Flask-based REST API for managing students and their university applications with automatic calculation of highest status and intake based on application hierarchy.

## Features

- **Student Management**: Full CRUD operations for student records
- **Application Management**: Full CRUD operations for university applications
- **Business Logic**: Automatic calculation of highest status and intake based on application hierarchy
- **Status Hierarchy**: 6-tier status system with proper weightage
- **Data Validation**: Comprehensive input validation and error handling
- **Pagination**: Built-in pagination for all list endpoints
- **Production Ready**: Docker support, health checks, and proper error handling
- **Testing**: Comprehensive test suite with pytest
- **Documentation**: Complete API documentation and Postman collection

## Technology Stack

- **Backend**: Flask (Python 3.11)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Testing**: pytest
- **Containerization**: Docker & Docker Compose
- **Web Server**: Gunicorn + Nginx

## Project Structure

```
student-platform/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── database_utils.py               # Database management utilities
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose setup
├── nginx.conf                      # Nginx configuration
├── models/                         # Database models
│   ├── __init__.py
│   ├── student.py                  # Student model
│   └── application.py              # Application model
├── services/                       # Business logic layer
│   ├── __init__.py
│   ├── student_service.py          # Student business logic
│   └── application_service.py      # Application business logic
├── routes/                         # API routes
│   ├── __init__.py
│   ├── student_routes.py           # Student endpoints
│   ├── application_routes.py       # Application endpoints
│   └── health_routes.py            # Health check endpoint
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── conftest.py                 # Test configuration
│   ├── test_student_routes.py      # Student route tests
│   ├── test_application_routes.py  # Application route tests
│   └── test_business_logic.py      # Business logic tests
├── API_DOCUMENTATION.md            # Complete API documentation
├── Student_Platform_API.postman_collection.json  # Postman collection
└── README.md                       # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Docker & Docker Compose (optional)

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd student-platform
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**
   ```bash
   # Make sure PostgreSQL is running
   # Update the connection string in config.py if needed
   python database_utils.py reset
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the API**
   - API Base URL: `http://localhost:5005`
   - Health Check: `http://localhost:5005/api/health/`

### Option 2: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd student-platform
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the API**
   - API Base URL: `http://localhost:5005`
   - With Nginx: `http://localhost:80`

## API Endpoints

### Health Check
- `GET /api/health/` - Check API and database status

### Students
- `POST /api/students/` - Create a new student
- `GET /api/students/` - Get all students (paginated)
- `GET /api/students/{id}` - Get a specific student
- `PUT /api/students/{id}` - Update a student
- `DELETE /api/students/{id}` - Delete a student
- `GET /api/students/{id}/applications` - Get student's applications
- `GET /api/students/{id}/highest-status` - Get student's highest status and intake

### Applications
- `POST /api/applications/` - Create a new application
- `GET /api/applications/` - Get all applications (paginated)
- `GET /api/applications/{id}` - Get a specific application
- `PUT /api/applications/{id}` - Update an application
- `DELETE /api/applications/{id}` - Delete an application
- `GET /api/applications/status-hierarchy` - Get status hierarchy information

## Business Logic

### Status Hierarchy
Applications have a status hierarchy where higher numbers indicate higher priority:

1. **Building Application** (Weight: 1)
2. **Application Submitted to University** (Weight: 2)
3. **Offer Received** (Weight: 3)
4. **Offer Accepted by Student** (Weight: 4)
5. **Visa Approved** (Weight: 5) - Highest priority
6. **Dropped** (Weight: 0) - Lowest priority

### Highest Status Calculation
- When an application is created or updated, the student's `highest_status` and `highest_intake` are automatically recalculated
- The `highest_status` is determined by the application with the highest status weight
- The `highest_intake` is taken from the application that has the highest status
- If multiple applications have the same highest status, the one with the closest (earliest) intake date is chosen

### Example Scenario
A student has 3 applications:
- Application A: "Building Application" (Jan 2026)
- Application B: "Offer Received" (Feb 2026)
- Application C: "Visa Approved" (Mar 2026)

The student's highest status will be "Visa Approved" and highest intake will be "Mar 2026".

## Data Models

### Student
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "highest_intake": "Jan 2026",
  "highest_status": "Offer Received",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "applications_count": 2
}
```

### Application
```json
{
  "id": 1,
  "student_id": 1,
  "university_name": "Harvard University",
  "program_name": "Computer Science",
  "intake": "Jan 2026",
  "status": "Offer Received",
  "status_weight": 3,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

## Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_student_routes.py

# Run application test file
pytest tests/test_application_routes.py

# Run single student business logic test
pytest tests/test_individual_student_business_logic.py --student-id 1

# Run batch wise all student business logic test 

pytest tests/test_batch_student_business_logic.py --order asc --batch-size 10

# Run with verbose output
pytest -v
```

### Test Coverage
The test suite includes:
- Unit tests for all API endpoints
- Business logic tests for status hierarchy calculations
- Error handling tests
- Data validation tests
- Edge case scenarios

## Database Management

### Database Utilities
```bash
# Reset database (drop, create, and create tables)
python database_utils.py reset

# Drop existing database
python database_utils.py drop

# Create new database
python database_utils.py create

# Create tables only
python database_utils.py tables

# Show existing tables
python database_utils.py show
```

### Database Connection
Default connection string: `postgresql://postgres:1234@localhost:5432/student_platform_db`

Update the connection string in `config.py` for your environment.

## API Documentation

Complete API documentation is available in `API_DOCUMENTATION.md` with:
- Detailed endpoint descriptions
- Request/response examples
- Error handling information
- Business logic explanations

## Postman Collection

Import `Student_Platform_API.postman_collection.json` into Postman to test all endpoints with pre-configured requests including:
- Basic CRUD operations
- Complete test scenarios
- Error handling examples
- Business logic demonstrations

## Production Deployment

### Environment Variables
```bash
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key
```

### Docker Production
```bash
# Build and run production containers
docker-compose -f docker-compose.yml up --build

# Run in background
docker-compose -f docker-compose.yml up -d --build
```

### Manual Production Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables
3. Run database migrations: `python database_utils.py reset`
4. Start with Gunicorn: `gunicorn --bind 0.0.0.0:5005 app:app`

## Error Handling

The API includes comprehensive error handling:
- **400 Bad Request**: Invalid input data or validation errors
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side errors

All errors return JSON responses with descriptive messages.

## Performance Considerations

- Database indexes on frequently queried fields
- Pagination for all list endpoints
- Connection pooling for database connections
- Proper error handling and logging
- ACID compliance for data integrity

## Security Features

- Input validation and sanitization
- SQL injection prevention through ORM
- CORS configuration
- Non-root user in Docker containers
- Environment-based configuration

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

For questions or issues, please create an issue in the repository or contact the development team.
