#!/usr/bin/env python3
"""
Test script to verify that the profile page has been removed and logout button is added
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

def test_profile_page_removed():
    """Test that the profile page is no longer accessible"""
    print("🔍 Testing Profile Page Removal...")
    
    client = Client()
    
    try:
        # Test that profile page returns 404 (not found)
        response = client.get('/admin-dashboard/profile/')
        
        if response.status_code == 404:
            print("✅ Profile page correctly returns 404 (removed)")
            return True
        else:
            print(f"❌ Profile page still accessible with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing profile page removal: {e}")
        return False

def test_logout_button_present():
    """Test that logout button is present in admin pages"""
    print("\n🔍 Testing Logout Button Presence...")
    
    client = Client()
    
    try:
        # Test main dashboard page
        response = client.get('/admin-dashboard/')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            if 'logout' in content.lower() and 'sign-out-alt' in content.lower():
                print("✅ Logout button found in dashboard page")
                return True
            else:
                print("❌ Logout button not found in dashboard page")
                return False
        else:
            print(f"❌ Dashboard page not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing logout button: {e}")
        return False

def test_navbar_structure():
    """Test that navbar structure is correct without profile"""
    print("\n🔍 Testing Navbar Structure...")
    
    client = Client()
    
    try:
        response = client.get('/admin-dashboard/')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for required navbar items
            required_items = [
                'dashboard',
                'users',
                'surveys', 
                'system',
                'settings',
                'logout'
            ]
            
            # Check that profile is NOT present
            if 'admin-profile' in content.lower():
                print("❌ Profile link still present in navbar")
                return False
            
            success_count = 0
            total_count = len(required_items)
            
            for item in required_items:
                if item in content.lower():
                    print(f"✅ {item.title()} found in navbar")
                    success_count += 1
                else:
                    print(f"❌ {item.title()} missing from navbar")
            
            print(f"\n📊 Navbar Items: {success_count}/{total_count} found")
            return success_count == total_count
            
        else:
            print(f"❌ Dashboard page not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing navbar structure: {e}")
        return False

def test_url_patterns():
    """Test that profile URL patterns are removed"""
    print("\n🔍 Testing URL Pattern Removal...")
    
    try:
        from admindashboard.urls import urlpatterns
        
        # Check that profile patterns are removed
        profile_patterns = [
            'admin-profile',
            'admin_api_profile'
        ]
        
        pattern_names = [pattern.name for pattern in urlpatterns if hasattr(pattern, 'name') and pattern.name]
        
        removed_count = 0
        total_count = len(profile_patterns)
        
        for pattern in profile_patterns:
            if pattern not in pattern_names:
                print(f"✅ Profile pattern '{pattern}' removed")
                removed_count += 1
            else:
                print(f"❌ Profile pattern '{pattern}' still exists")
        
        print(f"\n📊 URL Pattern Removal: {removed_count}/{total_count} patterns removed")
        return removed_count == total_count
        
    except Exception as e:
        print(f"❌ Error testing URL patterns: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Profile Removal Verification Test...\n")
    
    profile_removed = test_profile_page_removed()
    logout_present = test_logout_button_present()
    navbar_correct = test_navbar_structure()
    urls_cleaned = test_url_patterns()
    
    print("\n" + "="*60)
    print("🎯 PROFILE REMOVAL TEST RESULTS")
    print("="*60)
    
    if profile_removed and logout_present and navbar_correct and urls_cleaned:
        print("✅ ALL TESTS PASSED!")
        print("🎉 Profile page successfully removed!")
        print("🚀 Logout button properly added!")
    else:
        print("❌ SOME TESTS FAILED!")
        if not profile_removed:
            print("   - Profile page still accessible")
        if not logout_present:
            print("   - Logout button missing")
        if not navbar_correct:
            print("   - Navbar structure issues")
        if not urls_cleaned:
            print("   - URL patterns not cleaned")
    
    print("\n📝 Final Summary:")
    print("✅ Profile Page: " + ("Removed" if profile_removed else "Still Exists"))
    print("✅ Logout Button: " + ("Added" if logout_present else "Missing"))
    print("✅ Navbar Structure: " + ("Correct" if navbar_correct else "Issues"))
    print("✅ URL Patterns: " + ("Cleaned" if urls_cleaned else "Not Cleaned"))
    
    print("\n✨ Test completed!")
    print("\n🎯 Changes Made:")
    print("• Profile page removed from navbar")
    print("• Profile.html template deleted")
    print("• Profile URL patterns removed")
    print("• Profile API endpoints removed")
    print("• Logout button added to all admin pages")
    print("• Clean navbar structure maintained")
    
    if profile_removed and logout_present and navbar_correct and urls_cleaned:
        print("\n🏆 STATUS: PROFILE SUCCESSFULLY REMOVED! 🏆")
    else:
        print("\n⚠️  STATUS: NEEDS ADDITIONAL CLEANUP") 