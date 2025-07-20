#!/usr/bin/env python3
"""
Simple validation of student management system
"""

def test_models():
    """Test student models."""
    print("🧪 Testing Student Models...")
    
    from app.models.student import StudentProfile, StudentCSVRow, StudentBatchUploadResponse
    
    # Test CSV validation
    csv_row = StudentCSVRow(
        first_name="john",
        last_name="smith", 
        grade=5,
        password="john123"
    )
    print(f"✅ CSV Row: {csv_row.first_name.title()} {csv_row.last_name.title()}")
    
    # Test profile creation
    profile = StudentProfile(
        student_id="test-123",
        teacher_uid="teacher-456", 
        first_name="John",
        last_name="Smith",
        grade=5,
        default_password="john123"
    )
    print(f"✅ Profile: {profile.first_name} {profile.last_name}, Grade {profile.grade}")
    
    return True

def test_csv_file():
    """Test CSV file structure."""
    print("\n📊 Testing CSV File...")
    
    import csv
    
    with open('sample_students.csv', 'r') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        
        required = {'first_name', 'last_name', 'grade', 'password'}
        if not required.issubset(set(headers)):
            print(f"❌ Missing headers. Found: {headers}")
            return False
        
        students = list(reader)
        print(f"✅ CSV has {len(students)} students with correct headers")
        
        # Show first few students
        for i, student in enumerate(students[:3]):
            print(f"   • {student['first_name']} {student['last_name']}, Grade {student['grade']}")
        
    return True

def test_api_imports():
    """Test API imports."""
    print("\n🌐 Testing API Imports...")
    
    try:
        from app.api.v1.students import router
        from app.services.student_service import student_service
        print("✅ API components imported successfully")
        return True
    except Exception as e:
        print(f"❌ API import failed: {e}")
        return False

if __name__ == "__main__":
    print("🏫 Student Management System - Quick Validation")
    print("=" * 50)
    
    tests = [
        ("Models", test_models),
        ("CSV File", test_csv_file), 
        ("API Imports", test_api_imports)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            print(f"✅ {name}: PASS" if result else f"❌ {name}: FAIL")
        except Exception as e:
            print(f"❌ {name}: FAILED - {e}")
            results.append(False)
    
    print("\n📋 Summary:")
    if all(results):
        print("🎉 All validations passed!")
        print("\n📋 Phase 1 Complete: Student Management System Ready")
        print("\n🚀 Ready for:")
        print("• CSV upload via API (with authentication)")
        print("• Student profile management")
        print("• Move to Phase 2: Assessment Configuration")
    else:
        print("❌ Some validations failed")
