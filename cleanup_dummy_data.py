#!/usr/bin/env python3
"""
Script to clean up dummy data from the geospatial dashboard
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from userdashboard.models import UploadedParcel, KMLData, CSVData, ShapefileData, FileUpload
from django.db.models import Q

def cleanup_dummy_data():
    """Remove all dummy data from the database"""
    print("🧹 Cleaning up dummy data...")
    print("=" * 50)
    
    # Remove dummy parcels
    dummy_parcels = UploadedParcel.objects.filter(
        Q(name__icontains='Dummy') |
        Q(name__icontains='Shapefile Feature') |
        Q(name__icontains='Test') |
        Q(name__icontains='Sample')
    )
    
    dummy_count = dummy_parcels.count()
    if dummy_count > 0:
        print(f"Found {dummy_count} dummy parcels")
        dummy_parcels.delete()
        print("✅ Dummy parcels removed")
    else:
        print("ℹ️  No dummy parcels found")
    
    # Remove dummy KML data
    dummy_kml = KMLData.objects.filter(
        Q(placemark_name__icontains='Dummy') |
        Q(placemark_name__icontains='Test') |
        Q(placemark_name__icontains='Sample')
    )
    
    dummy_kml_count = dummy_kml.count()
    if dummy_kml_count > 0:
        print(f"Found {dummy_kml_count} dummy KML records")
        dummy_kml.delete()
        print("✅ Dummy KML data removed")
    else:
        print("ℹ️  No dummy KML data found")
    
    # Remove dummy CSV data
    dummy_csv = CSVData.objects.filter(
        Q(data__icontains='Dummy') |
        Q(data__icontains='Test') |
        Q(data__icontains='Sample')
    )
    
    dummy_csv_count = dummy_csv.count()
    if dummy_csv_count > 0:
        print(f"Found {dummy_csv_count} dummy CSV records")
        dummy_csv.delete()
        print("✅ Dummy CSV data removed")
    else:
        print("ℹ️  No dummy CSV data found")
    
    # Remove dummy shapefile data
    dummy_shp = ShapefileData.objects.filter(
        Q(attributes__icontains='Dummy') |
        Q(attributes__icontains='Test') |
        Q(attributes__icontains='Sample')
    )
    
    dummy_shp_count = dummy_shp.count()
    if dummy_shp_count > 0:
        print(f"Found {dummy_shp_count} dummy shapefile records")
        dummy_shp.delete()
        print("✅ Dummy shapefile data removed")
    else:
        print("ℹ️  No dummy shapefile data found")
    
    # Remove orphaned file uploads
    orphaned_files = FileUpload.objects.filter(
        Q(original_filename__icontains='Dummy') |
        Q(original_filename__icontains='Test') |
        Q(original_filename__icontains='Sample')
    )
    
    orphaned_count = orphaned_files.count()
    if orphaned_count > 0:
        print(f"Found {orphaned_count} orphaned dummy files")
        orphaned_files.delete()
        print("✅ Orphaned dummy files removed")
    else:
        print("ℹ️  No orphaned dummy files found")
    
    print()
    print("=" * 50)
    print("🎉 Dummy data cleanup completed!")
    
    # Show current data statistics
    print("\n📊 Current Data Statistics:")
    print(f"Total Parcels: {UploadedParcel.objects.count()}")
    print(f"Total KML Records: {KMLData.objects.count()}")
    print(f"Total CSV Records: {CSVData.objects.count()}")
    print(f"Total Shapefile Records: {ShapefileData.objects.count()}")
    print(f"Total File Uploads: {FileUpload.objects.count()}")

if __name__ == '__main__':
    cleanup_dummy_data() 