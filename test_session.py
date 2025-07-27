#!/usr/bin/env python3
"""
Test session authentication
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

def test_session_authentication():
    """Test session authentication"""
    print("🔍 Testing Session Authentication...")
    
    client = Client()
    
    # Get admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    print(f"👤 Using admin user: {admin_user.email}")
    
    # Test login
    login_success = client.login(username=admin_user.email, password='admin123')
    print(f"🔍 Login success: {login_success}")
    
    if not login_success:
        print("❌ Login failed")
        return False
    
    # Test session
    session = client.session
    print(f"🔍 Session ID: {session.session_key}")
    print(f"🔍 Session data: {dict(session)}")
    
    # Test users API
    response = client.get('/admin-dashboard/api/users/')
    print(f"📊 Users API Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Users API working with session!")
        return True
    else:
        print(f"❌ Users API failed: {response.status_code}")
        print(f"Response: {response.content.decode()}")
        return False

def show_session_fix():
    """Show how to fix session issues"""
    print("\n" + "="*60)
    print("🔧 SESSION AUTHENTICATION FIX")
    print("="*60)
    
    print("The issue is that the API calls are not maintaining the session.")
    print("Here's how to fix it:")
    print()
    
    print("1️⃣ Make sure you're logged in:")
    print("   - Go to: http://127.0.0.1:8000/")
    print("   - Login with: acharyautsab390@gmail.com / admin123")
    print()
    
    print("2️⃣ Check if you're logged in:")
    print("   - Go to: http://127.0.0.1:8000/admin-dashboard/")
    print("   - If you see the dashboard, you're logged in")
    print()
    
    print("3️⃣ Test the API directly:")
    print("   - Go to: http://127.0.0.1:8000/admin-dashboard/api/users/")
    print("   - You should see JSON data with all users")
    print()
    
    print("4️⃣ If the API works directly but not from JavaScript:")
    print("   - The issue is with CSRF tokens or session cookies")
    print("   - Check browser console for more details")

if __name__ == "__main__":
    print("🚀 Testing Session Authentication\n")
    
    success = test_session_authentication()
    
    if success:
        print("\n✅ Session authentication is working!")
        print("🔍 The issue might be in the browser JavaScript")
    else:
        print("\n❌ Session authentication issue detected")
        show_session_fix()
    
    print("\n✨ Test completed!") 