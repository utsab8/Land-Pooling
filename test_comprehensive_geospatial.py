#!/usr/bin/env python3
"""
Comprehensive test script for geospatial dashboard functionality
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

def test_comprehensive_geospatial():
    """Comprehensive test of geospatial dashboard functionality"""
    client = Client()
    
    print("🔍 Comprehensive Geospatial Dashboard Test...")
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
    if not login_success:
        print("❌ Login failed")
        return
    
    print("✅ User logged in successfully")
    
    # Clear existing test data
    UploadedParcel.objects.filter(user=user).delete()
    print("🧹 Cleared existing test data")
    
    # Test 1: Upload KML file with ExtendedData
    print("\n1. Testing KML upload with ExtendedData...")
    
    kml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Test Parcel 1</name>
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
    <Placemark>
      <name>Test Parcel 2</name>
      <description>Kitta No: 67890, District: Lalitpur</description>
      <ExtendedData>
        <SimpleData name="kitta_no">67890</SimpleData>
        <SimpleData name="district">Lalitpur</SimpleData>
        <SimpleData name="municipality">Lalitpur Metro</SimpleData>
        <SimpleData name="ward">5</SimpleData>
      </ExtendedData>
      <Point>
        <coordinates>85.3340,27.6672</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>'''
    
    test_file = SimpleUploadedFile(
        "test_parcels.kml",
        kml_content.encode('utf-8'),
        content_type='application/vnd.google-earth.kml+xml'
    )
    
    response = client.post('/dashboard/upload-parcel/', {
        'file': test_file
    })
    
    print(f"   KML upload -> Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ KML upload successful: {result.get('message')}")
        else:
            print(f"   ❌ KML upload failed: {result.get('error')}")
    else:
        print("   ❌ KML upload endpoint not working")
    
    # Test 2: Upload CSV file
    print("\n2. Testing CSV upload...")
    
    csv_content = '''name,kitta_no,district,municipality,ward,latitude,longitude
CSV Parcel 1,11111,Bhaktapur,Bhaktapur Metro,1,27.6712,85.4280
CSV Parcel 2,22222,Bhaktapur,Bhaktapur Metro,2,27.6812,85.4180'''
    
    csv_file = SimpleUploadedFile(
        "test_parcels.csv",
        csv_content.encode('utf-8'),
        content_type='text/csv'
    )
    
    response = client.post('/dashboard/upload-parcel/', {
        'file': csv_file
    })
    
    print(f"   CSV upload -> Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ CSV upload successful: {result.get('message')}")
        else:
            print(f"   ❌ CSV upload failed: {result.get('error')}")
    else:
        print("   ❌ CSV upload endpoint not working")
    
    # Test 3: Check GeoJSON API
    print("\n3. Testing GeoJSON API...")
    response = client.get('/dashboard/geojson-data/')
    if response.status_code == 200:
        data = response.json()
        features = data.get('features', [])
        print(f"   ✅ GeoJSON API working: {len(features)} features")
        
        for i, feature in enumerate(features[:3]):  # Show first 3 features
            props = feature.get('properties', {})
            print(f"   📍 Feature {i+1}: {props.get('name', 'Unknown')}")
            print(f"      🏷️  Kitta: {props.get('kitta_no', 'N/A')}")
            print(f"      🏛️  District: {props.get('district', 'N/A')}")
            print(f"      🏘️  Municipality: {props.get('municipality', 'N/A')}")
    else:
        print("   ❌ GeoJSON API not working")
    
    # Test 4: Test filtering
    print("\n4. Testing filter functionality...")
    
    # Test district filter
    response = client.get('/dashboard/geojson-data/?district=Kathmandu')
    if response.status_code == 200:
        data = response.json()
        features = data.get('features', [])
        print(f"   ✅ District filter (Kathmandu): {len(features)} features")
    
    # Test municipality filter
    response = client.get('/dashboard/geojson-data/?municipality=Bhaktapur Metro')
    if response.status_code == 200:
        data = response.json()
        features = data.get('features', [])
        print(f"   ✅ Municipality filter (Bhaktapur Metro): {len(features)} features")
    
    # Test kitta_no filter
    response = client.get('/dashboard/geojson-data/?kitta_no=12345')
    if response.status_code == 200:
        data = response.json()
        features = data.get('features', [])
        print(f"   ✅ Kitta filter (12345): {len(features)} features")
    
    # Test 5: Check database records
    print("\n5. Testing database records...")
    parcels = UploadedParcel.objects.filter(user=user)
    print(f"   📊 Total parcels in database: {parcels.count()}")
    
    for parcel in parcels:
        print(f"   📍 Parcel: {parcel.name}")
        print(f"      🏷️  Kitta: {parcel.kitta_no}")
        print(f"      🏛️  District: {parcel.district}")
        print(f"      🏘️  Municipality: {parcel.municipality}")
        print(f"      📄 Type: {parcel.file_type}")
        print(f"      📅 Uploaded: {parcel.uploaded_at}")
        print()
    
    # Test 6: Test dashboard access
    print("\n6. Testing dashboard access...")
    response = client.get('/dashboard/geospatial-dashboard/')
    if response.status_code == 200:
        print("   ✅ Dashboard accessible")
        # Check if the response contains expected content
        content = response.content.decode('utf-8')
        if 'geospatial-dashboard' in content:
            print("   ✅ Dashboard content loaded properly")
        else:
            print("   ⚠️  Dashboard content may be incomplete")
    else:
        print("   ❌ Dashboard not accessible")
    
    print("\n" + "=" * 60)
    print("🎉 Comprehensive geospatial test completed!")

if __name__ == '__main__':
    test_comprehensive_geospatial() 