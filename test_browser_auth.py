#!/usr/bin/env python3
"""
Test browser authentication
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

def test_browser_authentication():
    """Test browser authentication flow"""
    print("🔍 Testing Browser Authentication Flow...")
    
    client = Client()
    
    # Get admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    print(f"👤 Using admin user: {admin_user.email}")
    
    # Step 1: Test login page
    response = client.get('/api/account/login-page/')
    print(f"📊 Login page status: {response.status_code}")
    
    # Step 2: Test login via API
    login_data = {
        'email': admin_user.email,
        'password': 'admin123'
    }
    response = client.post('/api/account/login/', login_data)
    print(f"📊 Login API response status: {response.status_code}")
    
    # Step 3: Check if logged in
    response = client.get('/admin-dashboard/')
    print(f"📊 Admin dashboard status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Login failed")
        return False
    
    print("✅ Login successful!")
    
    # Step 4: Test users page
    response = client.get('/admin-dashboard/users/')
    print(f"📊 Users page status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Users page failed")
        return False
    
    print("✅ Users page accessible!")
    
    # Step 5: Test users API
    response = client.get('/admin-dashboard/api/users/')
    print(f"📊 Users API status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Users API working!")
        return True
    else:
        print(f"❌ Users API failed: {response.status_code}")
        return False

def show_browser_instructions():
    """Show instructions for browser testing"""
    print("\n" + "="*60)
    print("🌐 BROWSER AUTHENTICATION TESTING")
    print("="*60)
    
    print("The issue might be with the browser session. Let's test step by step:")
    print()
    
    print("1️⃣ Clear your browser cache and cookies:")
    print("   - Press Ctrl+Shift+Delete")
    print("   - Select 'All time' and check all boxes")
    print("   - Click 'Clear data'")
    print()
    
    print("2️⃣ Open a new incognito/private window:")
    print("   - Press Ctrl+Shift+N (Chrome) or Ctrl+Shift+P (Firefox)")
    print()
    
    print("3️⃣ Go to the login page:")
    print("   - Navigate to: http://127.0.0.1:8000/accounts/login/")
    print()
    
    print("4️⃣ Login with these credentials:")
    print("   - Username: acharyautsab390@gmail.com")
    print("   - Password: admin123")
    print()
    
    print("5️⃣ After login, go to users page:")
    print("   - Navigate to: http://127.0.0.1:8000/admin-dashboard/users/")
    print()
    
    print("6️⃣ Check browser console (F12):")
    print("   - Look for any authentication errors")
    print("   - Check if the API call is made")
    print()
    
    print("7️⃣ Test API directly:")
    print("   - Go to: http://127.0.0.1:8000/admin-dashboard/api/users/")
    print("   - You should see JSON data with all users")

if __name__ == "__main__":
    print("🚀 Testing Browser Authentication\n")
    
    success = test_browser_authentication()
    
    if success:
        print("\n✅ Backend authentication is working!")
        print("🔍 The issue is likely in the browser session")
        show_browser_instructions()
    else:
        print("\n❌ Backend authentication issue detected")
    
    print("\n✨ Test completed!") 