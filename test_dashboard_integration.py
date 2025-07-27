#!/usr/bin/env python3
"""
Test script to verify geospatial dashboard integration with KML data
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
from userdashboard.geospatial_views import GeospatialDashboardView, GeoJSONAPIView

User = get_user_model()

def test_dashboard_integration():
    """Test that the geospatial dashboard properly displays KML data"""
    print("🔍 Testing Geospatial Dashboard Integration...")
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
    
    # Check current data
    print("\n📊 Current Data Status:")
    uploaded_parcels = UploadedParcel.objects.filter(user=user)
    user_kml_files = KMLFile.objects.filter(user=user)
    kml_data = KMLData.objects.filter(kml_file__in=user_kml_files)
    
    print(f"   UploadedParcel count: {uploaded_parcels.count()}")
    print(f"   KMLFile count: {user_kml_files.count()}")
    print(f"   KMLData count: {kml_data.count()}")
    
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
            filter_options = context.get('filter_options', {})
            
            print(f"   📋 Parcels in context: {len(parcels)}")
            print(f"   📊 Statistics: {stats}")
            print(f"   🔍 Filter options: {filter_options}")
            
            if parcels:
                print("   ✅ Data is being passed to template")
                for i, parcel in enumerate(parcels[:3]):  # Show first 3
                    if isinstance(parcel, dict):
                        print(f"      Parcel {i+1}: {parcel.get('name', 'Unknown')} ({parcel.get('file_type', 'Unknown')})")
                    else:
                        print(f"      Parcel {i+1}: {parcel.name} ({parcel.file_type})")
            else:
                print("   ⚠️  No parcels in context")
        else:
            print("   ⚠️  No context available")
    else:
        print("   ❌ Dashboard not accessible")
    
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
                print("   📍 Sample features:")
                for i, feature in enumerate(features[:3]):
                    props = feature.get('properties', {})
                    print(f"      Feature {i+1}: {props.get('name', 'Unknown')} ({props.get('file_type', 'Unknown')})")
            else:
                print("   ⚠️  No features in GeoJSON response")
        except Exception as e:
            print(f"   ❌ Error parsing GeoJSON: {e}")
    else:
        print("   ❌ GeoJSON API not working")
    
    # Test with filters
    print("\n🔍 Testing with filters...")
    response = client.get('/dashboard/geospatial-dashboard/?file_type=KML')
    print(f"   Filtered Dashboard Status: {response.status_code}")
    
    if response.status_code == 200:
        context = response.context
        if context:
            parcels = context.get('parcels', [])
            print(f"   📋 Parcels after KML filter: {len(parcels)}")
    
    print("\n" + "=" * 60)
    print("🎉 Dashboard integration test completed!")

if __name__ == '__main__':
    test_dashboard_integration() 