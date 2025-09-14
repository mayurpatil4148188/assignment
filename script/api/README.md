# API Test Script

This script reads the `students.json` file and creates students and applications using the Student Platform API endpoints.

## Features

- **API Integration**: Uses HTTP requests to create students and applications
- **Error Handling**: Comprehensive error handling with detailed logging
- **Logging**: Creates timestamped log files for debugging
- **Dry Run Mode**: Test what would be created without making API calls
- **Statistics**: Shows current API statistics after operations
- **Rate Limiting**: Small delays between API calls to avoid overwhelming the server

## Prerequisites

1. **Install Dependencies**:
   ```bash
   pip install requests
   ```

2. **Start the API Server**:
   ```bash
   # Make sure your Student Platform API is running
   python app.py
   ```

3. **Generate Data** (if needed):
   ```bash
   python faker_data.py --count 10 --output students.json
   ```

## Usage

### Basic Usage
```bash
# Create all students and applications from students.json
python api_test.py

# Use custom API base URL
python api_test.py --base-url http://localhost:5005

# Limit to first 10 students
python api_test.py --limit 10

# Dry run (show what would be created)
python api_test.py --dry-run

# Use custom JSON file
python api_test.py --json-file my_data.json
```

### Examples

1. **Test with 5 students**:
   ```bash
   python api_test.py --limit 5
   ```

2. **Dry run to see what would be created**:
   ```bash
   python api_test.py --dry-run
   ```

3. **Use different API port**:
   ```bash
   python api_test.py --base-url http://localhost:8080
   ```

## API Endpoints Used

Based on the Postman collection, the script uses:

- `GET /api/health/` - Health check
- `POST /api/students/` - Create student
- `POST /api/applications/` - Create application
- `GET /api/students/?page=1&per_page=1` - Get students count
- `GET /api/applications/?page=1&per_page=1` - Get applications count

## Output

### Console Output
```
✅ API connection successful
📁 Loaded data from: /path/to/students.json
   Students: 50
   Applications: 98
👥 Creating 50 students...
   Processing student 1/50: Destiny Morgan
✅ Created student: Destiny Morgan (ID: 1)
...
📝 Creating applications...
✅ Created application: University of Connecticut - Chemistry (ID: 1)
...

📊 API TEST SUMMARY
============================================================
✅ Created Students: 50
✅ Created Applications: 98
❌ Errors: 0

📈 Current API Statistics:
   Total Students in API: 50
   Total Applications in API: 98
============================================================
```

### Log Files
- Creates timestamped log files: `api_test_YYYYMMDD_HHMMSS.log`
- Contains detailed error information and API responses
- Useful for debugging issues

## Error Handling

The script handles various error scenarios:

- **Connection Errors**: API server not running
- **Validation Errors**: Invalid data format
- **HTTP Errors**: 4xx/5xx status codes
- **Timeout Errors**: API calls taking too long
- **JSON Parsing Errors**: Malformed response data

All errors are logged and included in the summary.

## Data Flow

1. **Load JSON**: Reads `students.json` file
2. **Test Connection**: Verifies API is accessible
3. **Create Students**: Creates students via API (removes timestamps)
4. **Map IDs**: Maps original student IDs to new API-generated IDs
5. **Create Applications**: Creates applications with correct student IDs
6. **Generate Summary**: Shows statistics and any errors

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   ```
   ❌ API connection failed: Connection refused
   ```
   - Make sure the API server is running
   - Check the base URL is correct

2. **Validation Errors**:
   ```
   ❌ Failed to create student: 400 - {"error": "Invalid email format"}
   ```
   - Check the JSON data format
   - Verify email and phone number formats

3. **Student ID Not Found**:
   ```
   ⚠️  Student ID 5 not found in created students
   ```
   - Student creation failed, so applications can't be created
   - Check the error logs for the specific student creation failure

### Debug Mode

For detailed debugging, check the log files created in the same directory.

## Integration with Other Scripts

This script works well with:

- `faker_data.py` - Generate test data
- `reset_db.py` - Reset database before testing
- Postman collection - Manual API testing

## Example Workflow

```bash
# 1. Reset database
cd ../db
python reset_db.py --force

# 2. Generate test data
cd ../api
python faker_data.py --count 20 --output test_data.json

# 3. Test API with generated data
python api_test.py --json-file test_data.json --limit 20

# 4. Check results
python api_test.py --dry-run
```
