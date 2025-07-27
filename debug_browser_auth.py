#!/usr/bin/env python3
"""
Debug browser authentication issue
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

def debug_browser_auth():
    """Debug browser authentication issue"""
    print("🔍 Debugging Browser Authentication Issue...")
    
    client = Client()
    
    # Get admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    print(f"👤 Using admin user: {admin_user.email}")
    
    # Step 1: Check initial state
    print("\n📊 Step 1: Initial State")
    response = client.get('/admin-dashboard/api/users/')
    print(f"   API call status: {response.status_code}")
    print(f"   Session key: {client.session.session_key}")
    print(f"   User authenticated: {response.wsgi_request.user.is_authenticated}")
    
    # Step 2: Login via API
    print("\n📊 Step 2: Login via API")
    login_data = {
        'email': admin_user.email,
        'password': 'admin123'
    }
    response = client.post('/api/account/login/', login_data)
    print(f"   Login API response status: {response.status_code}")
    print(f"   Session key after login: {client.session.session_key}")
    print(f"   Session data: {dict(client.session)}")
    
    if response.status_code != 200:
        print("❌ Login failed")
        return False
    
    print("✅ Login successful!")
    
    # Step 3: Test API call immediately after login
    print("\n📊 Step 3: API Call After Login")
    response = client.get('/admin-dashboard/api/users/')
    print(f"   API call status: {response.status_code}")
    print(f"   Session key: {client.session.session_key}")
    print(f"   User authenticated: {response.wsgi_request.user.is_authenticated}")
    print(f"   User is staff: {response.wsgi_request.user.is_staff}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API working! Found {len(data.get('users', []))} users")
        return True
    else:
        print(f"❌ API still failing: {response.status_code}")
        print(f"   Response content: {response.content.decode()}")
        return False

def show_debug_instructions():
    """Show debug instructions"""
    print("\n" + "="*60)
    print("🔧 BROWSER AUTHENTICATION DEBUG INSTRUCTIONS")
    print("="*60)
    
    print("The backend is working, but browser session is not maintained.")
    print("This is likely due to one of these issues:")
    print()
    
    print("1️⃣ SESSION COOKIE ISSUE:")
    print("   - Browser might be blocking session cookies")
    print("   - Check browser settings for cookie permissions")
    print("   - Try disabling browser extensions")
    print()
    
    print("2️⃣ CSRF TOKEN ISSUE:")
    print("   - CSRF token might not be included in requests")
    print("   - Check if CSRF token is being sent")
    print()
    
    print("3️⃣ MIDDLEWARE ISSUE:")
    print("   - Session middleware might not be working")
    print("   - Check Django middleware order")
    print()
    
    print("4️⃣ BROWSER CACHE ISSUE:")
    print("   - Hard refresh: Ctrl+F5")
    print("   - Clear all browser data completely")
    print("   - Try different browser")
    print()
    
    print("5️⃣ TEST IN BROWSER CONSOLE:")
    print("   - Press F12")
    print("   - Go to Console tab")
    print("   - Run this JavaScript:")
    print("     fetch('/admin-dashboard/api/users/', {")
    print("       credentials: 'same-origin',")
    print("       headers: {")
    print("         'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value")
    print("       }")
    print("     })")
    print("   - Check the response")

if __name__ == "__main__":
    print("🚀 Debugging Browser Authentication\n")
    
    success = debug_browser_auth()
    
    if success:
        print("\n✅ Backend authentication is working!")
        print("🔍 The issue is browser-specific")
        show_debug_instructions()
    else:
        print("\n❌ Backend authentication issue detected")
    
    print("\n✨ Debug completed!") 