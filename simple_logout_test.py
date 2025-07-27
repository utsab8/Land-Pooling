#!/usr/bin/env python3
"""
Simple test to verify logout URL works
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from django.test import Client

def test_logout_url():
    """Test logout URL directly"""
    print("🚪 Testing Logout URL...")
    print("=" * 40)
    
    client = Client()
    
    # Test GET request to logout
    print("\n🔄 Testing GET logout...")
    response = client.get('/logout/')
    print(f"   Status code: {response.status_code}")
    print(f"   Redirect URL: {response.url if hasattr(response, 'url') else 'No redirect'}")
    
    if response.status_code == 302 and response.url == '/api/account/login-page/':
        print("✅ GET logout works correctly!")
    else:
        print("❌ GET logout failed")
        return False
    
    # Test POST request to logout
    print("\n🔄 Testing POST logout...")
    response = client.post('/logout/')
    print(f"   Status code: {response.status_code}")
    print(f"   Redirect URL: {response.url if hasattr(response, 'url') else 'No redirect'}")
    
    if response.status_code == 302 and response.url == '/api/account/login-page/':
        print("✅ POST logout works correctly!")
    else:
        print("❌ POST logout failed")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 Logout URL test passed!")
    return True

if __name__ == '__main__':
    success = test_logout_url()
    exit(0 if success else 1) 