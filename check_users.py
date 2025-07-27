#!/usr/bin/env python3
"""
Check existing users and their permissions
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def check_users():
    """Check all users in the system"""
    print("🔍 Checking Users in System...\n")
    
    users = User.objects.all()
    
    if not users.exists():
        print("❌ No users found in the system")
        return
    
    print(f"📊 Total users found: {users.count()}\n")
    
    for user in users:
        print(f"👤 User: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Date Joined: {user.date_joined}")
        print(f"   Last Login: {user.last_login}")
        print("-" * 50)
    
    # Check for admin users
    admin_users = users.filter(is_staff=True)
    super_users = users.filter(is_superuser=True)
    
    print(f"\n👑 Admin Users (is_staff=True): {admin_users.count()}")
    for user in admin_users:
        print(f"   - {user.username}")
    
    print(f"\n👑 Super Users (is_superuser=True): {super_users.count()}")
    for user in super_users:
        print(f"   - {user.username}")

def create_admin_user():
    """Create an admin user if none exists"""
    print("\n🔧 Creating Admin User...")
    
    try:
        # Check if admin user already exists
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            print(f"✅ Admin user already exists: {admin_user.username}")
            return admin_user
        
        # Create new admin user
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print(f"✅ Created new admin user: {admin_user.username}")
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return None

if __name__ == "__main__":
    check_users()
    create_admin_user()
    print("\n" + "="*50)
    print("Final User Check:")
    print("="*50)
    check_users() 