#!/usr/bin/env python3
"""
Simple test script to verify KML upload functionality
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

User = get_user_model()

def test_kml_upload():
    """Test KML upload functionality"""
    print("🌍 Testing KML Upload Functionality...")
    print("=" * 50)
    
    client = Client()
    
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
    
    # Login the user
    login_success = client.login(email='test@example.com', password='testpass123')
    if not login_success:
        print("❌ Login failed")
        return
    
    print("✅ User logged in successfully")
    
    # Clear existing test data
    UploadedParcel.objects.filter(user=user).delete()
    print("🧹 Cleared existing test data")
    
    # Test KML file
    kml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Test Parcel</name>
      <description>Kitta No: 12345, District: Kathmandu, Municipality: Kathmandu Metro</description>
      <ExtendedData>
        <SimpleData name="kitta_no">12345</SimpleData>
        <SimpleData name="district">Kathmandu</SimpleData>
        <SimpleData name="municipality">Kathmandu Metro</SimpleData>
        <SimpleData name="ward">1</SimpleData>
        <SimpleData name="location">Thamel, Kathmandu</SimpleData>
      </ExtendedData>
      <Point>
        <coordinates>85.3240,27.7172</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>'''
    
    # Create test file
    test_file = SimpleUploadedFile(
        "test_parcel.kml",
        kml_content.encode('utf-8'),
        content_type='application/vnd.google-earth.kml+xml'
    )
    
    print("\n📤 Uploading KML file...")
    
    # Test upload
    response = client.post('/dashboard/upload-parcel/', {
        'file': test_file
    })
    
    print(f"   Upload Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ Success: {result.get('message')}")
        else:
            print(f"   ❌ Error: {result.get('error')}")
            return
    else:
        print(f"   ❌ HTTP Error: {response.status_code}")
        return
    
    # Check database
    print("\n📊 Checking database...")
    parcels = UploadedParcel.objects.filter(user=user)
    print(f"   Total parcels: {parcels.count()}")
    
    for parcel in parcels:
        print(f"   📍 Parcel: {parcel.name}")
        print(f"      🏷️  Kitta No: {parcel.kitta_no}")
        print(f"      🏛️  District: {parcel.district}")
        print(f"      🏘️  Municipality: {parcel.municipality}")
        print(f"      🏘️  Ward: {parcel.ward}")
        print(f"      📍 Location: {parcel.location}")
        print(f"      📄 File Type: {parcel.file_type}")
        print(f"      📍 Geometry: {parcel.geometry}")
    
    # Test GeoJSON API
    print("\n🗺️  Testing GeoJSON API...")
    response = client.get('/dashboard/geojson-data/')
    if response.status_code == 200:
        data = response.json()
        features = data.get('features', [])
        print(f"   ✅ GeoJSON API: {len(features)} features")
        
        if features:
            feature = features[0]
            props = feature.get('properties', {})
            print(f"   📍 Feature: {props.get('name', 'Unknown')}")
            print(f"      🏷️  Kitta: {props.get('kitta_no', 'N/A')}")
            print(f"      🏛️  District: {props.get('district', 'N/A')}")
    else:
        print("   ❌ GeoJSON API not working")
    
    print("\n" + "=" * 50)
    print("🎉 KML upload test completed successfully!")
    print("\n💡 How to use:")
    print("1. Go to http://127.0.0.1:8000/dashboard/geospatial-dashboard/")
    print("2. Drag & drop or click to upload your KML file")
    print("3. The file will be processed and displayed on the map and table")
    print("4. Use filters to search and filter your data")

if __name__ == '__main__':
    test_kml_upload() 