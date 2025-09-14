# Student Platform API

A Flask-based REST API for managing students and their university applications with automatic calculation of highest status and intake based on application hierarchy.

## 🚀 Features

- **Student Management**: Full CRUD operations for student records
- **Application Management**: Full CRUD operations for university applications
- **Business Logic**: Automatic calculation of highest status and intake based on application hierarchy
- **Status Hierarchy**: 6-tier status system with proper weightage
- **Data Validation**: Comprehensive input validation and error handling
- **Pagination**: Built-in pagination for all list endpoints
- **Production Ready**: Docker support, health checks, and proper error handling
- **Testing**: Comprehensive test suite with pytest (individual and batch testing)
- **Data Generation**: Faker-based dummy data generation for testing
- **API Testing**: Automated API testing with retry logic and error handling
- **Database Management**: Environment-based database utilities
- **Documentation**: Complete API documentation and deployment guides

## 🛠️ Technology Stack

- **Backend**: Flask (Python 3.12)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Testing**: pytest with comprehensive test coverage
- **Data Generation**: Faker library
- **Containerization**: Docker & Docker Compose
- **Web Server**: Gunicorn + Nginx
- **Environment Management**: python-dotenv
- **API Testing**: requests library with retry logic

## 📁 Project Structure

```
student-platform/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── database_utils.py               # Database management utilities (env-based)
├── requirements.txt                # Python dependencies
├── pytest.ini                     # Pytest configuration
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose setup
├── nginx.conf                      # Nginx configuration
├── start.sh                        # Local development startup script
├── start-docker.sh                 # Docker startup script
├── models/                         # Database models
│   ├── __init__.py
│   ├── student.py                  # Student model with validation
│   └── application.py              # Application model with status hierarchy
├── services/                       # Business logic layer
│   ├── __init__.py
│   ├── student_service.py          # Student business logic
│   └── application_service.py      # Application business logic
├── routes/                         # API routes
│   ├── __init__.py
│   ├── student_routes.py           # Student endpoints
│   ├── application_routes.py       # Application endpoints
│   └── health_routes.py            # Health check endpoint
├── utils/                          # Utility functions
│   ├── __init__.py
│   └── response_utils.py           # API response utilities
├── tests/                          # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py                 # Test configuration
│   ├── test_student_routes.py      # Student route tests
│   ├── test_application_routes.py  # Application route tests
│   ├── test_individual_student_business_logic.py  # Individual student logic tests
│   ├── test_batch_student_business_logic.py       # Batch student logic tests
│   └── README.md                   # Test documentation
├── script/                         # Utility scripts
│   ├── api/                        # API testing and data generation
│   │   ├── api_test.py             # Automated API testing
│   │   ├── faker_data.py           # Dummy data generation
│   │   ├── logic_test_examples.py  # Logic validation examples
│   │   ├── result_test.py          # Database result testing
│   │   ├── debug_api.py            # API debugging utility
│   │   ├── students.json           # Generated test data
│   │   ├── TEST_GUIDE.md           # Testing guide
│   │   └── README.md               # Script documentation
│   └── db/                         # Database utilities
│       ├── reset_db.py             # Database reset script
│       └── test_connection.py      # Database connection testing
├── docs/                           # Documentation
│   ├── API_DOCUMENTATION.md        # Complete API documentation
│   ├── PROJECT_SUMMARY.md          # Project overview
│   └── PRODUCTION.md               # Production deployment guide
├── Student_Platform_API.postman_collection.json  # Postman collection
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 12+
- Docker & Docker Compose (optional)
- Git (for cloning)

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd student-platform
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv project_env
   source project_env/bin/activate  # On Windows: project_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Create .env file with your database configuration
   cp .env.example .env  # if available
   # OR create .env file manually with:
   # DATABASE_URL=postgresql://postgres:1234@localhost:5432/student_platform_db
   ```

5. **Set up the database**
   ```bash
   # Make sure PostgreSQL is running
   python database_utils.py reset
   ```

6. **Run the application**
   ```bash
   python app.py
   # OR use the startup script
   ./start.sh
   ```

7. **Access the API**
   - API Base URL: `http://localhost:5005`
   - Health Check: `http://localhost:5005/api/health/`

### Option 2: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd folder name
   ```

2. **Configure environment variables**
   ```bash
   # Create .env file for Docker
   echo "DATABASE_URL=postgresql://postgres:1234@db:5432/student_platform_db" > .env
   ```

3. **Run with Docker Compose**
   ```bash
   sudo docker compose build
   # OR use the Docker startup script
   ./start-docker.sh
   ```

4. **Access the API**
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

## 🧪 Testing

### Comprehensive Test Suite
The project includes a robust testing framework with multiple test types:

#### **1. API Route Tests**
```bash
# Test student routes
pytest tests/test_student_routes.py -v

# Test application routes
pytest tests/test_application_routes.py -v

# Run all route tests
pytest tests/test_*_routes.py -v
```

#### **2. Business Logic Tests**
```bash
# Test individual student business logic
pytest tests/test_individual_student_business_logic.py -v

# Test batch student business logic (students 1-10)
pytest tests/test_batch_student_business_logic.py::test_batch_students_asc_order -v

# Test all students in database
pytest tests/test_batch_student_business_logic.py::test_all_students -v -s
```

#### **3. Data Generation and API Testing**
```bash
# Generate dummy data
python script/api/faker_data.py --count 50

# Test API with generated data
python script/api/api_test.py

# Test database logic validation
python script/api/result_test.py --verbose
```

#### **4. Database Testing**
```bash
# Test database connection
python script/db/test_connection.py

# Reset database for testing
python script/db/reset_db.py --force
```

### Test Coverage
The comprehensive test suite includes:
- **Unit tests** for all API endpoints
- **Business logic tests** for status hierarchy calculations
- **Individual student validation** with detailed output
- **Batch processing tests** for multiple students
- **Data generation tests** with realistic scenarios
- **API integration tests** with retry logic
- **Database validation tests** for logic correctness
- **Error handling tests** for edge cases
- **Performance tests** for large datasets

### Test Documentation
- **Test Guide**: `tests/README.md` - Comprehensive testing documentation
- **Script Guide**: `script/api/README.md` - Data generation and API testing guide
- **Logic Examples**: `script/api/logic_test_examples.py` - Business logic validation examples

## 🗄️ Database Management

### Environment-Based Database Utilities
The database utilities now support environment variables for flexible configuration:

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

### Database Connection Configuration
The system supports multiple connection methods:

#### **Option 1: DATABASE_URL (Recommended)**
```bash
export DATABASE_URL="postgresql://postgres:1234@localhost:5432/student_platform_db"
```

#### **Option 2: Individual Environment Variables**
```bash
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="student_platform_db"
export DB_USER="postgres"
export DB_PASSWORD="1234"
```

#### **Option 3: .env File**
Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql://postgres:1234@localhost:5432/student_platform_db
# OR
DB_HOST=localhost
DB_PORT=5432
DB_NAME=student_platform_db
DB_USER=postgres
DB_PASSWORD=1234
```

### Database Reset Script
For testing and development, use the dedicated reset script:
```bash
# Reset with confirmation prompt
python script/db/reset_db.py

# Force reset without confirmation
python script/db/reset_db.py --force

# Show help
python script/db/reset_db.py --help
```

## 📚 Documentation

### **Complete Documentation Suite**
The project includes comprehensive documentation in the `docs/` folder:

#### **1. API Documentation**
- **File**: `docs/API_DOCUMENTATION.md`
- **Content**: Complete API reference with detailed endpoint descriptions, request/response examples, error handling, and business logic explanations

#### **2. Project Summary**
- **File**: `docs/PROJECT_SUMMARY.md`
- **Content**: High-level project overview, architecture, and key features

#### **3. Production Deployment Guide**
- **File**: `docs/PRODUCTION.md`
- **Content**: Step-by-step production deployment guide for Ubuntu servers with Docker

### **Testing Documentation**
- **Test Guide**: `tests/README.md` - Comprehensive testing documentation and examples
- **Script Guide**: `script/api/README.md` - Data generation and API testing guide
- **Logic Examples**: `script/api/logic_test_examples.py` - Business logic validation examples

### **Postman Collection**
Import `Student_Platform_API.postman_collection.json` into Postman to test all endpoints with pre-configured requests including:
- Basic CRUD operations
- Complete test scenarios
- Error handling examples
- Business logic demonstrations

## 🚀 Production Deployment

### **Complete Production Guide**
For detailed production deployment instructions, see: **`docs/PRODUCTION.md`**

### **Quick Production Setup**

#### **Environment Variables**
```bash
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key
```

#### **Docker Production**
```bash
# Build and run production containers
sudo docker compose up --build -d

# Check status
sudo docker compose ps

# View logs
sudo docker compose logs -f
```

#### **Manual Production Setup**
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables
3. Run database migrations: `python database_utils.py reset`
4. Start with Gunicorn: `gunicorn --bind 0.0.0.0:5005 app:app`

### **Production Features**
- **Environment-based configuration** with `.env` support
- **Docker containerization** with multi-stage builds
- **Nginx reverse proxy** for load balancing
- **SSL/HTTPS support** with Let's Encrypt
- **Database backup scripts** for data safety
- **Health monitoring** and logging
- **Firewall configuration** for security

## 🔧 Additional Features

### **Error Handling**
The API includes comprehensive error handling:
- **400 Bad Request**: Invalid input data or validation errors
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side errors

All errors return JSON responses with descriptive messages.

### **Performance Considerations**
- Database indexes on frequently queried fields
- Pagination for all list endpoints
- Connection pooling for database connections
- Proper error handling and logging
- ACID compliance for data integrity

### **Security Features**
- Input validation and sanitization
- SQL injection prevention through ORM
- CORS configuration
- Non-root user in Docker containers
- Environment-based configuration

### **Data Generation & Testing**
- **Faker-based dummy data generation** for realistic test scenarios
- **Automated API testing** with retry logic and error handling
- **Business logic validation** with comprehensive test coverage
- **Database result testing** to ensure logic correctness
- **Performance testing** for large datasets

### **Utility Scripts**
- **Database management** with environment variable support
- **API testing automation** with detailed logging
- **Data generation** for development and testing
- **Logic validation** with example scenarios
- **Connection testing** for database troubleshooting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation if needed
7. Submit a pull request

### **Development Guidelines**
- Follow the existing code structure and patterns
- Add comprehensive tests for new features
- Update documentation for any API changes
- Use the provided testing scripts for validation
- Follow the environment variable configuration pattern

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For questions or issues:
1. Check the comprehensive documentation in the `docs/` folder
2. Review the testing guides in `tests/README.md`
3. Use the utility scripts for debugging
4. Create an issue in the repository
5. Contact the development team

### **Quick Help**
- **API Documentation**: `docs/API_DOCUMENTATION.md`
- **Production Deployment**: `docs/PRODUCTION.md`
- **Testing Guide**: `tests/README.md`
- **Script Documentation**: `script/api/README.md`
- **Business Logic Examples**: `script/api/logic_test_examples.py`
