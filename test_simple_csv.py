#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

import pandas as pd

def test_csv_coordinates():
    """Test CSV coordinate detection"""
    print("Testing CSV coordinate detection...")
    
    csv_path = 'sample_files/sample.csv'
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    # Read CSV
    df = pd.read_csv(csv_path)
    print(f"✅ CSV loaded: {len(df)} rows, {len(df.columns)} columns")
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
    
    print(f"Found lat_col: {lat_col}")
    print(f"Found lon_col: {lon_col}")
    
    if lat_col and lon_col:
        print("✅ Coordinate detection successful!")
        
        # Test a few values
        for i in range(min(3, len(df))):
            lat = df.iloc[i][lat_col]
            lon = df.iloc[i][lon_col]
            print(f"Row {i+1}: lat={lat}, lon={lon}")
        
        return True
    else:
        print("❌ Coordinate detection failed!")
        return False

if __name__ == "__main__":
    test_csv_coordinates() 