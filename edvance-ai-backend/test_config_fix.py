#!/usr/bin/env python3
"""
Quick test for Phase 2 configuration fixes
"""

def test_vertex_config():
    """Test vertex configuration."""
    print("🧪 Testing Vertex Configuration...")
    
    try:
        from app.core.config import settings
        print(f"✅ Settings loaded: project={settings.google_cloud_project}")
        print(f"✅ Location: {settings.google_cloud_location}")
        
        # Test that the vertex import works
        from app.core.vertex import get_vertex_model
        print("✅ Vertex model function imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Vertex config test failed: {e}")
        return False

def test_basic_models():
    """Test basic model imports."""
    print("\n📊 Testing Assessment Models...")
    
    try:
        from app.models.student import AssessmentConfig, Assessment, AssessmentQuestion
        print("✅ Assessment models imported")
        
        # Test basic model creation
        config = AssessmentConfig(
            config_id="test-123",
            teacher_uid="teacher-456",
            name="Test Assessment",
            subject="Mathematics", 
            target_grade=5,
            difficulty_level="medium",
            topic="Basic Arithmetic"
        )
        print(f"✅ Assessment config created: {config.name}")
        
        return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Phase 2 Configuration - Quick Fix Test")
    print("=" * 45)
    
    vertex_ok = test_vertex_config()
    models_ok = test_basic_models()
    
    print("\n📋 Fix Results:")
    print(f"• Vertex Config: {'✅ FIXED' if vertex_ok else '❌ STILL BROKEN'}")
    print(f"• Assessment Models: {'✅ WORKING' if models_ok else '❌ BROKEN'}")
    
    if vertex_ok and models_ok:
        print("\n🎉 Configuration fixes successful!")
        print("🚀 Ready to continue with Phase 2 development")
    else:
        print("\n❌ Some issues remain - check the errors above")
