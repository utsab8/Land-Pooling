#!/usr/bin/env python3
"""
Final test to verify everything is working
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

def test_final_working():
    """Test final working state"""
    print("🔍 Testing Final Working State...")
    
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
        print(f"📊 Response keys: {list(data.keys())}")
        return True
    else:
        print(f"❌ API still failing: {response.status_code}")
        print(f"📊 Response: {response.content.decode()}")
        return False

def show_final_solution():
    """Show final solution"""
    print("\n" + "="*60)
    print("🎯 FINAL SOLUTION - AUTHENTICATION FIXED")
    print("="*60)
    
    print("✅ JWT authentication removed from REST framework!")
    print("✅ Session authentication is now the only method!")
    print("✅ Duplicate API views removed!")
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
    print("- Removed duplicate API views that were causing conflicts")
    print("- Updated all API views to use session authentication")
    print("- Fixed authentication class conflicts")
    print()
    
    print("🎉 The 401 Unauthorized error should now be completely resolved!")

if __name__ == "__main__":
    print("🚀 Testing Final Working State\n")
    
    success = test_final_working()
    
    if success:
        print("\n✅ Everything is working perfectly!")
        show_final_solution()
    else:
        print("\n❌ Issue still detected")
    
    print("\n✨ Test completed!") 