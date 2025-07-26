#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

def test_csv_upload_simple():
    """Test CSV upload without authentication"""
    print("Testing CSV upload (simple version)...")
    
    # Create a test client
    client = Client()
    
    # Test accessing the file upload page (should redirect to login)
    response = client.get('/dashboard/files/upload/')
    print(f"File upload page response: {response.status_code}")
    
    if response.status_code == 302:
        print("✅ File upload page redirects to login (expected)")
        print(f"Redirect URL: {response.url}")
    else:
        print(f"⚠️  Unexpected response: {response.status_code}")
    
    # Test the coordinate detection directly
    print("\nTesting coordinate detection...")
    csv_path = 'sample_files/sample.csv'
    if os.path.exists(csv_path):
        print(f"✅ Sample CSV file found: {csv_path}")
        
        # Test the file processing logic
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            print(f"✅ CSV loaded successfully with {len(df)} rows")
            print(f"Columns: {list(df.columns)}")
            
            # Test coordinate detection
            columns = df.columns.str.lower()
            lat_patterns = ['lat', 'latitude', 'y', 'y_coord', 'ycoord']
            lon_patterns = ['lon', 'long', 'longitude', 'lng', 'x', 'x_coord', 'xcoord']
            
            lat_col = None
            lon_col = None
            
            # First try exact matches
            for pattern in lat_patterns:
                if pattern in columns:
                    lat_col = df.columns[columns == pattern][0]
                    break
            
            for pattern in lon_patterns:
                if pattern in columns:
                    lon_col = df.columns[columns == pattern][0]
                    break
            
            print(f"Detected lat_col: {lat_col}")
            print(f"Detected lon_col: {lon_col}")
            
            if lat_col and lon_col:
                print("✅ Coordinate detection successful!")
                
                # Test a few coordinate values
                for i in range(min(3, len(df))):
                    lat = df.iloc[i][lat_col]
                    lon = df.iloc[i][lon_col]
                    print(f"Row {i+1}: lat={lat}, lon={lon}")
            else:
                print("❌ Coordinate detection failed!")
                
        except Exception as e:
            print(f"❌ Error processing CSV: {e}")
    else:
        print(f"❌ Sample CSV file not found: {csv_path}")

if __name__ == "__main__":
    test_csv_upload_simple() 