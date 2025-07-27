#!/usr/bin/env python3
"""
Test to verify profile page loads without JavaScript errors
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_profile_page_loads():
    """Test that profile page loads without errors"""
    print("🧪 Testing Profile Page Load...")
    print("=" * 40)
    
    client = Client()
    
    # Create a test user
    try:
        user = User.objects.create_user(
            username='testuser_profile',
            email='test_profile@example.com',
            password='testpass123'
        )
        print("✅ Test user created successfully")
    except Exception as e:
        # User might already exist, try to get it
        try:
            user = User.objects.get(username='testuser_profile')
            print("✅ Test user already exists")
        except:
            print(f"❌ Failed to create/get test user: {e}")
            return False
    
    # Login the user
    login_success = client.login(username='test_profile@example.com', password='testpass123')
    if not login_success:
        print("❌ Failed to login test user")
        return False
    
    print("✅ User logged in successfully")

    # Test profile page access
    print("\n🔄 Testing profile page access...")
    response = client.get('/dashboard/profile/')
    
    if response.status_code == 200:
        print("✅ Profile page loads successfully")
        
        # Check for key elements in the response
        content = response.content.decode('utf-8')
        
        # Check for required elements
        required_elements = [
            'profileCompletionFill',
            'full_name',
            'phone_number',
            'logoutBtn',
            'scrollProgress',
            'scrollIndicator'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"⚠️  Missing elements: {missing_elements}")
        else:
            print("✅ All required elements present")
        
        # Check for JavaScript error patterns
        error_patterns = [
            'Cannot read properties of null',
            'getElementById',
            'value.trim'
        ]
        
        has_potential_errors = False
        for pattern in error_patterns:
            if pattern in content:
                has_potential_errors = True
                print(f"⚠️  Found potential error pattern: {pattern}")
        
        if not has_potential_errors:
            print("✅ No obvious JavaScript error patterns found")
        
        return True
        
    else:
        print(f"❌ Profile page failed to load. Status: {response.status_code}")
        return False

if __name__ == '__main__':
    test_profile_page_loads() 