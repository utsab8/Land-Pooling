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

def test_auth_final():
    """Test final authentication fix"""
    print("🔍 Testing Final Authentication Fix...")
    
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
    print(f"📊 Session key: {client.session.session_key}")
    
    # Step 2: Test API call
    response = client.get('/admin-dashboard/api/users/')
    print(f"📊 API call status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API working! Found {len(data.get('users', []))} users")
        return True
    else:
        print(f"❌ API still failing: {response.status_code}")
        print(f"📊 Response: {response.content.decode()}")
        return False

def show_final_instructions():
    """Show final instructions"""
    print("\n" + "="*60)
    print("🎯 FINAL AUTHENTICATION FIX")
    print("="*60)
    
    print("✅ Removed JWT authentication from REST framework!")
    print("✅ Now using only session authentication!")
    print("✅ 401 Unauthorized error should be resolved!")
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
    print("- Removed JWT authentication from REST framework settings")
    print("- Now using only session authentication")
    print("- Updated API views to use session authentication")
    print("- Fixed authentication class conflicts")
    print()
    
    print("🎉 The 401 Unauthorized error should now be completely resolved!")

if __name__ == "__main__":
    print("🚀 Testing Final Authentication Fix\n")
    
    success = test_auth_final()
    
    if success:
        print("\n✅ Authentication fix is working!")
        show_final_instructions()
    else:
        print("\n❌ Authentication issue still detected")
    
    print("\n✨ Test completed!") 