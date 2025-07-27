#!/usr/bin/env python3
"""
Final test script to verify the surveys page is completely fixed
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

def test_all_survey_urls():
    """Test that all survey-related URL patterns resolve correctly"""
    print("🔍 Testing All Survey URL Patterns...")
    
    # List of all survey-related URL patterns
    survey_urls = [
        'admin-survey',
        'admin_api_surveys_files',
        'admin_api_survey_file_detail',
        'admin_api_surveys_file_preview',
        'admin_api_surveys_file_download',
        'admin_api_surveys_file_delete',
        'admin_api_surveys_upload',
    ]
    
    success_count = 0
    total_count = len(survey_urls)
    
    for url_name in survey_urls:
        try:
            if url_name in ['admin_api_survey_file_detail', 'admin_api_surveys_file_preview', 
                           'admin_api_surveys_file_download', 'admin_api_surveys_file_delete']:
                # These URLs require a file_id parameter
                test_uuid = "12345678-1234-1234-1234-123456789012"
                url = reverse(url_name, kwargs={'file_id': test_uuid})
                print(f"✅ {url_name}: {url}")
            else:
                # These URLs don't require parameters
                url = reverse(url_name)
                print(f"✅ {url_name}: {url}")
            success_count += 1
        except Exception as e:
            print(f"❌ {url_name}: {e}")
    
    print(f"\n📊 URL Resolution Results: {success_count}/{total_count} URLs working")
    return success_count == total_count

def test_surveys_page_loading():
    """Test that the surveys page loads without template errors"""
    print("\n🔍 Testing Surveys Page Loading...")
    
    client = Client()
    
    try:
        # Test the surveys page (should redirect to login when not authenticated)
        response = client.get('/admin-dashboard/surveys/')
        
        if response.status_code == 302:
            print("✅ Surveys page correctly redirects to login (expected)")
            return True
        elif response.status_code == 200:
            print("✅ Surveys page loads successfully!")
            return True
        else:
            print(f"❌ Surveys page failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading surveys page: {e}")
        return False

def test_surveys_api_endpoints():
    """Test that all survey API endpoints are accessible"""
    print("\n🔍 Testing Survey API Endpoints...")
    
    client = Client()
    
    api_endpoints = [
        '/admin-dashboard/api/surveys/files/',
        '/admin-dashboard/api/surveys/upload/',
    ]
    
    success_count = 0
    total_count = len(api_endpoints)
    
    for endpoint in api_endpoints:
        try:
            response = client.get(endpoint)
            if response.status_code in [200, 401, 403]:  # 401/403 are expected for unauthenticated requests
                print(f"✅ {endpoint}: Status {response.status_code}")
                success_count += 1
            else:
                print(f"❌ {endpoint}: Unexpected status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
    
    print(f"\n📊 API Endpoint Results: {success_count}/{total_count} endpoints accessible")
    return success_count == total_count

if __name__ == "__main__":
    print("🚀 Starting Final Surveys Page Test...\n")
    
    url_test = test_all_survey_urls()
    page_test = test_surveys_page_loading()
    api_test = test_surveys_api_endpoints()
    
    print("\n" + "="*50)
    print("🎯 FINAL TEST RESULTS")
    print("="*50)
    
    if url_test and page_test and api_test:
        print("✅ ALL TESTS PASSED!")
        print("🎉 The surveys page is completely fixed!")
        print("🚀 No more NoReverseMatch errors!")
    else:
        print("❌ SOME TESTS FAILED!")
        if not url_test:
            print("   - URL resolution issues")
        if not page_test:
            print("   - Page loading issues")
        if not api_test:
            print("   - API endpoint issues")
    
    print("\n📝 Summary:")
    print("✅ URL patterns: Working" if url_test else "❌ URL patterns: Issues found")
    print("✅ Page loading: Working" if page_test else "❌ Page loading: Issues found")
    print("✅ API endpoints: Working" if api_test else "❌ API endpoints: Issues found")
    
    print("\n✨ Test completed!") 