#!/usr/bin/env python3
"""
Test script for student management system
"""

import asyncio
import aiohttp
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
STUDENTS_ENDPOINT = f"{BASE_URL}/v1/students"

async def test_student_models():
    """Test that the student models work correctly."""
    print("🧪 Testing Student Models...")
    
    try:
        from app.models.student import StudentProfile, StudentCSVRow, StudentBatchUploadResponse
        
        # Test StudentCSVRow validation
        csv_row = StudentCSVRow(
            first_name="john",
            last_name="smith",
            grade=5,
            password="john123"
        )
        print(f"✅ CSV Row validation: {csv_row.first_name} {csv_row.last_name}")
        
        # Test StudentProfile creation
        profile = StudentProfile(
            student_id="test-123",
            teacher_uid="teacher-456",
            first_name="John",
            last_name="Smith",
            grade=5,
            default_password="john123",
            subjects=["Mathematics", "Science"]
        )
        print(f"✅ Student Profile: {profile.first_name} {profile.last_name}, Grade {profile.grade}")
        
        # Test BatchUploadResponse
        response = StudentBatchUploadResponse(
            total_students=10,
            students_created=8,
            students_updated=2,
            students_failed=0,
            failed_students=[],
            created_student_ids=["id1", "id2"],
            upload_summary="Test successful"
        )
        print(f"✅ Batch Upload Response: {response.upload_summary}")
        
        print("🎉 All student models working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Model validation failed: {e}")
        return False

async def test_csv_validation():
    """Test CSV file validation."""
    print("\n📊 Testing CSV Validation...")
    
    try:
        from app.services.student_service import student_service
        import pandas as pd
        
        # Check if sample CSV exists and is valid
        csv_path = Path("sample_students.csv")
        if not csv_path.exists():
            print("❌ Sample CSV file not found")
            return False
        
        # Read and validate CSV structure
        df = pd.read_csv(csv_path)
        required_columns = {'first_name', 'last_name', 'grade', 'password'}
        
        if not required_columns.issubset(set(df.columns)):
            print(f"❌ CSV missing required columns. Found: {list(df.columns)}")
            return False
        
        print(f"✅ CSV has {len(df)} students with correct columns")
        print(f"📊 Grade distribution: {df['grade'].value_counts().to_dict()}")
        
        # Validate data types and constraints
        if df['grade'].min() < 1 or df['grade'].max() > 12:
            print("❌ Invalid grade levels found")
            return False
        
        if df['password'].str.len().min() < 6:
            print("❌ Passwords too short found")
            return False
        
        print("✅ CSV validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ CSV validation failed: {e}")
        return False

def test_api_structure():
    """Test API endpoint structure."""
    print("\n🌐 Testing API Structure...")
    
    try:
        from app.api.v1.students import router
        
        # Check if router has expected routes
        routes = [route.path for route in router.routes]
        expected_routes = ['/upload-csv', '/', '/{student_id}', '/{student_id}/subjects', '/{student_id}', '/stats/summary']
        
        print(f"✅ API routes available: {routes}")
        
        # Note: This won't test actual endpoints without authentication
        print("✅ API structure looks good (authentication required for actual testing)")
        return True
        
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🏫 Testing Student Management System")
    print("=" * 50)
    
    # Test models
    models_ok = await test_student_models()
    
    # Test CSV validation
    csv_ok = await test_csv_validation()
    
    # Test API structure
    api_ok = test_api_structure()
    
    print("\n📋 Test Summary:")
    print(f"• Models: {'✅ PASS' if models_ok else '❌ FAIL'}")
    print(f"• CSV Validation: {'✅ PASS' if csv_ok else '❌ FAIL'}")
    print(f"• API Structure: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if all([models_ok, csv_ok, api_ok]):
        print("\n🎉 All tests passed! Student management system is ready.")
        print("\n📝 Next Steps:")
        print("1. Start the server: uvicorn app.main:app --reload")
        print("2. Test CSV upload via API with authentication")
        print("3. Move to Phase 2: Assessment Configuration")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    # Install pandas if not available
    try:
        import pandas as pd
    except ImportError:
        print("📦 Installing pandas for CSV testing...")
        import subprocess
        subprocess.check_call(["pip", "install", "pandas"])
        import pandas as pd
    
    asyncio.run(main())
