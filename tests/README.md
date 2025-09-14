# Student Logic Tests

This directory contains comprehensive pytest tests for validating the highest status and highest intake logic in the Student Platform API.

## 🎯 What We're Testing

The system should automatically calculate and update:
- **Highest Status**: The application status with the highest weightage
- **Highest Intake**: The intake from the application with the highest status

### Status Hierarchy (Weightage)
1. **Visa Approved** (5) - Highest
2. **Offer Accepted by Student** (4)
3. **Offer Received** (3)
4. **Application Submitted to University** (2)
5. **Building Application** (1)
6. **Dropped** (0) - Lowest

### Logic Rules
1. **Highest Status**: Application with maximum weightage
2. **Highest Intake**: Intake from the application with highest status
3. **Tie Breaking**: If multiple applications have same highest status, use the closest (earliest) intake date

## 🧪 Test Files

### 1. `test_individual_student_logic.py`
Tests individual students to validate their highest status and intake logic.

**Key Test Functions:**
- `test_student_1()` - Test student ID 1
- `test_student_2()` - Test student ID 2
- `test_student_3()` - Test student ID 3
- `test_student_4()` - Test student ID 4
- `test_student_5()` - Test student ID 5
- `test_student_detailed_output()` - Test with detailed output for debugging
- `test_student_no_applications()` - Test students with no applications
- `test_student_all_dropped()` - Test students with all dropped applications

### 2. `test_student_range_logic.py`
Tests ranges of students to validate the logic across multiple students.

**Key Test Functions:**
- `test_students_1_to_10()` - Test students 1-10
- `test_students_1_to_20()` - Test students 1-20
- `test_students_11_to_30()` - Test students 11-30
- `test_students_1_to_50()` - Test students 1-50
- `test_all_students()` - Test all students in database
- `test_students_with_applications()` - Test only students with applications
- `test_students_without_applications()` - Test students without applications
- `test_large_range_performance()` - Performance test for large ranges

### 3. `test_runner.py`
Convenient test runner script for different test scenarios.

## 🚀 Usage Examples

### Activate Virtual Environment
```bash
source project_env/bin/activate
```

### Run Individual Student Tests
```bash
# Test specific student
pytest tests/test_individual_student_logic.py::test_student_1 -v

# Test all individual student tests
pytest tests/test_individual_student_logic.py -v

# Test with detailed output
pytest tests/test_individual_student_logic.py::test_student_detailed_output -v -s
```

### Run Range Tests
```bash
# Test students 1-20
pytest tests/test_student_range_logic.py::test_students_1_to_20 -v

# Test all range tests
pytest tests/test_student_range_logic.py -v

# Test all students in database
pytest tests/test_student_range_logic.py::test_all_students -v -s
```

### Run All Tests
```bash
# Run all tests
pytest tests/ -v

# Run with verbose output
pytest tests/ -vv

# Run excluding slow tests
pytest tests/ -v -m "not slow"
```

### Using the Test Runner
```bash
# Test specific student
python tests/test_runner.py --individual --student-id 1

# Test student range
python tests/test_runner.py --range --start 1 --end 20

# Run all tests
python tests/test_runner.py --all --verbose

# Run logic examples
python tests/test_runner.py --examples
```

## 📊 Expected Test Output

### Individual Student Test
```
🎯 Testing Student 1: John Doe
   Applications: 3
   Current Highest Status: Visa Approved
   Current Highest Intake: Jan 2026
   Expected Highest Status: Visa Approved
   Expected Highest Intake: Jan 2026

   📝 Applications:
      1. Harvard | Computer Science | Jan 2026 | Visa Approved (weight: 5)
      2. MIT | Data Science | Sep 2025 | Offer Received (weight: 3)
      3. Stanford | AI | Jan 2027 | Building Application (weight: 1)

✅ Student 1 (John Doe) - PASSED
```

### Range Test
```
📊 Range Test Results (Students 1-20):
   Total Tested: 20
   ✅ Passed: 18
   ❌ Failed: 2
   Success Rate: 90.0%

❌ Failed Students:
   Student 5 (Jane Smith):
      Status: expected 'Visa Approved', got 'Offer Received'
      Intake: expected 'Jan 2026', got 'Sep 2025'
      Applications: [('Harvard', 'Jan 2026', 'Visa Approved', 5), ('MIT', 'Sep 2025', 'Offer Received', 3)]
```

## 🔍 Test Scenarios

### Scenario 1: Single Application
**Applications:**
- Harvard | Computer Science | Jan 2026 | Offer Received

**Expected Results:**
- Highest Status: Offer Received
- Highest Intake: Jan 2026

### Scenario 2: Multiple Statuses
**Applications:**
- MIT | Data Science | Sep 2025 | Building Application
- Stanford | AI | Jan 2026 | Offer Received  
- Berkeley | ML | Sep 2026 | Offer Accepted by Student

**Expected Results:**
- Highest Status: Offer Accepted by Student (weight: 4)
- Highest Intake: Sep 2026 (from the "Offer Accepted" application)

### Scenario 3: Same Highest Status
**Applications:**
- Harvard | CS | Jan 2026 | Offer Received
- MIT | AI | Sep 2026 | Offer Received
- Stanford | ML | Jan 2027 | Building Application

**Expected Results:**
- Highest Status: Offer Received (weight: 3)
- Highest Intake: Jan 2026 (closest date among "Offer Received" applications)

### Scenario 4: Complex Scenario
**Applications:**
- Harvard | CS | Jan 2026 | Visa Approved
- MIT | AI | Sep 2025 | Offer Accepted by Student
- Stanford | ML | Jan 2027 | Offer Received
- Berkeley | DS | Sep 2026 | Building Application

**Expected Results:**
- Highest Status: Visa Approved (weight: 5)
- Highest Intake: Jan 2026 (from the "Visa Approved" application)

## 🚨 Common Test Failures

### 1. Status Mismatch
**Error:** `Status: expected 'Visa Approved', got 'Offer Received'`
**Cause:** Logic not updating when applications are created/updated
**Solution:** Check if the business logic is being triggered

### 2. Intake Mismatch
**Error:** `Intake: expected 'Jan 2026', got 'Sep 2025'`
**Cause:** Wrong application selected for highest intake
**Solution:** Verify the tie-breaking logic (closest date)

### 3. No Applications
**Expected:** Both highest status and intake should be None
**Note:** Database might have non-None values, which is acceptable

### 4. All Dropped Applications
**Expected:** Highest status should be "Dropped", highest intake should be from the closest dropped application

## 🛠️ Troubleshooting

### Check Database Data
```sql
-- Check student with applications
SELECT s.id, s.name, s.highest_status, s.highest_intake,
       a.university_name, a.program_name, a.intake, a.status
FROM students s
LEFT JOIN applications a ON s.id = a.student_id
WHERE s.id = 1
ORDER BY a.status;
```

### Verify Status Weights
The status hierarchy should match:
- Visa Approved: 5
- Offer Accepted by Student: 4
- Offer Received: 3
- Application Submitted to University: 2
- Building Application: 1
- Dropped: 0

### Check Date Parsing
Intake dates should be in format: "Jan 2026", "Sep 2025", etc.
The system should parse these correctly for comparison.

## 📈 Test Configuration

### Pytest Configuration (`pytest.ini`)
- **Test Paths:** `tests/`
- **Test Files:** `test_*.py`
- **Verbose Output:** Enabled by default
- **Markers:** `slow`, `individual`, `range`, `logic`
- **Warnings:** Disabled for cleaner output

### Test Markers
- `@pytest.mark.slow` - Marks slow tests
- `@pytest.mark.individual` - Marks individual student tests
- `@pytest.mark.range` - Marks range tests
- `@pytest.mark.logic` - Marks logic validation tests

## 🎯 Test Strategy

1. **Unit Tests:** Test individual student logic
2. **Integration Tests:** Test ranges of students
3. **Edge Cases:** Test students with no applications, all dropped, etc.
4. **Performance Tests:** Test large ranges for performance
5. **Regression Tests:** Ensure logic doesn't break over time

## 📊 Success Criteria

- **Individual Tests:** Each student should pass their logic validation
- **Range Tests:** All students in the range should pass
- **Edge Cases:** Special scenarios should be handled correctly
- **Performance:** Tests should complete within reasonable time
- **Coverage:** All logic paths should be tested

The test suite provides comprehensive validation of the highest status and highest intake logic, ensuring the system works correctly across all scenarios! 🎉
