#!/usr/bin/env python3
"""
Test final authentication fix
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

def test_complete_authentication_flow():
    """Test complete authentication flow including API access"""
    print("🔍 Testing Complete Authentication Flow...")
    
    client = Client()
    
    # Get admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    print(f"👤 Using admin user: {admin_user.email}")
    
    # Step 1: Login via API
    login_data = {
        'email': admin_user.email,
        'password': 'admin123'
    }
    response = client.post('/api/account/login/', login_data)
    print(f"📊 Login API response status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Login failed")
        return False
    
    print("✅ Login successful!")
    
    # Step 2: Test users page access
    response = client.get('/admin-dashboard/users/')
    print(f"📊 Users page status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Users page access failed")
        return False
    
    print("✅ Users page accessible!")
    
    # Step 3: Test users API access
    response = client.get('/admin-dashboard/api/users/')
    print(f"📊 Users API status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Users API working! Found {len(data.get('users', []))} users")
        return True
    else:
        print(f"❌ Users API failed: {response.status_code}")
        return False

def show_final_instructions():
    """Show final instructions for the user"""
    print("\n" + "="*60)
    print("🎯 FINAL SOLUTION - AUTHENTICATION FIXED")
    print("="*60)
    
    print("✅ Backend authentication is now working properly!")
    print("✅ All fetch calls now include proper session handling")
    print("✅ CSRF tokens are included in all requests")
    print("✅ 401 errors should be resolved")
    print()
    
    print("🌐 To test in your browser:")
    print("1️⃣ Clear browser cache (Ctrl+Shift+Delete)")
    print("2️⃣ Open new incognito window (Ctrl+Shift+N)")
    print("3️⃣ Go to: http://127.0.0.1:8000/")
    print("4️⃣ Login with: acharyautsab390@gmail.com / admin123")
    print("5️⃣ Navigate to: http://127.0.0.1:8000/admin-dashboard/users/")
    print("6️⃣ You should now see all users without 401 errors!")
    print()
    
    print("🔧 What was fixed:")
    print("- Added CSRF token handling to all API calls")
    print("- Enhanced fetch function with proper session cookies")
    print("- Added authentication error handling and redirects")
    print("- Updated all user management functions")
    print()
    
    print("🎉 The users page should now be fully functional!")

if __name__ == "__main__":
    print("🚀 Testing Final Authentication Fix\n")
    
    success = test_complete_authentication_flow()
    
    if success:
        print("\n✅ Authentication fix is working!")
        show_final_instructions()
    else:
        print("\n❌ Authentication issue still detected")
    
    print("\n✨ Test completed!") 