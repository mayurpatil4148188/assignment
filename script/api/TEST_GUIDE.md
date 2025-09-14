# Student Logic Test Guide

This guide explains how to test the highest status and highest intake logic for the Student Platform API.

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

## 🧪 Test Scripts

### 1. Logic Test Examples (`logic_test_examples.py`)
Tests the logic with predefined examples to validate the implementation.

```bash
# Activate virtual environment
source project_env/bin/activate

# Run logic examples
python logic_test_examples.py
```

**Expected Output:**
```
🎯 STUDENT LOGIC TEST EXAMPLES
============================================================

🧪 Testing: Single Application
==================================================
Applications:
  1. Harvard | Computer Science | Jan 2026 | Offer Received (weight: 3)

Results:
  Expected Highest Status: Offer Received
  Actual Highest Status: Offer Received
  Expected Highest Intake: Jan 2026
  Actual Highest Intake: Jan 2026

Validation:
  Status: ✅ CORRECT
  Intake: ✅ CORRECT
```

### 2. Database Result Test (`result_test.py`)
Tests actual database records to ensure the logic is working correctly.

```bash
# Test all students
python result_test.py

# Test specific student
python result_test.py --student-id 1

# Test first 10 students
python result_test.py --limit 10

# Show detailed output
python result_test.py --verbose

# Show database statistics only
python result_test.py --stats
```

## 📊 Example Scenarios

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

## 🔍 Understanding Test Results

### ✅ Passed Test
```
✅ Student John Doe (ID: 1) - PASSED
```
- Highest status and intake are calculated correctly

### ❌ Failed Test
```
❌ Student Jane Smith (ID: 2) - FAILED
      Highest status mismatch: expected 'Visa Approved', got 'Offer Received'
      Highest intake mismatch: expected 'Jan 2026', got 'Sep 2025'
```
- The database values don't match the expected calculated values
- This indicates the logic needs to be fixed or the data needs to be updated

### 📊 Detailed Output (--verbose)
```
📊 Detailed Results for Student 1 (John Doe):
   Applications: 3
   Expected Highest Status: Visa Approved
   Actual Highest Status: Visa Approved
   Expected Highest Intake: Jan 2026
   Actual Highest Intake: Jan 2026
   Status Match: ✅
   Intake Match: ✅

   📝 Applications (sorted by status weight):
      - Harvard | Computer Science | Jan 2026 | Visa Approved (weight: 5)
      - MIT | Data Science | Sep 2025 | Offer Received (weight: 3)
      - Stanford | AI | Jan 2027 | Building Application (weight: 1)
```

## 🚨 Common Issues

### 1. Status Mismatch
**Problem:** Expected status doesn't match actual status
**Cause:** Logic not updating when applications are created/updated
**Solution:** Check if the business logic is being triggered

### 2. Intake Mismatch
**Problem:** Expected intake doesn't match actual intake
**Cause:** Wrong application selected for highest intake
**Solution:** Verify the tie-breaking logic (closest date)

### 3. No Applications
**Problem:** Student has no applications
**Expected:** Both highest status and intake should be null/empty

### 4. All Dropped Applications
**Problem:** All applications are "Dropped"
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

## 📈 Test Summary

After running tests, you'll see a summary like:

```
📊 STUDENT LOGIC TEST SUMMARY
============================================================
Total Students Tested: 50
✅ Passed: 48
❌ Failed: 2
Success Rate: 96.0%

❌ Errors Found:
   - Student 15 (Jane Smith): Highest status mismatch: expected 'Visa Approved', got 'Offer Received'
   - Student 23 (Bob Johnson): Highest intake mismatch: expected 'Jan 2026', got 'Sep 2025'
============================================================
```

This helps identify which students have incorrect logic and need to be fixed.
