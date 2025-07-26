#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

import pandas as pd

def detect_coordinate_columns(df):
    """Detect latitude and longitude columns in CSV"""
    columns = df.columns.str.lower()
    
    # Common latitude column names
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
    
    # If not found, try partial matches
    if not lat_col:
        for pattern in lat_patterns:
            matches = [col for col in columns if pattern in col]
            if matches:
                lat_col = df.columns[columns == matches[0]][0]
                break
    
    if not lon_col:
        for pattern in lon_patterns:
            matches = [col for col in columns if pattern in col]
            if matches:
                lon_col = df.columns[columns == matches[0]][0]
                break
    
    # Debug logging
    print(f"Detected columns: {list(df.columns)}")
    print(f"Looking for lat/lon patterns: {lat_patterns}/{lon_patterns}")
    print(f"Found lat_col: {lat_col}, lon_col: {lon_col}")
    
    return lat_col, lon_col

def test_coordinate_detection():
    """Test coordinate detection with sample CSV"""
    print("Testing coordinate detection...")
    
    # Read the sample CSV
    csv_path = 'sample_files/sample.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found!")
        return
    
    df = pd.read_csv(csv_path)
    print(f"CSV columns: {list(df.columns)}")
    print(f"First few rows:")
    print(df.head())
    
    # Test coordinate detection
    lat_col, lon_col = detect_coordinate_columns(df)
    
    print(f"\nDetected lat_col: {lat_col}")
    print(f"Detected lon_col: {lon_col}")
    
    if lat_col and lon_col:
        print("✅ Coordinate detection successful!")
        
        # Test a few coordinates
        print("\nTesting coordinate values:")
        for i in range(min(3, len(df))):
            lat = df.iloc[i][lat_col]
            lon = df.iloc[i][lon_col]
            print(f"Row {i+1}: lat={lat}, lon={lon}")
    else:
        print("❌ Coordinate detection failed!")

if __name__ == "__main__":
    test_coordinate_detection() 