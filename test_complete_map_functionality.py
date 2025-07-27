#!/usr/bin/env python3
"""
Comprehensive test for map functionality
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
from userdashboard.models import UploadedParcel, KMLData, KMLFile
import json

User = get_user_model()

def test_complete_map_functionality():
    """Test complete map functionality"""
    print("🗺️  Testing Complete Map Functionality...")
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
    
    # Test 1: Check if data exists
    print("\n📊 Test 1: Data Availability")
    uploaded_parcels = UploadedParcel.objects.filter(user=user)
    user_kml_files = KMLFile.objects.filter(user=user)
    kml_data = KMLData.objects.filter(kml_file__in=user_kml_files)
    
    print(f"   UploadedParcel count: {uploaded_parcels.count()}")
    print(f"   KMLFile count: {user_kml_files.count()}")
    print(f"   KMLData count: {kml_data.count()}")
    
    if uploaded_parcels.count() > 0 or kml_data.count() > 0:
        print("   ✅ Data available for map display")
    else:
        print("   ⚠️  No data available - map will show empty state")
    
    # Test 2: Test GeoJSON API
    print("\n🗺️  Test 2: GeoJSON API")
    response = client.get('/dashboard/geojson-data/')
    print(f"   API Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            features = data.get('features', [])
            print(f"   ✅ API working: {len(features)} features")
            
            if features:
                print("   📍 Sample feature data:")
                feature = features[0]
                props = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                
                print(f"      Name: {props.get('name', 'Unknown')}")
                print(f"      Type: {props.get('file_type', 'Unknown')}")
                print(f"      Geometry Type: {geometry.get('type', 'Unknown')}")
                print(f"      Coordinates: {geometry.get('coordinates', 'None')}")
                
                # Validate coordinates
                coords = geometry.get('coordinates', [])
                if coords and len(coords) >= 2:
                    print(f"      ✅ Valid coordinates: {coords}")
                else:
                    print(f"      ❌ Invalid coordinates: {coords}")
            else:
                print("   ℹ️  No features in response")
        except Exception as e:
            print(f"   ❌ Error parsing response: {e}")
    else:
        print("   ❌ API not working")
    
    # Test 3: Test Dashboard View
    print("\n🌐 Test 3: Dashboard View")
    response = client.get('/dashboard/geospatial-dashboard/')
    print(f"   Dashboard Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Dashboard accessible")
        
        # Check response content
        content = response.content.decode('utf-8')
        
        # Check for map container
        if 'id="map"' in content:
            print("   ✅ Map container found in HTML")
        else:
            print("   ❌ Map container missing from HTML")
        
        # Check for Leaflet CSS
        if 'leaflet.css' in content:
            print("   ✅ Leaflet CSS included")
        else:
            print("   ❌ Leaflet CSS missing")
        
        # Check for Leaflet JS
        if 'leaflet.js' in content:
            print("   ✅ Leaflet JS included")
        else:
            print("   ❌ Leaflet JS missing")
        
        # Check for map initialization
        if 'initializeMap' in content:
            print("   ✅ Map initialization function found")
        else:
            print("   ❌ Map initialization function missing")
        
        # Check for data loading
        if 'loadData' in content:
            print("   ✅ Data loading function found")
        else:
            print("   ❌ Data loading function missing")
        
    else:
        print("   ❌ Dashboard not accessible")
    
    # Test 4: Test with filters
    print("\n🔍 Test 4: Filtered Data")
    response = client.get('/dashboard/geojson-data/?file_type=KML')
    print(f"   Filtered API Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            features = data.get('features', [])
            print(f"   ✅ Filtered API working: {len(features)} features")
        except Exception as e:
            print(f"   ❌ Error parsing filtered response: {e}")
    else:
        print("   ❌ Filtered API not working")
    
    print("\n" + "=" * 60)
    print("🎉 Complete map functionality test finished!")
    print("\n💡 Next Steps:")
    print("1. Open browser console (F12)")
    print("2. Go to: http://127.0.0.1:8000/dashboard/geospatial-dashboard/")
    print("3. Check console for map initialization logs")
    print("4. Look for any JavaScript errors")
    print("5. Verify map displays with data")

if __name__ == '__main__':
    test_complete_map_functionality() 