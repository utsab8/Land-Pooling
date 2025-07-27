#!/usr/bin/env python3
"""
Test to verify admin panel logout functionality
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_admin_logout():
    """Test admin panel logout functionality"""
    print("🧪 Testing Admin Panel Logout...")
    print("=" * 40)
    
    client = Client()
    
    # Create a test admin user
    try:
        admin_user = User.objects.create_user(
            username='admin_test',
            email='admin_test@example.com',
            password='adminpass123'
        )
        # Make the user a staff member (admin)
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        print("✅ Admin test user created successfully")
    except Exception as e:
        # User might already exist, try to get it
        try:
            admin_user = User.objects.get(username='admin_test')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password('adminpass123')
            admin_user.save()
            print("✅ Admin test user already exists, updated")
        except:
            print(f"❌ Failed to create/get admin test user: {e}")
            return False
    
    # Login the admin user
    login_success = client.login(username='admin_test@example.com', password='adminpass123')
    if not login_success:
        print("❌ Failed to login admin user")
        return False
    
    print("✅ Admin user logged in successfully")

    # Test admin dashboard access when logged in
    print("\n🔄 Testing admin dashboard access (logged in)...")
    response = client.get('/admin-dashboard/')
    if response.status_code == 200:
        print("✅ Admin dashboard accessible when logged in")
    else:
        print(f"❌ Admin dashboard not accessible when logged in. Status: {response.status_code}")
        return False

    # Test logout
    print("\n🔄 Testing admin logout...")
    response = client.get('/logout/')  # Use GET for simplicity, custom_logout handles it
    print(f"   Status code: {response.status_code}")
    print(f"   Redirect URL: {response.url if hasattr(response, 'url') else 'No redirect'}")
    
    if response.status_code == 302 and response.url == '/api/account/login-page/':
        print("✅ Admin logout redirects to login page correctly!")
    else:
        print("❌ Admin logout failed to redirect to login page.")
        return False

    # Verify admin is logged out by trying to access admin dashboard
    print("\n🔄 Testing admin dashboard access (logged out)...")
    response = client.get('/admin-dashboard/')
    if response.status_code == 302:
        # Check if it's a redirect to login page
        if hasattr(response, 'url') and response.url == '/api/account/login-page/':
            print("✅ Admin dashboard redirects when logged out")
        else:
            print(f"❌ Admin dashboard redirected to wrong URL: {response.url if hasattr(response, 'url') else 'No URL'}")
            return False
    else:
        print(f"❌ Admin dashboard accessible when logged out. Status: {response.status_code}")
        return False

    # Verify login page is accessible
    print("\n🔄 Testing login page access...")
    response = client.get('/api/account/login-page/')
    if response.status_code == 200:
        print("✅ Login page accessible")
    else:
        print(f"❌ Login page not accessible. Status: {response.status_code}")
        return False

    print("\n==================================================")
    print("🎉 Admin logout functionality test passed!")
    return True

if __name__ == '__main__':
    test_admin_logout() 