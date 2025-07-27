#!/usr/bin/env python3
"""
Test current state to identify Bearer authentication issue
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

def test_current_state():
    """Test current state to identify Bearer authentication issue"""
    print("🔍 Testing Current State to Identify Bearer Authentication Issue...")
    
    client = Client()
    
    # Get admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    print(f"👤 Using admin user: {admin_user.email}")
    
    # Step 1: Test API call without authentication
    print("\n📊 Step 1: Testing API without authentication")
    response = client.get('/admin-dashboard/api/users/')
    print(f"   API call status: {response.status_code}")
    print(f"   Response headers: {dict(response.headers)}")
    print(f"   Response content: {response.content.decode()[:200]}...")
    
    # Step 2: Login via API
    print("\n📊 Step 2: Login via API")
    login_data = {
        'email': admin_user.email,
        'password': 'admin123'
    }
    response = client.post('/api/account/login/', login_data)
    print(f"   Login API response status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Login failed")
        return False
    
    print("✅ Login successful!")
    print(f"   Session key: {client.session.session_key}")
    
    # Step 3: Test API call with authentication
    print("\n📊 Step 3: Testing API with authentication")
    response = client.get('/admin-dashboard/api/users/')
    print(f"   API call status: {response.status_code}")
    print(f"   Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API working! Found {len(data.get('users', []))} users")
        return True
    else:
        print(f"❌ API still failing: {response.status_code}")
        print(f"   Response content: {response.content.decode()}")
        return False

def show_debug_info():
    """Show debug information"""
    print("\n" + "="*60)
    print("🔧 DEBUG INFORMATION")
    print("="*60)
    
    print("The Bearer authentication error suggests JWT is still being used.")
    print("Let's check the following:")
    print()
    
    print("1️⃣ Check if Django server was restarted:")
    print("   - Stop the server (Ctrl+C)")
    print("   - Start it again: python manage.py runserver")
    print()
    
    print("2️⃣ Check browser cache:")
    print("   - Clear all browser data")
    print("   - Try incognito mode")
    print()
    
    print("3️⃣ Check if there are any remaining JWT imports:")
    print("   - Look for any remaining JWT references")
    print("   - Check if any middleware is adding Bearer headers")
    print()
    
    print("4️⃣ Test API directly in browser:")
    print("   - Go to: http://127.0.0.1:8000/admin-dashboard/api/users/")
    print("   - Check the response headers")
    print()

if __name__ == "__main__":
    print("🚀 Testing Current State\n")
    
    success = test_current_state()
    
    if success:
        print("\n✅ Backend is working correctly!")
        print("🔍 The issue might be browser-specific")
    else:
        print("\n❌ Backend issue detected")
        show_debug_info()
    
    print("\n✨ Test completed!") 