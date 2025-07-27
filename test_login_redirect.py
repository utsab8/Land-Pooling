#!/usr/bin/env python3
"""
Test login redirect functionality for admin and regular users
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_login_redirects():
    """Test login redirects for different user types"""
    print("🧪 Testing Login Redirects...")
    print("=" * 50)
    
    client = Client()
    
    # Test 1: Admin user login
    print("\n🔄 Testing Admin User Login...")
    print("   Email: acharyautsab390@gmail.com")
    print("   Password: utsab12@")
    
    # Login as admin user
    login_success = client.login(username='acharyautsab390@gmail.com', password='utsab12@')
    if login_success:
        print("✅ Admin user login successful")
        
        # Check if user is staff
        user = User.objects.get(email='acharyautsab390@gmail.com')
        if user.is_staff:
            print("✅ User has admin permissions")
            
            # Test admin dashboard access
            response = client.get('/admin-dashboard/')
            if response.status_code == 200:
                print("✅ Admin dashboard accessible")
            else:
                print(f"❌ Admin dashboard not accessible. Status: {response.status_code}")
        else:
            print("❌ User does not have admin permissions")
    else:
        print("❌ Admin user login failed")
    
    # Logout
    client.logout()
    print("   Logged out admin user")
    
    # Test 2: Regular user login
    print("\n🔄 Testing Regular User Login...")
    print("   Email: utsabacharya12@gmail.com")
    print("   Password: (using any valid password)")
    
    # Create a test regular user if needed
    try:
        regular_user = User.objects.get(email='utsabacharya12@gmail.com')
        # Set a simple password for testing
        regular_user.set_password('testpass123')
        regular_user.save()
        print("✅ Regular user found and password set")
    except User.DoesNotExist:
        print("❌ Regular user not found")
        return False
    
    # Login as regular user
    login_success = client.login(username='utsabacharya12@gmail.com', password='testpass123')
    if login_success:
        print("✅ Regular user login successful")
        
        # Check if user is NOT staff
        user = User.objects.get(email='utsabacharya12@gmail.com')
        if not user.is_staff:
            print("✅ User does not have admin permissions (correct)")
            
            # Test user dashboard access
            response = client.get('/dashboard/')
            if response.status_code == 200:
                print("✅ User dashboard accessible")
            else:
                print(f"❌ User dashboard not accessible. Status: {response.status_code}")
                
            # Test admin dashboard access (should redirect)
            response = client.get('/admin-dashboard/')
            if response.status_code == 302:
                print("✅ Admin dashboard properly redirects regular users")
            else:
                print(f"❌ Admin dashboard accessible to regular user. Status: {response.status_code}")
        else:
            print("❌ Regular user has admin permissions (incorrect)")
    else:
        print("❌ Regular user login failed")
    
    # Logout
    client.logout()
    print("   Logged out regular user")
    
    print("\n==================================================")
    print("🎉 Login redirect tests completed!")
    return True

def test_api_login_redirects():
    """Test API login redirects"""
    print("\n🧪 Testing API Login Redirects...")
    print("=" * 50)
    
    client = Client()
    
    # Test admin user API login
    print("\n🔄 Testing Admin User API Login...")
    response = client.post('/api/account/login/', {
        'email': 'acharyautsab390@gmail.com',
        'password': 'utsab12@'
    })
    
    if response.status_code == 200:
        data = response.json()
        redirect_url = data.get('redirect_url', '')
        print(f"✅ Admin API login successful")
        print(f"   Redirect URL: {redirect_url}")
        
        if redirect_url == '/admin-dashboard/':
            print("✅ Admin user correctly redirected to admin dashboard")
        else:
            print(f"❌ Admin user redirected to wrong URL: {redirect_url}")
    else:
        print(f"❌ Admin API login failed. Status: {response.status_code}")
    
    # Test regular user API login
    print("\n🔄 Testing Regular User API Login...")
    response = client.post('/api/account/login/', {
        'email': 'utsabacharya12@gmail.com',
        'password': 'testpass123'
    })
    
    if response.status_code == 200:
        data = response.json()
        redirect_url = data.get('redirect_url', '')
        print(f"✅ Regular user API login successful")
        print(f"   Redirect URL: {redirect_url}")
        
        if redirect_url == '/dashboard/':
            print("✅ Regular user correctly redirected to user dashboard")
        else:
            print(f"❌ Regular user redirected to wrong URL: {redirect_url}")
    else:
        print(f"❌ Regular user API login failed. Status: {response.status_code}")
    
    print("\n==================================================")
    print("🎉 API login redirect tests completed!")

if __name__ == '__main__':
    test_login_redirects()
    test_api_login_redirects() 