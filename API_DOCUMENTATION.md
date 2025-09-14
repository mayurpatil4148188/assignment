# Student Platform API Documentation

## Overview
The Student Platform API provides endpoints for managing students and their university applications. The API follows RESTful conventions and returns JSON responses.

## Base URL
- Development: `http://localhost:5000`
- Production: `http://your-domain.com`

## Authentication
Currently, the API does not require authentication. In production, implement proper authentication mechanisms.

## Response Format
All responses are in JSON format. Error responses include an `error` or `errors` field with details.

## Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

---

## Health Check

### GET /api/health/
Check if the API is running and database is connected.

**Response:**
```json
{
  "status": "healthy",
  "message": "Student Platform API is running",
  "database": "connected"
}
```

---

## Students

### Create Student
**POST** `/api/students/`

Create a new student.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890"
}
```

**Response (201):**
```json
{
  "message": "Student created successfully",
  "student": {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "highest_intake": null,
    "highest_status": null,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "applications_count": 0
  }
}
```

### Get All Students
**GET** `/api/students/`

Get all students with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10, max: 100)

**Response (200):**
```json
{
  "students": [
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
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 10,
    "total": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### Get Student
**GET** `/api/students/{id}`

Get a specific student by ID.

**Response (200):**
```json
{
  "student": {
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
}
```

### Update Student
**PUT** `/api/students/{id}`

Update a specific student.

**Request Body:**
```json
{
  "name": "John Smith",
  "email": "john.smith@example.com"
}
```

**Response (200):**
```json
{
  "message": "Student updated successfully",
  "student": {
    "id": 1,
    "name": "John Smith",
    "email": "john.smith@example.com",
    "phone": "+1234567890",
    "highest_intake": "Jan 2026",
    "highest_status": "Offer Received",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T11:00:00",
    "applications_count": 2
  }
}
```

### Delete Student
**DELETE** `/api/students/{id}`

Delete a specific student and all associated applications.

**Response (200):**
```json
{
  "message": "Student deleted successfully"
}
```

### Get Student Applications
**GET** `/api/students/{id}/applications`

Get all applications for a specific student.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10, max: 100)

**Response (200):**
```json
{
  "applications": [
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
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 10,
    "total": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### Get Student Highest Status
**GET** `/api/students/{id}/highest-status`

Get the highest status and intake for a specific student.

**Response (200):**
```json
{
  "highest_status": "Offer Received",
  "highest_intake": "Jan 2026"
}
```

---

## Applications

### Create Application
**POST** `/api/applications/`

Create a new application for a student.

**Request Body:**
```json
{
  "student_id": 1,
  "university_name": "Harvard University",
  "program_name": "Computer Science",
  "intake": "Jan 2026",
  "status": "Building Application"
}
```

**Response (201):**
```json
{
  "message": "Application created successfully",
  "application": {
    "id": 1,
    "student_id": 1,
    "university_name": "Harvard University",
    "program_name": "Computer Science",
    "intake": "Jan 2026",
    "status": "Building Application",
    "status_weight": 1,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

### Get All Applications
**GET** `/api/applications/`

Get all applications with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10, max: 100)

**Response (200):**
```json
{
  "applications": [
    {
      "id": 1,
      "student_id": 1,
      "university_name": "Harvard University",
      "program_name": "Computer Science",
      "intake": "Jan 2026",
      "status": "Building Application",
      "status_weight": 1,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 10,
    "total": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### Get Application
**GET** `/api/applications/{id}`

Get a specific application by ID.

**Response (200):**
```json
{
  "application": {
    "id": 1,
    "student_id": 1,
    "university_name": "Harvard University",
    "program_name": "Computer Science",
    "intake": "Jan 2026",
    "status": "Building Application",
    "status_weight": 1,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

### Update Application
**PUT** `/api/applications/{id}`

Update a specific application.

**Request Body:**
```json
{
  "status": "Offer Received",
  "university_name": "Updated University Name"
}
```

**Response (200):**
```json
{
  "message": "Application updated successfully",
  "application": {
    "id": 1,
    "student_id": 1,
    "university_name": "Updated University Name",
    "program_name": "Computer Science",
    "intake": "Jan 2026",
    "status": "Offer Received",
    "status_weight": 3,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T11:00:00"
  }
}
```

### Delete Application
**DELETE** `/api/applications/{id}`

Delete a specific application.

**Response (200):**
```json
{
  "message": "Application deleted successfully"
}
```

### Get Status Hierarchy
**GET** `/api/applications/status-hierarchy`

Get the status hierarchy and valid statuses.

**Response (200):**
```json
{
  "status_hierarchy": {
    "Building Application": 1,
    "Application Submitted to University": 2,
    "Offer Received": 3,
    "Offer Accepted by Student": 4,
    "Visa Approved": 5,
    "Dropped": 0
  },
  "valid_statuses": [
    "Building Application",
    "Application Submitted to University",
    "Offer Received",
    "Offer Accepted by Student",
    "Visa Approved",
    "Dropped"
  ]
}
```

---

## Error Responses

### Validation Error (400)
```json
{
  "errors": [
    "Name is required",
    "Invalid email format"
  ]
}
```

### Not Found Error (404)
```json
{
  "error": "Student not found"
}
```

### Internal Server Error (500)
```json
{
  "error": "Internal server error"
}
```

---

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

### Intake Format
Intake values should follow the format: `MMM YYYY` (e.g., "Jan 2026", "Feb 2026", "Sep 2026")

### Data Validation
- **Name**: Required, minimum 2 characters
- **Email**: Required, valid email format, unique
- **Phone**: Required, 10-15 digits (non-digit characters are ignored)
- **University Name**: Required, minimum 2 characters
- **Program Name**: Required, minimum 2 characters
- **Intake**: Required, valid format (MMM YYYY)
- **Status**: Required, must be one of the valid statuses
