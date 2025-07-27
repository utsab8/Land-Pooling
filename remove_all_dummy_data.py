#!/usr/bin/env python3
"""
Comprehensive script to remove ALL dummy data from the geospatial dashboard
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from userdashboard.models import UploadedParcel, KMLData, CSVData, ShapefileData, FileUpload
from django.db.models import Q

def remove_all_dummy_data():
    print("🧹 Removing ALL dummy data...")
    print("=" * 50)
    
    # Remove ALL parcels that contain dummy/shapefile/test data
    dummy_parcels = UploadedParcel.objects.filter(
        Q(name__icontains='Dummy') | 
        Q(name__icontains='Shapefile') | 
        Q(name__icontains='Test') | 
        Q(name__icontains='Sample') |
        Q(name__icontains='SHP-') |
        Q(kitta_no__icontains='SHP-') |
        Q(sn_no__icontains='SN-')
    )
    
    dummy_count = dummy_parcels.count()
    if dummy_count > 0:
        print(f"Found {dummy_count} dummy parcels to remove:")
        for parcel in dummy_parcels:
            print(f"   - {parcel.name} (Kitta: {parcel.kitta_no}, Type: {parcel.file_type})")
        dummy_parcels.delete()
        print("✅ All dummy parcels removed")
    else:
        print("ℹ️  No dummy parcels found")
    
    # Remove ALL KML data that might be dummy
    dummy_kml = KMLData.objects.filter(
        Q(placemark_name__icontains='Dummy') | 
        Q(placemark_name__icontains='Test') | 
        Q(placemark_name__icontains='Sample') |
        Q(placemark_name__icontains='Shapefile')
    )
    dummy_kml_count = dummy_kml.count()
    if dummy_kml_count > 0:
        print(f"Found {dummy_kml_count} dummy KML records")
        dummy_kml.delete()
        print("✅ Dummy KML data removed")
    else:
        print("ℹ️  No dummy KML data found")
    
    # Remove ALL CSV data that might be dummy
    dummy_csv = CSVData.objects.filter(
        Q(data__icontains='Dummy') | 
        Q(data__icontains='Test') | 
        Q(data__icontains='Sample') |
        Q(data__icontains='Shapefile')
    )
    dummy_csv_count = dummy_csv.count()
    if dummy_csv_count > 0:
        print(f"Found {dummy_csv_count} dummy CSV records")
        dummy_csv.delete()
        print("✅ Dummy CSV data removed")
    else:
        print("ℹ️  No dummy CSV data found")
    
    # Remove ALL shapefile data that might be dummy
    dummy_shp = ShapefileData.objects.filter(
        Q(attributes__icontains='Dummy') | 
        Q(attributes__icontains='Test') | 
        Q(attributes__icontains='Sample') |
        Q(attributes__icontains='Shapefile')
    )
    dummy_shp_count = dummy_shp.count()
    if dummy_shp_count > 0:
        print(f"Found {dummy_shp_count} dummy shapefile records")
        dummy_shp.delete()
        print("✅ Dummy shapefile data removed")
    else:
        print("ℹ️  No dummy shapefile data found")
    
    # Remove orphaned files
    orphaned_files = FileUpload.objects.filter(
        Q(original_filename__icontains='Dummy') | 
        Q(original_filename__icontains='Test') | 
        Q(original_filename__icontains='Sample') |
        Q(original_filename__icontains='shapefile')
    )
    orphaned_count = orphaned_files.count()
    if orphaned_count > 0:
        print(f"Found {orphaned_count} orphaned dummy files")
        orphaned_files.delete()
        print("✅ Orphaned dummy files removed")
    else:
        print("ℹ️  No orphaned dummy files found")
    
    # Remove ALL data for a clean start (optional - uncomment if you want to start completely fresh)
    # print("\n🗑️  Removing ALL data for clean start...")
    # UploadedParcel.objects.all().delete()
    # KMLData.objects.all().delete()
    # CSVData.objects.all().delete()
    # ShapefileData.objects.all().delete()
    # FileUpload.objects.all().delete()
    # print("✅ All data removed for clean start")
    
    print("\n" + "=" * 50)
    print("🎉 Dummy data removal completed!")
    print("\n📊 Current Data Statistics:")
    print(f"Total Parcels: {UploadedParcel.objects.count()}")
    print(f"Total KML Records: {KMLData.objects.count()}")
    print(f"Total CSV Records: {CSVData.objects.count()}")
    print(f"Total Shapefile Records: {ShapefileData.objects.count()}")
    print(f"Total File Uploads: {FileUpload.objects.count()}")
    
    # Show remaining parcels
    remaining_parcels = UploadedParcel.objects.all()
    if remaining_parcels.exists():
        print(f"\n📋 Remaining Parcels ({remaining_parcels.count()}):")
        for parcel in remaining_parcels:
            print(f"   📍 {parcel.name} (Kitta: {parcel.kitta_no}, Type: {parcel.file_type})")
    else:
        print("\n📋 No parcels remaining - table will be empty")
        print("   💡 Upload your own KML/CSV files to see data!")

if __name__ == '__main__':
    remove_all_dummy_data() 