#!/usr/bin/env python3
"""
Check and fix admin user permissions
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def check_and_fix_admin_user():
    """Check and fix admin user permissions"""
    print("🔍 Checking Admin User Permissions...")
    print("=" * 50)
    
    # Find the user by email
    try:
        user = User.objects.get(email='acharyautsab390@gmail.com')
        print(f"✅ Found user: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   Full Name: {user.full_name}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")
        print(f"   Is Active: {user.is_active}")
        
        # Check if user needs admin permissions
        if not user.is_staff:
            print("\n🔧 User is not staff. Making user admin...")
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print("✅ User now has admin permissions!")
        else:
            print("\n✅ User already has admin permissions!")
            
        # Verify the fix
        user.refresh_from_db()
        print(f"\n📋 Updated User Status:")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")
        
        return True
        
    except User.DoesNotExist:
        print("❌ User with email 'acharyautsab390@gmail.com' not found!")
        print("   Please create the user first or check the email address.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def list_all_users():
    """List all users in the system"""
    print("\n👥 All Users in System:")
    print("=" * 30)
    
    users = User.objects.all()
    for user in users:
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")
        print(f"   Is Active: {user.is_active}")
        print("   " + "-" * 20)

if __name__ == '__main__':
    success = check_and_fix_admin_user()
    if success:
        list_all_users()
    else:
        print("\n❌ Failed to fix admin user permissions.") 