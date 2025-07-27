import json
import zipfile
import tempfile
import os
from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import pandas as pd
import xml.etree.ElementTree as ET
from .models import UploadedParcel, KMLData, KMLFile, CSVData, ShapefileData
import uuid
import logging
import re

logger = logging.getLogger(__name__)

class GeospatialDashboardView(LoginRequiredMixin, View):
    """Main geospatial dashboard view"""
    
    def get(self, request):
        # Get filter parameters
        filters = self._get_filters(request)
        
        # Get parcels with filters (combine UploadedParcel and KMLData)
        parcels = self._get_filtered_parcels(request.user, filters)
        
        # Get statistics
        stats = self._get_statistics(request.user)
        
        # Get unique values for filter dropdowns
        filter_options = self._get_filter_options(request.user)
        
        context = {
            'parcels': parcels,
            'filters': filters,
            'stats': stats,
            'filter_options': filter_options,
        }
        
        return render(request, 'userdashboard/geospatial_dashboard.html', context)
    
    def _get_filters(self, request):
        """Extract filter parameters from request"""
        return {
            'name': request.GET.get('name', '').strip(),
            'kitta_no': request.GET.get('kitta_no', '').strip(),
            'sn_no': request.GET.get('sn_no', '').strip(),
            'district': request.GET.get('district', '').strip(),
            'municipality': request.GET.get('municipality', '').strip(),
            'ward': request.GET.get('ward', '').strip(),
            'location': request.GET.get('location', '').strip(),
            'file_type': request.GET.get('file_type', '').strip(),
        }
    
    def _get_filtered_parcels(self, user, filters):
        """Get parcels filtered by criteria - combine UploadedParcel and KMLData"""
        # Get UploadedParcel data
        uploaded_parcels = UploadedParcel.objects.filter(user=user)
        
        # Apply filters to UploadedParcel
        if filters['name']:
            uploaded_parcels = uploaded_parcels.filter(name__icontains=filters['name'])
        if filters['kitta_no']:
            uploaded_parcels = uploaded_parcels.filter(kitta_no__icontains=filters['kitta_no'])
        if filters['sn_no']:
            uploaded_parcels = uploaded_parcels.filter(sn_no__icontains=filters['sn_no'])
        if filters['district']:
            uploaded_parcels = uploaded_parcels.filter(district__icontains=filters['district'])
        if filters['municipality']:
            uploaded_parcels = uploaded_parcels.filter(municipality__icontains=filters['municipality'])
        if filters['ward']:
            uploaded_parcels = uploaded_parcels.filter(ward__icontains=filters['ward'])
        if filters['location']:
            uploaded_parcels = uploaded_parcels.filter(location__icontains=filters['location'])
        if filters['file_type']:
            uploaded_parcels = uploaded_parcels.filter(file_type=filters['file_type'])
        
        # Get KMLData from user's KML files
        user_kml_files = KMLFile.objects.filter(user=user)
        kml_data = KMLData.objects.filter(kml_file__in=user_kml_files)
        
        # Apply filters to KMLData
        if filters['name']:
            kml_data = kml_data.filter(placemark_name__icontains=filters['name'])
        if filters['kitta_no']:
            kml_data = kml_data.filter(kitta_number__icontains=filters['kitta_no'])
        if filters['district']:
            kml_data = kml_data.filter(administrative_area__icontains=filters['district'])
        if filters['municipality']:
            kml_data = kml_data.filter(locality__icontains=filters['municipality'])
        if filters['location']:
            kml_data = kml_data.filter(address__icontains=filters['location'])
        if filters['file_type'] and filters['file_type'] == 'KML':
            pass  # Keep KML data
        elif filters['file_type']:
            kml_data = kml_data.none()  # Exclude KML data if other file type selected
        
        # Convert KMLData to parcel-like format for display
        kml_parcels = []
        for kml_item in kml_data:
            # Only include KML items with valid geometry
            geometry = None
            if kml_item.coordinates:
                try:
                    geometry = json.loads(kml_item.coordinates)
                    # Validate geometry structure
                    if not (isinstance(geometry, dict) and 
                           geometry.get('type') and 
                           geometry.get('coordinates')):
                        geometry = None
                except (json.JSONDecodeError, TypeError):
                    geometry = None
            
            if geometry:  # Only add if we have valid geometry
                kml_parcels.append({
                    'id': f"kml_{kml_item.id}",
                    'name': kml_item.placemark_name or 'Unnamed Placemark',
                    'kitta_no': kml_item.kitta_number or '',
                    'sn_no': '',
                    'district': kml_item.administrative_area or '',
                    'municipality': kml_item.locality or '',
                    'ward': '',
                    'location': kml_item.address or '',
                    'file_type': 'KML',
                    'uploaded_at': kml_item.created_at,
                    'geometry': geometry,
                    'is_kml_data': True,
                    'kml_data_id': kml_item.id,
                })
        
        # Combine and sort results
        all_parcels = list(uploaded_parcels) + kml_parcels
        all_parcels.sort(key=lambda x: x.uploaded_at if hasattr(x, 'uploaded_at') else x['uploaded_at'], reverse=True)
        
        return all_parcels
    
    def _get_statistics(self, user):
        """Get dashboard statistics - include both UploadedParcel and KMLData"""
        uploaded_parcels = UploadedParcel.objects.filter(user=user)
        user_kml_files = KMLFile.objects.filter(user=user)
        kml_data = KMLData.objects.filter(kml_file__in=user_kml_files)
        
        # Get unique districts from both sources
        uploaded_districts = set(uploaded_parcels.values_list('district', flat=True).exclude(district=''))
        kml_districts = set(kml_data.values_list('administrative_area', flat=True).exclude(administrative_area=''))
        all_districts = uploaded_districts.union(kml_districts)
        
        # Get unique municipalities from both sources
        uploaded_municipalities = set(uploaded_parcels.values_list('municipality', flat=True).exclude(municipality=''))
        kml_municipalities = set(kml_data.values_list('locality', flat=True).exclude(locality=''))
        all_municipalities = uploaded_municipalities.union(kml_municipalities)
        
        # Get unique wards from uploaded parcels
        uploaded_wards = set(uploaded_parcels.values_list('ward', flat=True).exclude(ward=''))
        
        return {
            'total_parcels': uploaded_parcels.count() + kml_data.count(),
            'total_districts': len(all_districts),
            'total_municipalities': len(all_municipalities),
            'total_wards': len(uploaded_wards),
            'by_file_type': {
                'KML': uploaded_parcels.filter(file_type='KML').count() + kml_data.count(),
                'CSV': uploaded_parcels.filter(file_type='CSV').count(),
                'SHP': uploaded_parcels.filter(file_type='SHP').count(),
            }
        }
    
    def _get_filter_options(self, user):
        """Get unique values for filter dropdowns - include both data sources"""
        uploaded_parcels = UploadedParcel.objects.filter(user=user)
        user_kml_files = KMLFile.objects.filter(user=user)
        kml_data = KMLData.objects.filter(kml_file__in=user_kml_files)
        
        # Combine districts
        uploaded_districts = list(uploaded_parcels.values_list('district', flat=True).distinct().exclude(district=''))
        kml_districts = list(kml_data.values_list('administrative_area', flat=True).distinct().exclude(administrative_area=''))
        all_districts = list(set(uploaded_districts + kml_districts))
        
        # Combine municipalities
        uploaded_municipalities = list(uploaded_parcels.values_list('municipality', flat=True).distinct().exclude(municipality=''))
        kml_municipalities = list(kml_data.values_list('locality', flat=True).distinct().exclude(locality=''))
        all_municipalities = list(set(uploaded_municipalities + kml_municipalities))
        
        # Wards (only from uploaded parcels)
        uploaded_wards = list(uploaded_parcels.values_list('ward', flat=True).distinct().exclude(ward=''))
        
        return {
            'districts': all_districts,
            'municipalities': all_municipalities,
            'wards': uploaded_wards,
            'file_types': ['KML', 'CSV', 'SHP'],
        }


class UploadParcelView(LoginRequiredMixin, View):
    """Handle file uploads and parsing"""
    
    def post(self, request):
        try:
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({'error': 'No file uploaded'}, status=400)
            
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'kml':
                parcels = self._parse_kml_file(uploaded_file, request.user)
            elif file_extension == 'csv':
                parcels = self._parse_csv_file(uploaded_file, request.user)
            elif file_extension == 'zip':
                parcels = self._parse_shapefile(uploaded_file, request.user)
            else:
                return JsonResponse({'error': 'Unsupported file type'}, status=400)
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully uploaded {len(parcels)} parcels',
                'parcels_count': len(parcels)
            })
            
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            return JsonResponse({'error': f'Upload failed: {str(e)}'}, status=500)
    
    def _parse_kml_file(self, file, user):
        """Parse KML file and extract parcels"""
        parcels = []
        
        try:
            # Reset file pointer to beginning
            file.seek(0)
            
            tree = ET.parse(file)
            root = tree.getroot()
            
            # Define KML namespace
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}
            
            # Find all Placemarks
            placemarks = root.findall('.//kml:Placemark', ns)
            
            if not placemarks:
                # Try alternative namespace or no namespace
                placemarks = root.findall('.//Placemark')
                if not placemarks:
                    raise Exception("No Placemark elements found in KML file")
            
            logger.info(f"Found {len(placemarks)} placemarks in KML file")
            
            for i, placemark in enumerate(placemarks):
                try:
                    # Extract name
                    name_elem = placemark.find('kml:name', ns)
                    if name_elem is None:
                        name_elem = placemark.find('name')  # Try without namespace
                    name = name_elem.text if name_elem is not None else f'Placemark {i+1}'
                
                    # Extract description for additional attributes
                    desc_elem = placemark.find('kml:description', ns)
                    if desc_elem is None:
                        desc_elem = placemark.find('description')  # Try without namespace
                    description = desc_elem.text if desc_elem is not None else ''
                    
                    # Extract ExtendedData (structured data)
                    extended_data = self._extract_extended_data(placemark, ns)
                
                    # Extract geometry
                    geometry = self._extract_kml_geometry(placemark, ns)
                
                    if geometry:
                        # Parse description for attributes
                        attrs = self._parse_kml_description(description)
                        
                        # Merge with ExtendedData (ExtendedData takes precedence)
                        attrs.update(extended_data)
                        
                        logger.info(f"Creating parcel: {name} with attributes: {attrs}")
                    
                        parcel = UploadedParcel.objects.create(
                            user=user,
                            name=name,
                            kitta_no=attrs.get('kitta_no', ''),
                            sn_no=attrs.get('sn_no', ''),
                            district=attrs.get('district', ''),
                            municipality=attrs.get('municipality', ''),
                            ward=attrs.get('ward', ''),
                            location=attrs.get('location', ''),
                            geometry=geometry,
                            coordinates=json.dumps(geometry.get('coordinates', [])),
                            file_type='KML',
                            original_file=file
                        )
                        parcels.append(parcel)
                        logger.info(f"Successfully created parcel: {parcel.id}")
                    else:
                        logger.warning(f"No valid geometry found for placemark: {name}")
                        
                except Exception as e:
                    logger.error(f"Error processing placemark {i+1}: {str(e)}")
                    continue
            
            if not parcels:
                raise Exception("No valid parcels could be extracted from KML file")
            
            logger.info(f"Successfully parsed {len(parcels)} parcels from KML file")
        
        except Exception as e:
            logger.error(f"KML parsing error: {str(e)}")
            raise Exception(f"Failed to parse KML file: {str(e)}")
        
        return parcels
    
    def _extract_extended_data(self, placemark, ns):
        """Extract data from KML ExtendedData elements"""
        attrs = {}
        
        try:
            extended_data = placemark.find('kml:ExtendedData', ns)
            if extended_data is None:
                extended_data = placemark.find('ExtendedData')  # Try without namespace
            
            if extended_data is not None:
                # Look for SimpleData elements
                simple_data_elements = extended_data.findall('.//kml:SimpleData', ns)
                if not simple_data_elements:
                    simple_data_elements = extended_data.findall('.//SimpleData')  # Try without namespace
                
                for simple_data in simple_data_elements:
                    try:
                        name = simple_data.get('name', '').lower()
                        value = simple_data.text if simple_data.text else ''
                        
                        # Map to our standard fields
                        if name in ['kitta', 'kitta_no', 'kitta_number', 'kitta no']:
                            attrs['kitta_no'] = value
                        elif name in ['sn', 'sn_no', 'serial_number', 'serial no']:
                            attrs['sn_no'] = value
                        elif name in ['district']:
                            attrs['district'] = value
                        elif name in ['municipality', 'municipal']:
                            attrs['municipality'] = value
                        elif name in ['ward']:
                            attrs['ward'] = value
                        elif name in ['location', 'address']:
                            attrs['location'] = value
                    except Exception as e:
                        logger.warning(f"Error processing SimpleData element: {e}")
                
                # Also look for Data elements
                data_elements = extended_data.findall('.//kml:Data', ns)
                if not data_elements:
                    data_elements = extended_data.findall('.//Data')  # Try without namespace
                
                for data_elem in data_elements:
                    try:
                        name = data_elem.get('name', '').lower()
                        value_elem = data_elem.find('kml:value', ns)
                        if value_elem is None:
                            value_elem = data_elem.find('value')  # Try without namespace
                        value = value_elem.text if value_elem is not None and value_elem.text else ''
                        
                        # Map to our standard fields
                        if name in ['kitta', 'kitta_no', 'kitta_number', 'kitta no']:
                            attrs['kitta_no'] = value
                        elif name in ['sn', 'sn_no', 'serial_number', 'serial no']:
                            attrs['sn_no'] = value
                        elif name in ['district']:
                            attrs['district'] = value
                        elif name in ['municipality', 'municipal']:
                            attrs['municipality'] = value
                        elif name in ['ward']:
                            attrs['ward'] = value
                        elif name in ['location', 'address']:
                            attrs['location'] = value
                    except Exception as e:
                        logger.warning(f"Error processing Data element: {e}")
        
        except Exception as e:
            logger.warning(f"Error extracting ExtendedData: {e}")
        
        return attrs
    
    def _extract_kml_geometry(self, placemark, ns):
        """Extract geometry from KML Placemark"""
        try:
            # Check for Point
            point = placemark.find('.//kml:Point', ns)
            if point is None:
                point = placemark.find('.//Point')  # Try without namespace
            
            if point is not None:
                coords_elem = point.find('kml:coordinates', ns)
                if coords_elem is None:
                    coords_elem = point.find('coordinates')  # Try without namespace
                
                if coords_elem is not None and coords_elem.text:
                    coords_text = coords_elem.text.strip()
                    # Split by comma and take only first 2 values (lon, lat)
                    # KML coordinates can be: lon,lat,altitude
                    coord_values = coords_text.split(',')
                    if len(coord_values) >= 2:
                        try:
                            lon, lat = float(coord_values[0]), float(coord_values[1])
                            # Validate coordinate ranges
                            if -180 <= lon <= 180 and -90 <= lat <= 90:
                                return {
                                    'type': 'Point',
                                    'coordinates': [lon, lat]
                                }
                            else:
                                logger.warning(f"Invalid coordinates: lon={lon}, lat={lat}")
                        except ValueError as e:
                            logger.warning(f"Could not parse coordinates '{coords_text}': {e}")
            
            # Check for Polygon
            polygon = placemark.find('.//kml:Polygon', ns)
            if polygon is None:
                polygon = placemark.find('.//Polygon')  # Try without namespace
            
            if polygon is not None:
                outer_boundary = polygon.find('.//kml:outerBoundaryIs//kml:coordinates', ns)
                if outer_boundary is None:
                    outer_boundary = polygon.find('.//outerBoundaryIs//coordinates')  # Try without namespace
                
                if outer_boundary is not None and outer_boundary.text:
                    try:
                        coords_text = outer_boundary.text.strip()
                        coords_list = []
                        for coord_pair in coords_text.split():
                            if ',' in coord_pair:
                                # Split by comma and take only first 2 values (lon, lat)
                                # KML coordinates can be: lon,lat,altitude
                                coord_values = coord_pair.split(',')
                                if len(coord_values) >= 2:
                                    try:
                                        lon, lat = float(coord_values[0]), float(coord_values[1])
                                        if -180 <= lon <= 180 and -90 <= lat <= 90:
                                            coords_list.append([lon, lat])
                                    except ValueError as e:
                                        logger.warning(f"Invalid coordinate values in '{coord_pair}': {e}")
                                        continue
                        
                        if len(coords_list) >= 3:
                            return {
                                'type': 'Polygon',
                                'coordinates': [coords_list]
                            }
                        else:
                            logger.warning(f"Polygon needs at least 3 points, got {len(coords_list)}")
                    except Exception as e:
                        logger.warning(f"Could not parse polygon coordinates: {e}")
            
            # Check for LineString
            linestring = placemark.find('.//kml:LineString', ns)
            if linestring is None:
                linestring = placemark.find('.//LineString')  # Try without namespace
            
            if linestring is not None:
                coords_elem = linestring.find('kml:coordinates', ns)
                if coords_elem is None:
                    coords_elem = linestring.find('coordinates')  # Try without namespace
                
                if coords_elem is not None and coords_elem.text:
                    try:
                        coords_text = coords_elem.text.strip()
                        coords_list = []
                        for coord_pair in coords_text.split():
                            if ',' in coord_pair:
                                # Split by comma and take only first 2 values (lon, lat)
                                # KML coordinates can be: lon,lat,altitude
                                coord_values = coord_pair.split(',')
                                if len(coord_values) >= 2:
                                    try:
                                        lon, lat = float(coord_values[0]), float(coord_values[1])
                                        if -180 <= lon <= 180 and -90 <= lat <= 90:
                                            coords_list.append([lon, lat])
                                    except ValueError as e:
                                        logger.warning(f"Invalid coordinate values in '{coord_pair}': {e}")
                                        continue
                        
                        if len(coords_list) >= 2:
                            return {
                                'type': 'LineString',
                                'coordinates': coords_list
                            }
                        else:
                            logger.warning(f"LineString needs at least 2 points, got {len(coords_list)}")
                    except Exception as e:
                        logger.warning(f"Could not parse linestring coordinates: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting geometry: {e}")
            return None
    
    def _parse_kml_description(self, description):
        """Parse KML description for attributes"""
        attrs = {}
        if description:
            # Simple parsing - look for key-value pairs
            lines = description.split('\n')
            for line in lines:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    # Map various key names to our standard fields
                    if key in ['kitta', 'kitta_no', 'kitta number', 'kitta no']:
                        attrs['kitta_no'] = value
                    elif key in ['sn', 'sn_no', 'serial number', 'serial no']:
                        attrs['sn_no'] = value
                    elif key in ['district']:
                        attrs['district'] = value
                    elif key in ['municipality', 'municipal']:
                        attrs['municipality'] = value
                    elif key in ['ward']:
                        attrs['ward'] = value
                    elif key in ['location', 'address']:
                        attrs['location'] = value
                    
                    # Also try to extract from HTML-like descriptions
                    elif '<' in line and '>' in line:
                        # Handle HTML-like descriptions
                        if 'kitta' in line.lower():
                            # Extract kitta number from HTML
                            kitta_match = re.search(r'kitta[^>]*>([^<]+)', line, re.IGNORECASE)
                            if kitta_match:
                                attrs['kitta_no'] = kitta_match.group(1).strip()
                        elif 'district' in line.lower():
                            district_match = re.search(r'district[^>]*>([^<]+)', line, re.IGNORECASE)
                            if district_match:
                                attrs['district'] = district_match.group(1).strip()
        
        return attrs
    
    def _parse_csv_file(self, file, user):
        """Parse CSV file with coordinates or WKT geometry"""
        parcels = []
        
        try:
            df = pd.read_csv(file)
            
            # Check for coordinate columns with more variations
            lat_col = None
            lon_col = None
            wkt_col = None
            
            for col in df.columns:
                col_lower = col.lower().strip()
                if any(term in col_lower for term in ['lat', 'latitude', 'y']):
                    lat_col = col
                elif any(term in col_lower for term in ['lon', 'longitude', 'lng', 'x']):
                    lon_col = col
                elif any(term in col_lower for term in ['wkt', 'geometry', 'geom']):
                    wkt_col = col
            
            # If no coordinate columns found, try to infer from first few rows
            if not lat_col and not lon_col and not wkt_col:
                # Look for numeric columns that might be coordinates
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) >= 2:
                    # Assume first two numeric columns might be coordinates
                    potential_lon = numeric_cols[0]
                    potential_lat = numeric_cols[1]
                    
                    # Check if values are in reasonable coordinate ranges
                    lon_values = df[potential_lon].dropna()
                    lat_values = df[potential_lat].dropna()
                    
                    if (len(lon_values) > 0 and len(lat_values) > 0 and
                        lon_values.min() >= -180 and lon_values.max() <= 180 and
                        lat_values.min() >= -90 and lat_values.max() <= 90):
                        lon_col = potential_lon
                        lat_col = potential_lat
            
            for index, row in df.iterrows():
                geometry = None
                
                # Try WKT first
                if wkt_col and pd.notna(row[wkt_col]):
                    try:
                        geometry = self._parse_wkt(str(row[wkt_col]))
                    except:
                        pass
                
                # Try coordinates
                if geometry is None and lat_col and lon_col:
                    if pd.notna(row[lat_col]) and pd.notna(row[lon_col]):
                        try:
                            lat = float(row[lat_col])
                            lon = float(row[lon_col])
                            # Validate coordinate ranges
                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                geometry = {
                                    'type': 'Point',
                                    'coordinates': [lon, lat]
                                }
                        except:
                            pass
                
                if geometry:
                    # Extract attributes from row
                    parcel = UploadedParcel.objects.create(
                        user=user,
                        name=str(row.get('name', row.get('Name', f'CSV Record {index + 1}'))),
                        kitta_no=str(row.get('kitta_no', row.get('kitta', row.get('Kitta No', '')))),
                        sn_no=str(row.get('sn_no', row.get('sn', row.get('SN No', '')))),
                        district=str(row.get('district', row.get('District', ''))),
                        municipality=str(row.get('municipality', row.get('Municipality', ''))),
                        ward=str(row.get('ward', row.get('Ward', ''))),
                        location=str(row.get('location', row.get('Location', ''))),
                        geometry=geometry,
                        coordinates=json.dumps(geometry.get('coordinates', [])),
                        file_type='CSV',
                        original_file=file
                    )
                    parcels.append(parcel)
        
        except Exception as e:
            logger.error(f"CSV parsing error: {str(e)}")
            raise Exception(f"Failed to parse CSV file: {str(e)}")
        
        return parcels
    
    def _parse_wkt(self, wkt_string):
        """Parse WKT string to GeoJSON"""
        wkt = wkt_string.strip().upper()
        
        if wkt.startswith('POINT'):
            # Parse POINT (lon lat)
            coords_str = wkt.replace('POINT(', '').replace(')', '')
            coords = [float(x) for x in coords_str.split()]
            return {
                'type': 'Point',
                'coordinates': coords
            }
        elif wkt.startswith('POLYGON'):
            # Parse POLYGON ((lon1 lat1, lon2 lat2, ...))
            coords_str = wkt.replace('POLYGON((', '').replace('))', '')
            rings = coords_str.split('),(')
            coordinates = []
            for ring in rings:
                ring_coords = []
                for coord_pair in ring.split(','):
                    coords = [float(x) for x in coord_pair.strip().split()]
                    ring_coords.append(coords)
                coordinates.append(ring_coords)
            return {
                'type': 'Polygon',
                'coordinates': coordinates
            }
        elif wkt.startswith('LINESTRING'):
            # Parse LINESTRING (lon1 lat1, lon2 lat2, ...)
            coords_str = wkt.replace('LINESTRING(', '').replace(')', '')
            coordinates = []
            for coord_pair in coords_str.split(','):
                coords = [float(x) for x in coord_pair.strip().split()]
                coordinates.append(coords)
            return {
                'type': 'LineString',
                'coordinates': coordinates
            }
        
        return None
    
    def _parse_shapefile(self, file, user):
        """Parse zipped shapefile (simplified version)"""
        parcels = []
        
        try:
            # Check if file is a zip file
            if not file.name.lower().endswith('.zip'):
                raise Exception("Shapefile must be uploaded as a ZIP file containing .shp, .shx, .dbf files")
            
            # For now, return an error message since full shapefile parsing requires GDAL/geopandas
            # In a production environment, you would install and use geopandas to read shapefiles
            raise Exception(
                "Shapefile parsing is not fully implemented yet. "
                "This feature requires GDAL and geopandas libraries. "
                "Please use KML or CSV files for now, or contact the administrator to enable shapefile support."
            )
            
            # Future implementation would look like this:
            # import geopandas as gpd
            # import zipfile
            # import tempfile
            # 
            # with tempfile.TemporaryDirectory() as temp_dir:
            #     with zipfile.ZipFile(file, 'r') as zip_ref:
            #         zip_ref.extractall(temp_dir)
            #     
            #     # Find the .shp file
            #     shp_files = [f for f in os.listdir(temp_dir) if f.endswith('.shp')]
            #     if not shp_files:
            #         raise Exception("No .shp file found in the ZIP archive")
            #     
            #     shp_path = os.path.join(temp_dir, shp_files[0])
            #     gdf = gpd.read_file(shp_path)
            #     
            #     for index, row in gdf.iterrows():
            #         geometry = row.geometry.__geo_interface__
            #         parcel = UploadedParcel.objects.create(
            #             user=user,
            #             name=str(row.get('name', f'Feature {index + 1}')),
            #             kitta_no=str(row.get('kitta_no', '')),
            #             sn_no=str(row.get('sn_no', '')),
            #             district=str(row.get('district', '')),
            #             municipality=str(row.get('municipality', '')),
            #             ward=str(row.get('ward', '')),
            #             location=str(row.get('location', '')),
            #             geometry=geometry,
            #             coordinates=json.dumps(geometry.get('coordinates', [])),
            #             file_type='SHP',
            #             original_file=file
            #         )
            #         parcels.append(parcel)
        
        except Exception as e:
            logger.error(f"Shapefile parsing error: {str(e)}")
            raise Exception(f"Failed to parse shapefile: {str(e)}")
        
        return parcels


class GeoJSONAPIView(LoginRequiredMixin, View):
    """API endpoint to return GeoJSON data for map display"""
    
    def get(self, request):
        try:
            user = request.user
            
            # Get filter parameters
            filters = self._get_filters(request)
            
            # Get parcels with filters (combine UploadedParcel and KMLData)
            parcels = self._get_filtered_parcels(user, filters)
            
            # Convert to GeoJSON format
            features = []
            
            for parcel in parcels:
                # Handle both UploadedParcel objects and KML data dictionaries
                if hasattr(parcel, 'get_geojson'):
                    # UploadedParcel object
                    geojson = parcel.get_geojson()
                    if geojson and geojson.get('geometry'):
                        features.append(geojson)
                elif isinstance(parcel, dict) and parcel.get('geometry'):
                    # KML data dictionary - only add if geometry is valid
                    geometry = parcel['geometry']
                    if geometry and geometry.get('type') and geometry.get('coordinates'):
                        feature = {
                            'type': 'Feature',
                            'geometry': geometry,
                            'properties': {
                                'id': parcel['id'],
                                'name': parcel['name'],
                                'kitta_no': parcel['kitta_no'],
                                'sn_no': parcel['sn_no'],
                                'district': parcel['district'],
                                'municipality': parcel['municipality'],
                                'ward': parcel['ward'],
                                'location': parcel['location'],
                                'file_type': parcel['file_type'],
                                'uploaded_at': parcel['uploaded_at'].isoformat() if hasattr(parcel['uploaded_at'], 'isoformat') else str(parcel['uploaded_at']),
                            }
                        }
                        features.append(feature)
            
            geojson_data = {
                'type': 'FeatureCollection',
                'features': features
            }
            
            # Log the GeoJSON structure for debugging
            logger.info(f"Generated GeoJSON with {len(features)} features")
            if features:
                logger.info(f"First feature: {features[0]}")
            
            return JsonResponse(geojson_data)
            
        except Exception as e:
            logger.error(f"GeoJSON API error: {str(e)}")
            return JsonResponse({'error': f'Failed to generate GeoJSON: {str(e)}'}, status=500)
    
    def _get_filters(self, request):
        """Extract filter parameters from request"""
        return {
                'name': request.GET.get('name', '').strip(),
                'kitta_no': request.GET.get('kitta_no', '').strip(),
                'sn_no': request.GET.get('sn_no', '').strip(),
                'district': request.GET.get('district', '').strip(),
                'municipality': request.GET.get('municipality', '').strip(),
                'ward': request.GET.get('ward', '').strip(),
                'location': request.GET.get('location', '').strip(),
                'file_type': request.GET.get('file_type', '').strip(),
            }
            
    def _get_filtered_parcels(self, user, filters):
        """Get parcels filtered by criteria - combine UploadedParcel and KMLData"""
        # Get UploadedParcel data
        uploaded_parcels = UploadedParcel.objects.filter(user=user)
        
        # Apply filters to UploadedParcel
        if filters['name']:
            uploaded_parcels = uploaded_parcels.filter(name__icontains=filters['name'])
        if filters['kitta_no']:
            uploaded_parcels = uploaded_parcels.filter(kitta_no__icontains=filters['kitta_no'])
        if filters['sn_no']:
            uploaded_parcels = uploaded_parcels.filter(sn_no__icontains=filters['sn_no'])
        if filters['district']:
            uploaded_parcels = uploaded_parcels.filter(district__icontains=filters['district'])
        if filters['municipality']:
            uploaded_parcels = uploaded_parcels.filter(municipality__icontains=filters['municipality'])
        if filters['ward']:
            uploaded_parcels = uploaded_parcels.filter(ward__icontains=filters['ward'])
        if filters['location']:
            uploaded_parcels = uploaded_parcels.filter(location__icontains=filters['location'])
        if filters['file_type']:
            uploaded_parcels = uploaded_parcels.filter(file_type=filters['file_type'])
        
        # Get KMLData from user's KML files
        user_kml_files = KMLFile.objects.filter(user=user)
        kml_data = KMLData.objects.filter(kml_file__in=user_kml_files)
        
        # Apply filters to KMLData
        if filters['name']:
            kml_data = kml_data.filter(placemark_name__icontains=filters['name'])
        if filters['kitta_no']:
            kml_data = kml_data.filter(kitta_number__icontains=filters['kitta_no'])
        if filters['district']:
            kml_data = kml_data.filter(administrative_area__icontains=filters['district'])
        if filters['municipality']:
            kml_data = kml_data.filter(locality__icontains=filters['municipality'])
        if filters['location']:
            kml_data = kml_data.filter(address__icontains=filters['location'])
        if filters['file_type'] and filters['file_type'] == 'KML':
            pass  # Keep KML data
        elif filters['file_type']:
            kml_data = kml_data.none()  # Exclude KML data if other file type selected
        
        # Convert KMLData to parcel-like format for display
        kml_parcels = []
        for kml_item in kml_data:
            # Only include KML items with valid geometry
            geometry = None
            if kml_item.coordinates:
                try:
                    geometry = json.loads(kml_item.coordinates)
                    # Validate geometry structure
                    if not (isinstance(geometry, dict) and 
                           geometry.get('type') and 
                           geometry.get('coordinates')):
                        geometry = None
                except (json.JSONDecodeError, TypeError):
                    geometry = None
            
            if geometry:  # Only add if we have valid geometry
                kml_parcels.append({
                    'id': f"kml_{kml_item.id}",
                    'name': kml_item.placemark_name or 'Unnamed Placemark',
                    'kitta_no': kml_item.kitta_number or '',
                    'sn_no': '',
                    'district': kml_item.administrative_area or '',
                    'municipality': kml_item.locality or '',
                    'ward': '',
                    'location': kml_item.address or '',
                    'file_type': 'KML',
                    'uploaded_at': kml_item.created_at,
                    'geometry': geometry,
                    'is_kml_data': True,
                    'kml_data_id': kml_item.id,
                })
        
        # Combine and sort results
        all_parcels = list(uploaded_parcels) + kml_parcels
        all_parcels.sort(key=lambda x: x.uploaded_at if hasattr(x, 'uploaded_at') else x['uploaded_at'], reverse=True)
        
        return all_parcels


class ExportPDFView(LoginRequiredMixin, View):
    """Export filtered data to PDF"""
    
    def get(self, request):
        try:
            # Get filter parameters
            filters = {
                'name': request.GET.get('name', '').strip(),
                'kitta_no': request.GET.get('kitta_no', '').strip(),
                'sn_no': request.GET.get('sn_no', '').strip(),
                'district': request.GET.get('district', '').strip(),
                'municipality': request.GET.get('municipality', '').strip(),
                'ward': request.GET.get('ward', '').strip(),
                'location': request.GET.get('location', '').strip(),
                'file_type': request.GET.get('file_type', '').strip(),
            }
            
            # Get filtered parcels
            queryset = UploadedParcel.objects.filter(user=request.user)
            
            if filters['name']:
                queryset = queryset.filter(name__icontains=filters['name'])
            if filters['kitta_no']:
                queryset = queryset.filter(kitta_no__icontains=filters['kitta_no'])
            if filters['sn_no']:
                queryset = queryset.filter(sn_no__icontains=filters['sn_no'])
            if filters['district']:
                queryset = queryset.filter(district__icontains=filters['district'])
            if filters['municipality']:
                queryset = queryset.filter(municipality__icontains=filters['municipality'])
            if filters['ward']:
                queryset = queryset.filter(ward__icontains=filters['ward'])
            if filters['location']:
                queryset = queryset.filter(location__icontains=filters['location'])
            if filters['file_type']:
                queryset = queryset.filter(file_type=filters['file_type'])
            
            parcels = list(queryset)
            
            # Generate description
            description = self._generate_description(parcels, filters)
            
            # Render PDF template
            context = {
                'parcels': parcels,
                'filters': filters,
                'description': description,
                'generated_at': timezone.now(),
            }
            
            html_content = render_to_string('userdashboard/pdf_report.html', context)
            
            # For now, return HTML (you can integrate WeasyPrint here)
            response = HttpResponse(html_content, content_type='text/html')
            response['Content-Disposition'] = 'attachment; filename="geospatial_report.html"'
            return response
            
        except Exception as e:
            logger.error(f"PDF export error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def _generate_description(self, parcels, filters):
        """Generate description for the report"""
        total_parcels = len(parcels)
        
        if total_parcels == 0:
            return "No parcels found matching the specified criteria."
        
        # Count unique districts, municipalities, wards
        districts = set(p.district for p in parcels if p.district)
        municipalities = set(p.municipality for p in parcels if p.municipality)
        wards = set(p.ward for p in parcels if p.ward)
        
        description = f"This report displays {total_parcels} parcels"
        
        if districts:
            description += f" across {len(districts)} district(s): {', '.join(districts)}"
        
        if municipalities:
            description += f" in {len(municipalities)} municipality(ies)"
        
        if wards:
            description += f" covering {len(wards)} unique ward(s)"
        
        description += "."
        
        # Add filter information
        applied_filters = [f"{k}: {v}" for k, v in filters.items() if v]
        if applied_filters:
            description += f" Filters applied: {', '.join(applied_filters)}."
        
        return description 