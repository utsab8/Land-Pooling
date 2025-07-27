#!/usr/bin/env python3
"""
Test login functionality and admin access
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

User = get_user_model()

def test_login():
    """Test login functionality"""
    print("🔍 Testing Login Functionality...")
    
    client = Client()
    
    # Get admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    print(f"👤 Found admin user: {admin_user.username} ({admin_user.email})")
    print(f"   Is Staff: {admin_user.is_staff}")
    print(f"   Is Superuser: {admin_user.is_superuser}")
    
    # Try to login with email as username
    print(f"\n🔐 Attempting login with email: {admin_user.email}")
    login_success = client.login(username=admin_user.email, password='your_password_here')
    
    if login_success:
        print("✅ Login successful!")
        
        # Test admin dashboard access
        response = client.get('/admin-dashboard/')
        print(f"📊 Admin Dashboard Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Admin dashboard accessible!")
            
            # Test users page
            response = client.get('/admin-dashboard/users/')
            print(f"📊 Users Page Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Users page accessible!")
                
                # Test users API
                response = client.get('/admin-dashboard/api/users/')
                print(f"📊 Users API Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Users API working!")
                    return True
                else:
                    print(f"❌ Users API failed: {response.status_code}")
                    print(f"Response: {response.content.decode()}")
            else:
                print(f"❌ Users page failed: {response.status_code}")
        else:
            print(f"❌ Admin dashboard failed: {response.status_code}")
    else:
        print("❌ Login failed!")
        print("💡 Please update the password in this script to match your admin user's password")
    
    return False

def show_login_instructions():
    """Show instructions for manual login"""
    print("\n" + "="*60)
    print("🔧 MANUAL LOGIN INSTRUCTIONS")
    print("="*60)
    
    admin_users = User.objects.filter(is_superuser=True)
    
    print("📝 To access the admin dashboard:")
    print("1. Go to: http://127.0.0.1:8000/")
    print("2. Click 'Login' or go to: http://127.0.0.1:8000/accounts/login/")
    print("3. Use one of these admin accounts:")
    
    for user in admin_users:
        print(f"   👤 Username: {user.email}")
        print(f"      Email: {user.email}")
        print(f"      Is Admin: {user.is_staff}")
        print()
    
    print("4. After login, go to: http://127.0.0.1:8000/admin-dashboard/")
    print("5. Click 'Users' to see all user details")
    print("\n💡 If you don't remember the password, you can reset it using Django admin")

if __name__ == "__main__":
    print("🚀 Testing Login and Admin Access...\n")
    
    success = test_login()
    
    if not success:
        show_login_instructions()
    
    print("\n✨ Test completed!") 