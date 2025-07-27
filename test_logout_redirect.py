#!/usr/bin/env python3
"""
Quick test to verify logout redirects to login page
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_logout_redirect():
    """Test that logout redirects to login page"""
    print("🚪 Testing Logout Redirect...")
    print("=" * 40)
    
    client = Client()
    
    # Create and login a test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'full_name': 'Test User',
            'phone_number': '1234567890',
            'password': 'testpass123'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Login the user
    login_success = client.login(email='test@example.com', password='testpass123')
    if not login_success:
        print("❌ Failed to login test user")
        return
    
    print("✅ User logged in successfully")
    
    # Test logout
    print("\n🔄 Testing logout...")
    logout_response = client.post('/logout/')
    
    print(f"   Logout status code: {logout_response.status_code}")
    print(f"   Redirect URL: {logout_response.url}")
    
    if logout_response.status_code == 302:
        if '/api/account/login-page/' in logout_response.url:
            print("✅ Logout successfully redirects to login page!")
        else:
            print(f"❌ Logout redirects to unexpected URL: {logout_response.url}")
    else:
        print("❌ Logout failed")
    
    # Verify user is logged out
    dashboard_response = client.get('/dashboard/')
    if dashboard_response.status_code == 302:
        print("✅ User is properly logged out (dashboard redirects)")
    else:
        print("❌ User is still authenticated")
    
    print("\n" + "=" * 40)
    print("🎉 Logout redirect test completed!")
    
    # Cleanup
    if created:
        user.delete()

if __name__ == '__main__':
    test_logout_redirect() 