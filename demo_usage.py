#!/usr/bin/env python3
"""
Demo script for GeoSurvey File Upload System
This script demonstrates how to use the file upload and processing system programmatically.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from django.contrib.auth import get_user_model
from userdashboard.models import FileUpload, KMLData, CSVData, ShapefileData
from userdashboard.file_utils import FileValidator, FileProcessor, FileConverter
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.db import models

User = get_user_model()

def create_sample_kml():
    """Create a sample KML file for testing"""
    kml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Sample KML File</name>
    <description>This is a sample KML file for testing</description>
    <Placemark>
      <name>Sample Point</name>
      <description>This is a sample point</description>
      <Point>
        <coordinates>-122.4194,37.7749,0</coordinates>
      </Point>
      <ExtendedData>
        <Data name="kitta_number">
          <value>KML001</value>
        </Data>
        <Data name="owner_name">
          <value>John Doe</value>
        </Data>
        <Data name="area_hectares">
          <value>0.5</value>
        </Data>
      </ExtendedData>
    </Placemark>
    <Placemark>
      <name>Sample Polygon</name>
      <description>This is a sample polygon</description>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              -122.4194,37.7749,0
              -122.4194,37.7849,0
              -122.4094,37.7849,0
              -122.4094,37.7749,0
              -122.4194,37.7749,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
      <ExtendedData>
        <Data name="kitta_number">
          <value>KML002</value>
        </Data>
        <Data name="owner_name">
          <value>Jane Smith</value>
        </Data>
        <Data name="area_hectares">
          <value>1.2</value>
        </Data>
      </ExtendedData>
    </Placemark>
  </Document>
</kml>'''
    
    return SimpleUploadedFile(
        "sample.kml",
        kml_content.encode('utf-8'),
        content_type='application/vnd.google-earth.kml+xml'
    )

def create_sample_csv():
    """Create a sample CSV file for testing"""
    csv_content = '''name,description,latitude,longitude,area_hectares,owner_name
Point 1,This is point 1,37.7749,-122.4194,0.5,John Doe
Point 2,This is point 2,37.7849,-122.4094,0.8,Jane Smith
Point 3,This is point 3,37.7949,-122.3994,1.2,Bob Johnson'''
    
    return SimpleUploadedFile(
        "sample.csv",
        csv_content.encode('utf-8'),
        content_type='text/csv'
    )

def demo_file_upload():
    """Demonstrate file upload and processing"""
    print("🚀 Starting GeoSurvey File Upload Demo")
    print("=" * 50)
    
    # Get or create a test user
    try:
        user = User.objects.get(email='demo@example.com')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='demo_user',
            email='demo@example.com',
            password='demo123456'
        )
        print(f"✅ Created demo user: {user.email}")
    
    print(f"👤 Using user: {user.email}")
    print()
    
    # Demo 1: KML File Upload
    print("📁 Demo 1: KML File Upload")
    print("-" * 30)
    
    kml_file = create_sample_kml()
    print(f"📄 Created sample KML file: {kml_file.name}")
    
    # Validate KML file
    validator = FileValidator()
    file_type = validator.detect_file_type(kml_file, kml_file.name)
    validation_result = validator.validate_file(kml_file, kml_file.name, file_type)
    
    if validation_result['errors']:
        print(f"❌ Validation errors: {validation_result['errors']}")
        return
    
    print(f"✅ File validation passed. Detected type: {file_type}")
    
    # Create file upload record
    file_upload = FileUpload.objects.create(
        user=user,
        file=kml_file,
        original_filename=kml_file.name,
        file_type=file_type,
        file_size=kml_file.size,
        status='pending'
    )
    
    print(f"📝 Created file upload record: {file_upload.id}")
    
    # Process the file
    try:
        processor = FileProcessor(file_upload)
        result = processor.process_file()
        
        file_upload.status = 'completed'
        file_upload.save()
        
        print(f"✅ File processing completed successfully!")
        print(f"📊 Processing result: {result}")
        
        # Get processed data
        kml_data = KMLData.objects.filter(kml_file__file_upload=file_upload)
        print(f"📍 Found {kml_data.count()} KML features")
        
        for feature in kml_data:
            print(f"  - {feature.placemark_name}: {feature.geometry_type}")
        
    except Exception as e:
        file_upload.status = 'failed'
        file_upload.error_message = str(e)
        file_upload.save()
        print(f"❌ File processing failed: {e}")
    
    print()
    
    # Demo 2: CSV File Upload
    print("📁 Demo 2: CSV File Upload")
    print("-" * 30)
    
    csv_file = create_sample_csv()
    print(f"📄 Created sample CSV file: {csv_file.name}")
    
    # Validate CSV file
    csv_file.seek(0)  # Reset file pointer
    file_type = validator.detect_file_type(csv_file, csv_file.name)
    validation_result = validator.validate_file(csv_file, csv_file.name, file_type)
    
    if validation_result['errors']:
        print(f"❌ Validation errors: {validation_result['errors']}")
        return
    
    print(f"✅ File validation passed. Detected type: {file_type}")
    
    # Create file upload record
    csv_upload = FileUpload.objects.create(
        user=user,
        file=csv_file,
        original_filename=csv_file.name,
        file_type=file_type,
        file_size=csv_file.size,
        status='pending'
    )
    
    print(f"📝 Created file upload record: {csv_upload.id}")
    
    # Process the file
    try:
        processor = FileProcessor(csv_upload)
        result = processor.process_file()
        
        csv_upload.status = 'completed'
        csv_upload.save()
        
        print(f"✅ File processing completed successfully!")
        print(f"📊 Processing result: {result}")
        
        # Get processed data
        csv_data = CSVData.objects.filter(file_upload=csv_upload)
        print(f"📍 Found {csv_data.count()} CSV rows")
        
        for row in csv_data:
            print(f"  - Row {row.row_number}: {row.data.get('name', 'N/A')}")
        
    except Exception as e:
        csv_upload.status = 'failed'
        csv_upload.error_message = str(e)
        csv_upload.save()
        print(f"❌ File processing failed: {e}")
    
    print()
    
    # Demo 3: File Conversion
    print("🔄 Demo 3: File Conversion")
    print("-" * 30)
    
    # Convert KML to CSV
    try:
        kml_data = KMLData.objects.filter(kml_file__file_upload=file_upload)
        if kml_data.exists():
            filename = f"kml_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
            response = FileConverter.kml_to_csv(kml_data, filename)
            print(f"✅ KML to CSV conversion successful: {filename}.csv")
        else:
            print("⚠️ No KML data available for conversion")
    except Exception as e:
        print(f"❌ KML to CSV conversion failed: {e}")
    
    # Convert CSV to KML
    try:
        csv_data = CSVData.objects.filter(file_upload=csv_upload)
        if csv_data.exists():
            filename = f"csv_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
            response = FileConverter.csv_to_kml(csv_data, filename)
            print(f"✅ CSV to KML conversion successful: {filename}.kml")
        else:
            print("⚠️ No CSV data available for conversion")
    except Exception as e:
        print(f"❌ CSV to KML conversion failed: {e}")
    
    print()
    
    # Demo 4: File Statistics
    print("📊 Demo 4: File Statistics")
    print("-" * 30)
    
    user_files = FileUpload.objects.filter(user=user)
    print(f"📁 Total files uploaded: {user_files.count()}")
    
    files_by_type = {}
    for file_type, _ in FileUpload.FILE_TYPES:
        count = user_files.filter(file_type=file_type).count()
        if count > 0:
            files_by_type[file_type] = count
    
    print("📈 Files by type:")
    for file_type, count in files_by_type.items():
        print(f"  - {file_type.upper()}: {count}")
    
    total_size = user_files.aggregate(total=models.Sum('file_size'))['total'] or 0
    total_size_mb = round(total_size / (1024 * 1024), 2)
    print(f"💾 Total storage used: {total_size_mb} MB")
    
    print()
    print("🎉 Demo completed successfully!")
    print("=" * 50)
    print("🌐 Access the web interface at: http://127.0.0.1:8000/")
    print("📧 Login with: demo@example.com / demo123456")

if __name__ == "__main__":
    demo_file_upload() 