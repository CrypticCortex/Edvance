#!/usr/bin/env python3
"""
Test script to verify the streamlined API documentation
Shows the difference between full API and core teacher workflow API
"""

import requests
import json
from typing import Dict, Any

def test_api_documentation():
    """Test the streamlined API documentation"""
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        print("🔍 TESTING STREAMLINED API DOCUMENTATION")
        print("=" * 50)
        
        # Test if server is running
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print("❌ Server not running or not accessible")
            return
            
        print("✅ Server is running")
        root_info = response.json()
        print(f"📱 API: {root_info.get('message', 'Unknown')}")
        print(f"📊 Core Endpoints: {root_info.get('total_core_endpoints', 'Unknown')}")
        
        # Get OpenAPI schema
        openapi_response = requests.get(f"{base_url}/openapi.json")
        if openapi_response.status_code != 200:
            print("❌ Failed to get OpenAPI schema")
            return
            
        openapi_data = openapi_response.json()
        paths = openapi_data.get("paths", {})
        
        print(f"\n📋 STREAMLINED API ANALYSIS")
        print("-" * 30)
        print(f"Total endpoints shown: {len(paths)}")
        print(f"API Title: {openapi_data.get('info', {}).get('title', 'Unknown')}")
        
        # Categorize endpoints by tag
        endpoint_categories = {}
        for path, methods in paths.items():
            for method, details in methods.items():
                if method == "parameters":
                    continue
                    
                tags = details.get("tags", ["Untagged"])
                tag = tags[0] if tags else "Untagged"
                
                if tag not in endpoint_categories:
                    endpoint_categories[tag] = []
                    
                endpoint_categories[tag].append(f"{method.upper()} {path}")
        
        print(f"\n📊 ENDPOINTS BY CATEGORY")
        print("-" * 30)
        for category, endpoints in endpoint_categories.items():
            print(f"\n{category} ({len(endpoints)} endpoints):")
            for endpoint in sorted(endpoints):
                print(f"  • {endpoint}")
        
        # Verify core workflow endpoints are present
        core_workflow_endpoints = [
            "POST /v1/auth/signup",
            "GET /v1/auth/me",
            "POST /v1/learning/start-monitoring", 
            "POST /v1/learning/analyze-assessment",
            "POST /v1/learning/generate-learning-path",
            "POST /v1/lessons/lessons/create-from-step",
            "POST /v1/lessons/lessons/{lesson_id}/chat/start",
            "GET /v1/learning/teacher/learning-analytics"
        ]
        
        print(f"\n✅ CORE WORKFLOW VERIFICATION")
        print("-" * 30)
        all_endpoints = []
        for endpoints in endpoint_categories.values():
            all_endpoints.extend(endpoints)
            
        missing_endpoints = []
        present_endpoints = []
        
        for core_endpoint in core_workflow_endpoints:
            # Check for exact match or pattern match
            found = False
            for endpoint in all_endpoints:
                if core_endpoint == endpoint or _endpoints_match(core_endpoint, endpoint):
                    found = True
                    present_endpoints.append(core_endpoint)
                    break
            
            if not found:
                missing_endpoints.append(core_endpoint)
        
        print(f"Present core endpoints: {len(present_endpoints)}/{len(core_workflow_endpoints)}")
        
        for endpoint in present_endpoints:
            print(f"  ✅ {endpoint}")
            
        if missing_endpoints:
            print(f"\nMissing core endpoints:")
            for endpoint in missing_endpoints:
                print(f"  ❌ {endpoint}")
        
        # Check for unwanted endpoints (should be filtered out)
        unwanted_patterns = ["/debug/", "/apps/", "/builder/", "/v1/agent/", "/v1/assessments/rag/"]
        unwanted_found = []
        
        for endpoint in all_endpoints:
            for pattern in unwanted_patterns:
                if pattern in endpoint:
                    unwanted_found.append(endpoint)
                    break
        
        print(f"\n🔍 FILTERING VERIFICATION")
        print("-" * 30)
        if unwanted_found:
            print(f"⚠️  Found {len(unwanted_found)} endpoints that should be filtered:")
            for endpoint in unwanted_found[:5]:  # Show first 5
                print(f"  • {endpoint}")
            if len(unwanted_found) > 5:
                print(f"  ... and {len(unwanted_found) - 5} more")
        else:
            print("✅ All unwanted endpoints successfully filtered")
        
        # Performance summary
        target_core_count = 22
        actual_count = len(paths)
        
        print(f"\n🎯 STREAMLINING SUMMARY")
        print("-" * 30)
        print(f"Target core endpoints: {target_core_count}")
        print(f"Actual endpoints shown: {actual_count}")
        print(f"Filtering success: {'✅' if actual_count <= target_core_count + 5 else '⚠️'}")
        print(f"Core workflow complete: {'✅' if len(missing_endpoints) == 0 else '❌'}")
        
        if actual_count <= target_core_count + 5 and len(missing_endpoints) == 0:
            print(f"\n🎉 SUCCESS: Streamlined API documentation is working correctly!")
            print(f"📚 Visit http://127.0.0.1:8000/docs to see the clean teacher workflow API")
        else:
            print(f"\n⚠️  Issues found with streamlined documentation")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error testing API documentation: {e}")

def _endpoints_match(pattern: str, actual: str) -> bool:
    """Check if an endpoint matches a pattern (simple path parameter handling)"""
    if pattern == actual:
        return True
        
    # Handle path parameters like {lesson_id}
    pattern_parts = pattern.split()
    actual_parts = actual.split()
    
    if len(pattern_parts) != len(actual_parts):
        return False
        
    if pattern_parts[0] != actual_parts[0]:  # HTTP method must match exactly
        return False
        
    # Check path with parameter substitution
    pattern_path = pattern_parts[1].split('/')
    actual_path = actual_parts[1].split('/')
    
    if len(pattern_path) != len(actual_path):
        return False
        
    for p_part, a_part in zip(pattern_path, actual_path):
        if p_part.startswith('{') and p_part.endswith('}'):
            continue  # Parameter placeholder matches anything
        elif p_part != a_part:
            return False
            
    return True

if __name__ == "__main__":
    test_api_documentation()
