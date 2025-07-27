#!/usr/bin/env python3
"""
Debug script to test map functionality and identify issues
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

def debug_map_issue():
    """Debug map display issues"""
    print("🔍 Debugging Map Display Issue...")
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
    
    # Check current data
    print("\n📊 Current Data Status:")
    uploaded_parcels = UploadedParcel.objects.filter(user=user)
    user_kml_files = KMLFile.objects.filter(user=user)
    kml_data = KMLData.objects.filter(kml_file__in=user_kml_files)
    
    print(f"   UploadedParcel count: {uploaded_parcels.count()}")
    print(f"   KMLFile count: {user_kml_files.count()}")
    print(f"   KMLData count: {kml_data.count()}")
    
    # Show sample data
    if uploaded_parcels.exists():
        print("\n📋 Sample UploadedParcel data:")
        parcel = uploaded_parcels.first()
        print(f"   ID: {parcel.id}")
        print(f"   Name: {parcel.name}")
        print(f"   File Type: {parcel.file_type}")
        print(f"   Geometry: {parcel.geometry}")
        print(f"   Coordinates: {parcel.coordinates}")
    
    if kml_data.exists():
        print("\n📋 Sample KMLData:")
        kml_item = kml_data.first()
        print(f"   ID: {kml_item.id}")
        print(f"   Name: {kml_item.placemark_name}")
        print(f"   Geometry Type: {kml_item.geometry_type}")
        print(f"   Coordinates: {kml_item.coordinates}")
    
    # Test GeoJSON API
    print("\n🗺️  Testing GeoJSON API...")
    response = client.get('/dashboard/geojson-data/')
    print(f"   GeoJSON API Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            features = data.get('features', [])
            print(f"   ✅ GeoJSON API working: {len(features)} features")
            
            if features:
                print("   📍 Sample feature:")
                feature = features[0]
                props = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                
                print(f"      Properties: {props}")
                print(f"      Geometry Type: {geometry.get('type', 'Unknown')}")
                print(f"      Coordinates: {geometry.get('coordinates', 'None')}")
                
                # Check if coordinates are valid
                coords = geometry.get('coordinates', [])
                if coords and len(coords) >= 2:
                    print(f"      ✅ Valid coordinates: {coords}")
                else:
                    print(f"      ❌ Invalid coordinates: {coords}")
            else:
                print("   ⚠️  No features in GeoJSON response")
        except Exception as e:
            print(f"   ❌ Error parsing GeoJSON: {e}")
    else:
        print("   ❌ GeoJSON API not working")
    
    # Test dashboard view
    print("\n🌐 Testing Dashboard View...")
    response = client.get('/dashboard/geospatial-dashboard/')
    print(f"   Dashboard Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Dashboard accessible")
        
        # Check if data is in context
        context = response.context
        if context:
            parcels = context.get('parcels', [])
            stats = context.get('stats', {})
            
            print(f"   📋 Parcels in context: {len(parcels)}")
            print(f"   📊 Statistics: {stats}")
            
            if parcels:
                print("   ✅ Data is being passed to template")
                for i, parcel in enumerate(parcels[:2]):  # Show first 2
                    if isinstance(parcel, dict):
                        print(f"      Parcel {i+1}: {parcel.get('name', 'Unknown')} ({parcel.get('file_type', 'Unknown')})")
                        print(f"         Geometry: {parcel.get('geometry', 'None')}")
                    else:
                        print(f"      Parcel {i+1}: {parcel.name} ({parcel.file_type})")
                        print(f"         Geometry: {parcel.geometry}")
            else:
                print("   ⚠️  No parcels in context")
        else:
            print("   ⚠️  No context available")
    else:
        print("   ❌ Dashboard not accessible")
    
    print("\n" + "=" * 50)
    print("🎉 Map debugging completed!")

if __name__ == '__main__':
    debug_map_issue() 