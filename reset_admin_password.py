#!/usr/bin/env python3
"""
Reset admin user password
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

def reset_admin_password():
    """Reset admin user password"""
    print("🔧 Resetting Admin Password...")
    
    # Find admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    print(f"👤 Found admin user: {admin_user.username} ({admin_user.email})")
    
    # Set new password
    new_password = "admin123"
    admin_user.set_password(new_password)
    admin_user.save()
    
    print(f"✅ Password reset successfully!")
    print(f"📝 New password: {new_password}")
    print(f"📝 Username: {admin_user.email}")
    
    return True

def show_login_steps():
    """Show step-by-step login instructions"""
    print("\n" + "="*60)
    print("🚀 LOGIN STEPS TO ACCESS USERS PAGE")
    print("="*60)
    
    admin_user = User.objects.filter(is_superuser=True).first()
    
    print("1️⃣ Go to login page:")
    print("   http://127.0.0.1:8000/accounts/login/")
    print()
    
    print("2️⃣ Login with these credentials:")
    print(f"   Username: {admin_user.email}")
    print("   Password: admin123")
    print()
    
    print("3️⃣ After successful login, go to admin dashboard:")
    print("   http://127.0.0.1:8000/admin-dashboard/")
    print()
    
    print("4️⃣ Click 'Users' in the sidebar or go directly to:")
    print("   http://127.0.0.1:8000/admin-dashboard/users/")
    print()
    
    print("5️⃣ You should now see all your user details!")
    print("   - Total Users: 8")
    print("   - Your account: acharyautsab390@gmail.com")
    print("   - All other user accounts")
    print()
    
    print("🎯 The users page will show:")
    print("   ✅ User statistics (Total, Active, New, Suspended)")
    print("   ✅ Search and filter options")
    print("   ✅ User list with details")
    print("   ✅ Actions (View, Edit, Suspend, Delete)")
    print("   ✅ Bulk operations")
    print("   ✅ Export functionality")

if __name__ == "__main__":
    print("🔧 Admin Password Reset Tool\n")
    
    success = reset_admin_password()
    
    if success:
        show_login_steps()
    
    print("\n✨ Setup completed!") 