#!/usr/bin/env python3
"""
Test script to verify logout functionality
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
from django.urls import reverse

User = get_user_model()

def test_logout_functionality():
    """Test the logout functionality"""
    print("🧪 Testing Logout Functionality...")
    print("=" * 50)
    
    client = Client()
    
    # Create a test user
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
    
    print(f"✅ Test user created: {user.email}")
    
    # Test 1: Login the user
    print("\n1. Testing user login...")
    login_success = client.login(email='test@example.com', password='testpass123')
    if login_success:
        print("✅ User logged in successfully")
        
        # Check if user is authenticated
        response = client.get('/dashboard/')
        if response.status_code == 200:
            print("✅ User can access dashboard (authenticated)")
        else:
            print("❌ User cannot access dashboard")
    else:
        print("❌ Login failed")
        return
    
    # Test 2: Test logout
    print("\n2. Testing logout...")
    logout_response = client.post('/logout/')
    print(f"   Logout response status: {logout_response.status_code}")
    
    if logout_response.status_code in [200, 302]:
        print("✅ Logout request successful")
        
        # Check if user is logged out
        dashboard_response = client.get('/dashboard/')
        if dashboard_response.status_code == 302:
            print("✅ User is properly logged out (redirected)")
        else:
            print("❌ User is still authenticated")
    else:
        print("❌ Logout failed")
    
    # Test 3: Verify logout redirect
    print("\n3. Testing logout redirect...")
    if logout_response.status_code == 302:
        redirect_url = logout_response.url
        print(f"   Redirect URL: {redirect_url}")
        
        if '/api/account/login-page/' in redirect_url or '/login/' in redirect_url:
            print("✅ Logout redirects to login page")
        else:
            print("⚠️  Logout redirects to unexpected URL")
    else:
        print("❌ No redirect after logout")
    
    # Test 4: Test accessing protected pages after logout
    print("\n4. Testing access to protected pages after logout...")
    protected_pages = [
        '/dashboard/',
        '/dashboard/uploads/',
        '/dashboard/profile/',
        '/dashboard/geospatial-dashboard/'
    ]
    
    for page in protected_pages:
        response = client.get(page)
        if response.status_code == 302:
            print(f"✅ {page} - Properly protected (redirected)")
        else:
            print(f"❌ {page} - Not properly protected (status: {response.status_code})")
    
    print("\n" + "=" * 50)
    print("🎉 Logout functionality test completed!")
    
    # Cleanup
    if created:
        user.delete()
        print("🧹 Test user cleaned up")

if __name__ == '__main__':
    test_logout_functionality() 