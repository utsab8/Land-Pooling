#!/usr/bin/env python3
"""
Test script to verify geospatial dashboard functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from userdashboard.models import UploadedParcel
from django.core.files.uploadedfile import SimpleUploadedFile
import json

User = get_user_model()

def test_geospatial_functionality():
    """Test the geospatial dashboard functionality"""
    client = Client()
    
    print("🔍 Testing Geospatial Dashboard Functionality...")
    print("=" * 60)
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'full_name': 'Test User',
            'phone_number': '1234567890',
            'password': 'testpass123'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Test user created")
    else:
        print("ℹ️  Test user already exists")
    
    # Login the user
    login_success = client.login(email='test@example.com', password='testpass123')
    if login_success:
        print("✅ User logged in successfully")
    else:
        print("❌ Login failed")
        return
    
    # Test 1: Access geospatial dashboard
    print("\n1. Testing geospatial dashboard access...")
    response = client.get('/dashboard/geospatial-dashboard/')
    print(f"   Dashboard access -> Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Dashboard accessible")
    else:
        print("   ❌ Dashboard not accessible")
    
    # Test 2: Check GeoJSON API endpoint
    print("\n2. Testing GeoJSON API endpoint...")
    response = client.get('/dashboard/geojson-data/')
    print(f"   GeoJSON API -> Status: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   ✅ GeoJSON API working, returned {len(data.get('features', []))} features")
        except:
            print("   ❌ Invalid JSON response")
    else:
        print("   ❌ GeoJSON API not working")
    
    # Test 3: Test file upload endpoint
    print("\n3. Testing file upload endpoint...")
    
    # Create a simple KML file content
    kml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Test Point</name>
      <description>Kitta No: 123, District: Test District</description>
      <Point>
        <coordinates>85.3240,27.7172</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>'''
    
    # Create a test file
    test_file = SimpleUploadedFile(
        "test.kml",
        kml_content.encode('utf-8'),
        content_type='application/vnd.google-earth.kml+xml'
    )
    
    # Test upload
    response = client.post('/dashboard/upload-parcel/', {
        'file': test_file
    })
    
    print(f"   File upload -> Status: {response.status_code}")
    if response.status_code == 200:
        try:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ File upload successful: {result.get('message')}")
            else:
                print(f"   ❌ Upload failed: {result.get('error')}")
        except:
            print("   ❌ Invalid JSON response")
    else:
        print("   ❌ Upload endpoint not working")
    
    # Test 4: Check if data appears in GeoJSON API
    print("\n4. Testing data retrieval after upload...")
    response = client.get('/dashboard/geojson-data/')
    if response.status_code == 200:
        try:
            data = response.json()
            features = data.get('features', [])
            print(f"   ✅ Retrieved {len(features)} features from API")
            
            if features:
                feature = features[0]
                props = feature.get('properties', {})
                print(f"   📍 Sample feature: {props.get('name', 'Unknown')}")
                print(f"   🏷️  Kitta No: {props.get('kitta_no', 'N/A')}")
                print(f"   🏛️  District: {props.get('district', 'N/A')}")
            else:
                print("   ℹ️  No features found in API response")
        except Exception as e:
            print(f"   ❌ Error parsing API response: {e}")
    else:
        print("   ❌ Could not retrieve data from API")
    
    # Test 5: Test filtering
    print("\n5. Testing filter functionality...")
    response = client.get('/dashboard/geojson-data/?district=Test District')
    if response.status_code == 200:
        try:
            data = response.json()
            features = data.get('features', [])
            print(f"   ✅ Filter working: {len(features)} features match filter")
        except:
            print("   ❌ Filter not working properly")
    else:
        print("   ❌ Filter endpoint not working")
    
    # Test 6: Check database records
    print("\n6. Testing database records...")
    parcels = UploadedParcel.objects.filter(user=user)
    print(f"   📊 Total parcels in database: {parcels.count()}")
    
    if parcels.exists():
        parcel = parcels.first()
        print(f"   📍 Sample parcel: {parcel.name}")
        print(f"   🏷️  Kitta No: {parcel.kitta_no}")
        print(f"   🏛️  District: {parcel.district}")
        print(f"   📄 File Type: {parcel.file_type}")
        print(f"   📅 Uploaded: {parcel.uploaded_at}")
    else:
        print("   ℹ️  No parcels found in database")
    
    print("\n" + "=" * 60)
    print("🎉 Geospatial functionality test completed!")

if __name__ == '__main__':
    test_geospatial_functionality() 