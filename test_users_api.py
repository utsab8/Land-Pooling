#!/usr/bin/env python3
"""
Simple test to verify users API functionality
"""

import os
import sys
import django
import json
from django.test import Client
from django.contrib.auth import get_user_model

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

User = get_user_model()

def test_users_api():
    """Test the users API endpoint"""
    print("🔍 Testing Users API...")
    
    client = Client()
    
    # Use existing admin user
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            print(f"✅ Using existing admin user: {admin_user.username}")
        else:
            print("❌ No admin user found")
            return False
    except Exception as e:
        print(f"❌ Error finding admin user: {e}")
        return False
    
    # Login as admin
    login_success = client.login(username=admin_user.username, password='your_password_here')
    if not login_success:
        # Try with email as username
        login_success = client.login(username=admin_user.email, password='your_password_here')
    
    if login_success:
        print("✅ Logged in as admin")
    else:
        print("❌ Failed to login as admin")
        print("💡 Please update the password in the test script to match your admin user's password")
        return False
    
    # Test the users API
    try:
        response = client.get('/admin-dashboard/api/users/')
        print(f"📊 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print("✅ Users API working!")
            print(f"📈 Total users: {data.get('stats', {}).get('total_users', 0)}")
            print(f"📈 Active users: {data.get('stats', {}).get('active_users', 0)}")
            print(f"📈 Users in list: {len(data.get('users', []))}")
            
            # Show user details
            users = data.get('users', [])
            if users:
                print("\n👥 Current Users:")
                for user in users[:5]:  # Show first 5 users
                    print(f"  - {user.get('full_name', 'N/A')} ({user.get('username', 'N/A')}) - {user.get('status', 'N/A')}")
            else:
                print("📝 No users found in the system")
            
            return True
        else:
            print(f"❌ Users API failed with status: {response.status_code}")
            print(f"Response content: {response.content.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing users API: {e}")
        return False

def test_users_page():
    """Test the users page"""
    print("\n🔍 Testing Users Page...")
    
    client = Client()
    
    # Use existing admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    # Login as admin
    login_success = client.login(username=admin_user.username, password='your_password_here')
    if not login_success:
        login_success = client.login(username=admin_user.email, password='your_password_here')
    
    if not login_success:
        print("❌ Failed to login as admin")
        return False
    
    try:
        response = client.get('/admin-dashboard/users/')
        print(f"📊 Page Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Users page loads successfully!")
            return True
        else:
            print(f"❌ Users page failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing users page: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Users Functionality...\n")
    
    print("💡 Note: This test requires you to update the password in the script")
    print("💡 Replace 'your_password_here' with your actual admin user password")
    print("💡 Available admin users:")
    
    admin_users = User.objects.filter(is_superuser=True)
    for user in admin_users:
        print(f"   - {user.username} ({user.email})")
    
    print("\n" + "="*60)
    
    api_working = test_users_api()
    page_working = test_users_page()
    
    print("\n" + "="*50)
    print("🎯 TEST RESULTS")
    print("="*50)
    
    if api_working and page_working:
        print("✅ ALL TESTS PASSED!")
        print("🎉 Users functionality is working correctly!")
    else:
        print("❌ SOME TESTS FAILED!")
        if not api_working:
            print("   - Users API issues")
        if not page_working:
            print("   - Users page issues")
    
    print("\n✨ Test completed!") 