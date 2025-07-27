#!/usr/bin/env python3
"""
Debug session authentication issue
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

def test_session_debug():
    """Debug session authentication"""
    print("🔍 Debugging Session Authentication...")
    
    client = Client()
    
    # Get admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    print(f"👤 Using admin user: {admin_user.email}")
    
    # Step 1: Check initial session
    response = client.get('/admin-dashboard/api/users/')
    print(f"📊 Initial API call status: {response.status_code}")
    print(f"📊 Session key before login: {client.session.session_key}")
    
    # Step 2: Login via API
    login_data = {
        'email': admin_user.email,
        'password': 'admin123'
    }
    response = client.post('/api/account/login/', login_data)
    print(f"📊 Login API response status: {response.status_code}")
    print(f"📊 Session key after login: {client.session.session_key}")
    print(f"📊 Session data: {dict(client.session)}")
    
    if response.status_code != 200:
        print("❌ Login failed")
        return False
    
    print("✅ Login successful!")
    
    # Step 3: Test API call immediately after login
    response = client.get('/admin-dashboard/api/users/')
    print(f"📊 API call after login status: {response.status_code}")
    print(f"📊 Session key: {client.session.session_key}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API working! Found {len(data.get('users', []))} users")
        return True
    else:
        print(f"❌ API still failing: {response.status_code}")
        return False

def show_session_instructions():
    """Show instructions for session debugging"""
    print("\n" + "="*60)
    print("🔧 SESSION DEBUGGING INSTRUCTIONS")
    print("="*60)
    
    print("The issue might be with session persistence. Try these steps:")
    print()
    
    print("1️⃣ Check Django settings:")
    print("   - Make sure SESSION_ENGINE is set to 'django.contrib.sessions.backends.db'")
    print("   - Verify SESSION_COOKIE_AGE is not too short")
    print("   - Check SESSION_COOKIE_SECURE and SESSION_COOKIE_HTTPONLY")
    print()
    
    print("2️⃣ Clear all browser data:")
    print("   - Press Ctrl+Shift+Delete")
    print("   - Select 'All time'")
    print("   - Check ALL boxes (cookies, cache, etc.)")
    print("   - Click 'Clear data'")
    print()
    
    print("3️⃣ Test in incognito mode:")
    print("   - Press Ctrl+Shift+N")
    print("   - Go to http://127.0.0.1:8000/")
    print("   - Login with admin credentials")
    print("   - Check if session persists")
    print()
    
    print("4️⃣ Check browser console:")
    print("   - Press F12")
    print("   - Go to Network tab")
    print("   - Look for session cookies in requests")
    print()

if __name__ == "__main__":
    print("🚀 Debugging Session Authentication\n")
    
    success = test_session_debug()
    
    if success:
        print("\n✅ Session authentication is working in tests!")
        print("🔍 The issue might be browser-specific")
        show_session_instructions()
    else:
        print("\n❌ Session authentication issue detected")
    
    print("\n✨ Debug completed!") 