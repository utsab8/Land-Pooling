#!/usr/bin/env python3
"""
Test script to verify logout functionality works correctly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_logout_functionality():
    """Test logout functionality"""
    print("🚪 Testing Logout Functionality...")
    print("=" * 40)
    
    client = Client()
    
    # Create a test user
    try:
        user = User.objects.create_user(
            username='testuser_logout',
            email='test_logout@example.com',
            password='testpass123'
        )
        print("✅ Test user created successfully")
    except Exception as e:
        # User might already exist, try to get it
        try:
            user = User.objects.get(username='testuser_logout')
            # Reset password to ensure we can login
            user.set_password('testpass123')
            user.save()
            print("✅ Test user already exists, password reset")
        except:
            print(f"❌ Failed to create/get test user: {e}")
            return False
    
    # Login the user
    login_success = client.login(username='testuser_logout', password='testpass123')
    if not login_success:
        print("❌ Failed to login test user")
        return False
    
    print("✅ User logged in successfully")
    
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
    
    # Verify user is logged out
    print("\n🔄 Verifying user is logged out...")
    response = client.get('/dashboard/')
    if response.status_code == 302:
        print("✅ User is properly logged out (dashboard redirects)")
    else:
        print("❌ User is still logged in")
        return False
    
    # Clean up
    user.delete()
    
    print("\n" + "=" * 40)
    print("🎉 All logout tests passed!")
    return True

if __name__ == '__main__':
    success = test_logout_functionality()
    sys.exit(0 if success else 1) 