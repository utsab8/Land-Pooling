#!/usr/bin/env python3
"""
Test script to verify the authentication flow
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
from django.urls import reverse
from account.models import User

def test_auth_flow():
    """Test the authentication flow"""
    client = Client()
    
    print("🔍 Testing Authentication Flow...")
    print("=" * 50)
    
    # Test 1: Root URL redirects to login
    print("1. Testing root URL redirect...")
    response = client.get('/')
    print(f"   Root URL (/) -> Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirects to: {response.url}")
    print()
    
    # Test 2: Login page is accessible
    print("2. Testing login page access...")
    response = client.get('/api/account/login-page/')
    print(f"   Login page -> Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Login page is accessible")
    print()
    
    # Test 3: Dashboard requires authentication
    print("3. Testing dashboard authentication requirement...")
    response = client.get('/dashboard/')
    print(f"   Dashboard (unauthenticated) -> Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirects to: {response.url}")
        print("   ✅ Dashboard properly redirects unauthenticated users")
    print()
    
    # Test 4: Create a test user and login
    print("4. Testing user creation and login...")
    try:
        # Create test user
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
            print("   ✅ Test user created")
        else:
            print("   ℹ️  Test user already exists")
        
        # Test login
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'next': '/dashboard/'
        }
        response = client.post('/api/account/login/', login_data, content_type='application/json')
        print(f"   Login attempt -> Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Login successful")
            
            # Test dashboard access after login
            response = client.get('/dashboard/')
            print(f"   Dashboard (authenticated) -> Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Dashboard accessible after login")
            else:
                print("   ❌ Dashboard not accessible after login")
        else:
            print("   ❌ Login failed")
            
    except Exception as e:
        print(f"   ❌ Error during login test: {e}")
    
    print()
    print("=" * 50)
    print("🎉 Authentication flow test completed!")

if __name__ == '__main__':
    test_auth_flow() 