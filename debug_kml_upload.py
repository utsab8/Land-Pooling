#!/usr/bin/env python3
"""
Debug script to test KML upload and identify issues
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
import xml.etree.ElementTree as ET
import json

User = get_user_model()

def debug_kml_parsing():
    """Debug KML parsing issues"""
    print("🔍 Debugging KML Upload Issues...")
    print("=" * 50)
    
    # Test different KML formats
    test_kmls = [
        {
            'name': 'Simple KML with Point',
            'content': '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Test Point</name>
      <description>Kitta No: 12345, District: Kathmandu</description>
      <Point>
        <coordinates>85.3240,27.7172</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>'''
        },
        {
            'name': 'KML with ExtendedData',
            'content': '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Extended Data Test</name>
      <ExtendedData>
        <SimpleData name="kitta_no">67890</SimpleData>
        <SimpleData name="district">Lalitpur</SimpleData>
        <SimpleData name="municipality">Lalitpur Metro</SimpleData>
      </ExtendedData>
      <Point>
        <coordinates>85.3340,27.6672</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>'''
        },
        {
            'name': 'KML with Polygon',
            'content': '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Polygon Test</name>
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
        }
    ]
    
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
    
    # Clear existing data
    UploadedParcel.objects.filter(user=user).delete()
    
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
            else:
                print(f"   ❌ Error: {result.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            try:
                print(f"   Response: {response.content.decode()}")
            except:
                pass
    
    # Check final results
    print(f"\n📊 Final Results:")
    parcels = UploadedParcel.objects.filter(user=user)
    print(f"   Total parcels: {parcels.count()}")
    
    for parcel in parcels:
        print(f"   📍 {parcel.name}")
        print(f"      🏷️  Kitta: {parcel.kitta_no}")
        print(f"      🏛️  District: {parcel.district}")
        print(f"      📄 Type: {parcel.file_type}")
        print(f"      📍 Geometry: {parcel.geometry}")
        print()

def test_manual_kml_parsing():
    """Test KML parsing manually"""
    print("\n🔧 Manual KML Parsing Test...")
    print("=" * 50)
    
    # Test KML content
    kml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Manual Test</name>
      <description>Kitta No: 99999, District: Test District</description>
      <ExtendedData>
        <SimpleData name="kitta_no">99999</SimpleData>
        <SimpleData name="district">Test District</SimpleData>
      </ExtendedData>
      <Point>
        <coordinates>85.3240,27.7172</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>'''
    
    try:
        # Parse manually
        root = ET.fromstring(kml_content)
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        placemarks = root.findall('.//kml:Placemark', ns)
        print(f"   Found {len(placemarks)} placemarks")
        
        for i, placemark in enumerate(placemarks):
            print(f"   Placemark {i+1}:")
            
            # Extract name
            name_elem = placemark.find('kml:name', ns)
            name = name_elem.text if name_elem is not None else 'Unnamed'
            print(f"      Name: {name}")
            
            # Extract description
            desc_elem = placemark.find('kml:description', ns)
            description = desc_elem.text if desc_elem is not None else ''
            print(f"      Description: {description}")
            
            # Extract ExtendedData
            extended_data = placemark.find('kml:ExtendedData', ns)
            if extended_data is not None:
                print(f"      ExtendedData found:")
                simple_data_elements = extended_data.findall('.//kml:SimpleData', ns)
                for simple_data in simple_data_elements:
                    name_attr = simple_data.get('name', '')
                    value = simple_data.text if simple_data.text else ''
                    print(f"         {name_attr}: {value}")
            
            # Extract geometry
            point = placemark.find('.//kml:Point', ns)
            if point is not None:
                coords_elem = point.find('kml:coordinates', ns)
                if coords_elem is not None:
                    coords_text = coords_elem.text.strip()
                    print(f"      Coordinates: {coords_text}")
                    
                    coords = coords_text.split(',')
                    if len(coords) >= 2:
                        lon, lat = float(coords[0]), float(coords[1])
                        print(f"      Parsed: lon={lon}, lat={lat}")
        
        print("   ✅ Manual parsing successful")
        
    except Exception as e:
        print(f"   ❌ Manual parsing failed: {e}")

if __name__ == '__main__':
    debug_kml_parsing()
    test_manual_kml_parsing() 