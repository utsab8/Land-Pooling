#!/usr/bin/env python3
"""
Test the complete logout flow from user profile to login page
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_complete_logout_flow():
    """Test the complete logout flow"""
    print("🚪 Testing Complete Logout Flow...")
    print("=" * 50)
    
    client = Client()
    
    # Create a test user
    try:
        user = User.objects.create_user(
            username='testuser_flow',
            email='test_flow@example.com',
            password='testpass123'
        )
        print("✅ Test user created successfully")
    except Exception as e:
        # User might already exist, try to get it
        try:
            user = User.objects.get(username='testuser_flow')
            user.set_password('testpass123')
            user.save()
            print("✅ Test user already exists, password reset")
        except:
            print(f"❌ Failed to create/get test user: {e}")
            return False
    
    # Login the user
    login_success = client.login(username='test_flow@example.com', password='testpass123')
    if not login_success:
        print("❌ Failed to login test user")
        return False
    
    print("✅ User logged in successfully")
    
    # Test accessing dashboard (should work when logged in)
    print("\n🔄 Testing dashboard access (logged in)...")
    response = client.get('/dashboard/')
    if response.status_code == 200:
        print("✅ Dashboard accessible when logged in")
    else:
        print(f"❌ Dashboard not accessible: {response.status_code}")
        return False
    
    # Test logout
    print("\n🔄 Testing logout...")
    response = client.get('/logout/')
    print(f"   Status code: {response.status_code}")
    print(f"   Redirect URL: {response.url if hasattr(response, 'url') else 'No redirect'}")
    
    if response.status_code == 302 and response.url == '/api/account/login-page/':
        print("✅ Logout redirects to login page correctly!")
    else:
        print("❌ Logout failed to redirect to login page")
        return False
    
    # Test accessing login page
    print("\n🔄 Testing login page access...")
    response = client.get('/api/account/login-page/')
    if response.status_code == 200:
        print("✅ Login page accessible")
    else:
        print(f"❌ Login page not accessible: {response.status_code}")
        return False
    
    # Test accessing dashboard after logout (should redirect to login)
    print("\n🔄 Testing dashboard access (logged out)...")
    response = client.get('/dashboard/')
    if response.status_code == 302:
        print("✅ Dashboard redirects when logged out")
    else:
        print(f"❌ Dashboard accessible when should be logged out: {response.status_code}")
        return False
    
    # Clean up
    user.delete()
    
    print("\n" + "=" * 50)
    print("🎉 Complete logout flow test passed!")
    print("\n📋 Summary:")
    print("✅ User can login")
    print("✅ User can access dashboard when logged in")
    print("✅ Logout button works")
    print("✅ Logout redirects to login page")
    print("✅ Login page is accessible")
    print("✅ Dashboard redirects when logged out")
    return True

if __name__ == '__main__':
    success = test_complete_logout_flow()
    exit(0 if success else 1) 