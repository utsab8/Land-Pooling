#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

def test_csv_upload_flow():
    """Test the complete CSV upload flow"""
    print("Testing CSV upload flow...")
    
    # Create a test client
    client = Client()
    
    # Get or create a test user
    User = get_user_model()
    try:
        user = User.objects.get(email='demo@example.com')
        print(f"Found existing user: {user.username}")
    except User.DoesNotExist:
        print("Creating test user...")
        user = User.objects.create_user(
            username='demo_user',
            email='demo@example.com',
            password='demo123'
        )
    
    # Set password for the user
    user.set_password('demo123')
    user.save()
    print("Password set for demo_user")
    
    # Login the user
    login_success = client.login(username='demo_user', password='demo123')
    if not login_success:
        print("❌ Failed to login test user")
        return
    
    print("✅ User logged in successfully")
    
    # Test accessing the file upload page
    response = client.get('/dashboard/files/upload/')
    if response.status_code == 200:
        print("✅ File upload page accessible")
    else:
        print(f"❌ File upload page not accessible: {response.status_code}")
        return
    
    # Test uploading a CSV file
    csv_path = 'sample_files/sample.csv'
    if not os.path.exists(csv_path):
        print(f"❌ Sample CSV file not found: {csv_path}")
        return
    
    print("📁 Uploading sample CSV file...")
    
    # Read the CSV file content
    with open(csv_path, 'rb') as f:
        csv_content = f.read()
    
    # Create a SimpleUploadedFile
    csv_file = SimpleUploadedFile(
        name='sample.csv',
        content=csv_content,
        content_type='text/csv'
    )
    
    # Upload the file
    response = client.post('/dashboard/files/upload/', {
        'file': csv_file,
        'file_type': 'csv'
    }, follow=True)
    
    print(f"Upload response status: {response.status_code}")
    print(f"Redirect chain: {[r.url for r in response.redirect_chain]}")
    
    # Check if we were redirected to CSV preview
    if response.status_code == 200:
        final_url = response.url
        print(f"Final URL: {final_url}")
        
        if 'csv-preview' in final_url or any('csv-preview' in r.url for r in response.redirect_chain):
            print("✅ Successfully redirected to CSV preview page!")
            
            # Check the final response content
            content = response.content.decode()
            if 'CSV Preview' in content or 'csv-preview' in final_url:
                print("✅ CSV preview page loaded successfully!")
            else:
                print("⚠️  CSV preview page content not as expected")
                print(f"Content preview: {content[:200]}...")
        else:
            print(f"❌ Not redirected to CSV preview. Final URL: {final_url}")
            print(f"Response content preview: {response.content.decode()[:500]}...")
    else:
        print(f"❌ Upload failed with status: {response.status_code}")
        print(f"Response content: {response.content.decode()[:500]}")

if __name__ == "__main__":
    test_csv_upload_flow() 