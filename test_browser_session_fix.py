#!/usr/bin/env python3
"""
Test browser session fix
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

def test_browser_session_fix():
    """Test browser session fix"""
    print("🔍 Testing Browser Session Fix...")
    
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
    print(f"📊 Session data: {dict(client.session)}")
    
    # Step 2: Test API call
    response = client.get('/admin-dashboard/api/users/')
    print(f"📊 API call status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API working! Found {len(data.get('users', []))} users")
        return True
    else:
        print(f"❌ API still failing: {response.status_code}")
        return False

def show_browser_fix_instructions():
    """Show browser fix instructions"""
    print("\n" + "="*60)
    print("🌐 BROWSER SESSION FIX INSTRUCTIONS")
    print("="*60)
    
    print("The backend is working perfectly. The issue is browser session management.")
    print("Follow these steps EXACTLY:")
    print()
    
    print("1️⃣ COMPLETELY CLEAR BROWSER DATA:")
    print("   - Press Ctrl+Shift+Delete")
    print("   - Time range: 'All time'")
    print("   - Check ALL boxes:")
    print("     ☑️ Browsing history")
    print("     ☑️ Download history") 
    print("     ☑️ Cookies and other site data")
    print("     ☑️ Cached images and files")
    print("     ☑️ Passwords and other sign-in data")
    print("     ☑️ Autofill form data")
    print("     ☑️ Site settings")
    print("     ☑️ Hosted app data")
    print("   - Click 'Clear data'")
    print()
    
    print("2️⃣ CLOSE ALL BROWSER WINDOWS:")
    print("   - Close ALL browser windows completely")
    print("   - Don't just minimize them")
    print()
    
    print("3️⃣ OPEN NEW INCOGNITO WINDOW:")
    print("   - Press Ctrl+Shift+N (Chrome)")
    print("   - Or Ctrl+Shift+P (Firefox)")
    print()
    
    print("4️⃣ NAVIGATE TO LOGIN PAGE:")
    print("   - Go to: http://127.0.0.1:8000/")
    print("   - You should be redirected to login page")
    print()
    
    print("5️⃣ LOGIN WITH ADMIN CREDENTIALS:")
    print("   - Email: acharyautsab390@gmail.com")
    print("   - Password: admin123")
    print("   - Click Login")
    print()
    
    print("6️⃣ VERIFY REDIRECTION:")
    print("   - You should be redirected to admin dashboard")
    print("   - URL should be: http://127.0.0.1:8000/admin-dashboard/")
    print()
    
    print("7️⃣ TEST USERS PAGE:")
    print("   - Click 'Users' in sidebar")
    print("   - Or go to: http://127.0.0.1:8000/admin-dashboard/users/")
    print("   - You should see all users without 401 errors")
    print()
    
    print("8️⃣ CHECK BROWSER CONSOLE:")
    print("   - Press F12")
    print("   - Go to Console tab")
    print("   - Look for any authentication errors")
    print("   - Should see successful API calls")
    print()
    
    print("🔧 If still getting 401 errors:")
    print("   - Check Network tab in F12")
    print("   - Look for session cookies in requests")
    print("   - Verify CSRF token is being sent")
    print("   - Try a different browser")

if __name__ == "__main__":
    print("🚀 Testing Browser Session Fix\n")
    
    success = test_browser_session_fix()
    
    if success:
        print("\n✅ Backend session authentication is working!")
        print("🔍 The issue is browser-specific session management")
        show_browser_fix_instructions()
    else:
        print("\n❌ Backend session issue detected")
    
    print("\n✨ Test completed!") 