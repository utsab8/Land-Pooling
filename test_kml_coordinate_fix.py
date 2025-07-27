#!/usr/bin/env python3
"""
Test script to verify KML coordinate parsing fix
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

def test_kml_coordinate_fix():
    """Test KML coordinate parsing with various coordinate formats"""
    print("🧪 Testing KML Coordinate Parsing Fix...")
    print("=" * 60)
    
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
    
    # Test KML with various coordinate formats
    test_kmls = [
        {
            'name': 'Point with 2D coordinates',
            'content': '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Test Point 2D</name>
      <description>Kitta No: 12345, District: Kathmandu</description>
      <Point>
        <coordinates>85.3240,27.7172</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>'''
        },
        {
            'name': 'Point with 3D coordinates (altitude)',
            'content': '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Test Point 3D</name>
      <description>Kitta No: 67890, District: Lalitpur</description>
      <Point>
        <coordinates>85.3340,27.6672,100</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>'''
        },
        {
            'name': 'Polygon with 2D coordinates',
            'content': '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Test Polygon 2D</name>
      <description>Kitta No: 11111, District: Bhaktapur</description>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>85.3240,27.7172 85.3340,27.7172 85.3340,27.7072 85.3240,27.7072 85.3240,27.7172</coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>'''
        },
        {
            'name': 'Polygon with 3D coordinates (altitude)',
            'content': '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Test Polygon 3D</name>
      <description>Kitta No: 22222, District: Patan</description>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>85.3240,27.7172,50 85.3340,27.7172,50 85.3340,27.7072,50 85.3240,27.7072,50 85.3240,27.7172,50</coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>'''
        },
        {
            'name': 'LineString with mixed coordinates',
            'content': '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Test LineString</name>
      <description>Kitta No: 33333, District: Kirtipur</description>
      <LineString>
        <coordinates>85.3240,27.7172 85.3340,27.7172,100 85.3440,27.7072</coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>'''
        }
    ]
    
    successful_uploads = 0
    total_tests = len(test_kmls)
    
    for i, test_kml in enumerate(test_kmls):
        print(f"\n{i+1}. Testing {test_kml['name']}...")
        
        # Create test file
        test_file = SimpleUploadedFile(
            f"test_{i+1}.kml",
            test_kml['content'].encode('utf-8'),
            content_type='application/vnd.google-earth.kml+xml'
        )
        
        # Test upload
        response = client.post('/dashboard/upload-parcel/', {
            'file': test_file
        })
        
        print(f"   Upload Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Success: {result.get('message')}")
                successful_uploads += 1
            else:
                print(f"   ❌ Error: {result.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    
    # Check final results
    print(f"\n📊 Final Results:")
    parcels = UploadedParcel.objects.filter(user=user)
    print(f"   Total parcels created: {parcels.count()}")
    print(f"   Successful uploads: {successful_uploads}/{total_tests}")
    
    if parcels.exists():
        print(f"\n📋 Created Parcels:")
        for parcel in parcels:
            print(f"   📍 {parcel.name}")
            print(f"      🏷️  Kitta: {parcel.kitta_no}")
            print(f"      🏛️  District: {parcel.district}")
            print(f"      📄 Type: {parcel.file_type}")
            print(f"      📍 Geometry: {parcel.geometry}")
            print()
    
    # Test GeoJSON API
    print("🗺️  Testing GeoJSON API...")
    response = client.get('/dashboard/geojson-data/')
    if response.status_code == 200:
        data = response.json()
        features = data.get('features', [])
        print(f"   ✅ GeoJSON API: {len(features)} features")
        
        if features:
            print("   📍 Sample features:")
            for i, feature in enumerate(features[:3]):
                props = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                print(f"      Feature {i+1}: {props.get('name', 'Unknown')}")
                print(f"         Type: {geometry.get('type', 'Unknown')}")
                print(f"         Coordinates: {geometry.get('coordinates', 'None')}")
    else:
        print("   ❌ GeoJSON API not working")
    
    print("\n" + "=" * 60)
    if successful_uploads == total_tests:
        print("🎉 All coordinate parsing tests passed!")
    else:
        print(f"⚠️  {total_tests - successful_uploads} tests failed")

if __name__ == '__main__':
    test_kml_coordinate_fix() 