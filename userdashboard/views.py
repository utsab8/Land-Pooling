from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import FileUpload, KMLData, UploadedParcel, KMLFile, DownloadLog, ContactFormSubmission
import json
import re
import os
import csv
import xml.etree.ElementTree as ET
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Create your views here.

class UserDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            # Count total files
            total_files = FileUpload.objects.filter(user=request.user).count()
            
            # Count total surveys (KML files)
            total_surveys = KMLData.objects.filter(kml_file__user=request.user).count()
            
            # Count recent uploads (last 7 days)
            from django.utils import timezone
            from datetime import timedelta
            recent_date = timezone.now() - timedelta(days=7)
            recent_uploads = FileUpload.objects.filter(
                user=request.user, 
                created_at__gte=recent_date
            ).count()
            
            # Count total parcels
            total_parcels = UploadedParcel.objects.filter(user=request.user).count()
            
            # Get recent activities (last 5 activities)
            recent_activities = []
            
            # Add file upload activities
            recent_files = FileUpload.objects.filter(user=request.user).order_by('-created_at')[:3]
            for file in recent_files:
                recent_activities.append({
                    'type': 'upload',
                    'description': f'Uploaded {file.original_filename}',
                    'timestamp': file.created_at
                })
            
            # Add KML activities
            recent_kml = KMLData.objects.filter(kml_file__user=request.user).order_by('-created_at')[:2]
            for kml in recent_kml:
                recent_activities.append({
                    'type': 'survey',
                    'description': f'Created survey: {kml.placemark_name or kml.kitta_number or "KML Data"}',
                    'timestamp': kml.created_at
                })
            
            # Sort activities by timestamp
            recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
            recent_activities = recent_activities[:5]
            
            context = {
                'total_files': total_files,
                'total_surveys': total_surveys,
                'recent_uploads': recent_uploads,
                'total_parcels': total_parcels,
                'recent_activities': recent_activities,
            }
            
            return render(request, 'userdashboard/dashboard.html', context)
            
        except Exception as e:
            print(f"Dashboard error: {e}")
            # Return a simple context if there's an error
            context = {
                'total_files': 0,
                'total_surveys': 0,
                'recent_uploads': 0,
                'total_parcels': 0,
                'recent_activities': [],
            }
            return render(request, 'userdashboard/dashboard.html', context)

class UploadsView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'userdashboard/uploads.html')
    
    def post(self, request):
        """Handle file uploads and redirect to preview"""
        user = request.user
        
        # Handle KML upload
        if 'kml_file' in request.FILES:
            kml_file = request.FILES['kml_file']
            if self._validate_kml_file(kml_file):
                # Save file temporarily and store info in session
                file_path = self._save_temp_file(kml_file, 'kml')
                preview_data = self._parse_kml_file(kml_file)
                
                request.session['preview_data'] = {
                    'file_type': 'kml',
                    'file_name': kml_file.name,
                    'file_size': kml_file.size,
                    'file_path': file_path,
                    'preview_data': preview_data
                }
                return redirect('file_preview')
            else:
                messages.error(request, 'Invalid KML file. Please upload a valid KML file.')
        
        # Handle CSV upload
        elif 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            if self._validate_csv_file(csv_file):
                file_path = self._save_temp_file(csv_file, 'csv')
                preview_data = self._parse_csv_file(csv_file)
                
                request.session['preview_data'] = {
                    'file_type': 'csv',
                    'file_name': csv_file.name,
                    'file_size': csv_file.size,
                    'file_path': file_path,
                    'preview_data': preview_data
                }
                return redirect('file_preview')
            else:
                messages.error(request, 'Invalid CSV file. Please upload a valid CSV file.')
        
        # Handle Shapefile upload
        elif 'shp_file' in request.FILES:
            shp_file = request.FILES['shp_file']
            if self._validate_shapefile(shp_file):
                file_path = self._save_temp_file(shp_file, 'shp')
                preview_data = self._parse_shapefile(shp_file)
                
                request.session['preview_data'] = {
                    'file_type': 'shp',
                    'file_name': shp_file.name,
                    'file_size': shp_file.size,
                    'file_path': file_path,
                    'preview_data': preview_data
                }
                return redirect('file_preview')
            else:
                messages.error(request, 'Invalid Shapefile. Please upload a valid .shp or .zip file.')
        
        return redirect('uploads')
    
    def _validate_kml_file(self, file):
        """Validate KML file"""
        if not file.name.lower().endswith('.kml'):
            return False
        if file.size > 50 * 1024 * 1024:  # 50MB limit
            return False
        return True
    
    def _validate_csv_file(self, file):
        """Validate CSV file"""
        if not file.name.lower().endswith('.csv'):
            return False
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            return False
        return True
    
    def _validate_shapefile(self, file):
        """Validate Shapefile"""
        valid_extensions = ['.shp', '.zip']
        if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
            return False
        if file.size > 100 * 1024 * 1024:  # 100MB limit
            return False
        return True
    
    def _save_temp_file(self, file, file_type):
        """Save uploaded file temporarily"""
        temp_dir = f'temp_uploads/{file_type}'
        file_path = default_storage.save(f'{temp_dir}/{file.name}', ContentFile(file.read()))
        return file_path
    
    def _parse_kml_file(self, file):
        """Parse KML file and extract preview data"""
        try:
            file.seek(0)  # Reset file pointer
            content = file.read().decode('utf-8')
            root = ET.fromstring(content)
            
            # Extract basic KML information
            placemarks = root.findall('.//{http://www.opengis.net/kml/2.2}Placemark')
            coordinates = []
            
            for placemark in placemarks[:10]:  # Limit to first 10 placemarks
                name_elem = placemark.find('.//{http://www.opengis.net/kml/2.2}name')
                name = name_elem.text if name_elem is not None else 'Unnamed Placemark'
                
                coords_elem = placemark.find('.//{http://www.opengis.net/kml/2.2}coordinates')
                if coords_elem is not None:
                    coords_text = coords_elem.text.strip()
                    coords_list = coords_text.split()
                    if coords_list:
                        # Take first coordinate pair
                        first_coord = coords_list[0].split(',')
                        if len(first_coord) >= 2:
                            coordinates.append({
                                'name': name,
                                'longitude': float(first_coord[0]),
                                'latitude': float(first_coord[1])
                            })
            
            return {
                'total_placemarks': len(placemarks),
                'preview_coordinates': coordinates[:10],
                'file_content_preview': content[:1000] + '...' if len(content) > 1000 else content
            }
        except Exception as e:
            return {
                'error': f'Error parsing KML file: {str(e)}',
                'total_placemarks': 0,
                'preview_coordinates': []
            }
    
    def _parse_csv_file(self, file):
        """Parse CSV file and extract preview data"""
        try:
            file.seek(0)  # Reset file pointer
            content = file.read().decode('utf-8')
            lines = content.split('\n')
            
            # Parse CSV
            csv_reader = csv.reader(lines)
            headers = next(csv_reader, [])
            rows = list(csv_reader)
            
            # Extract preview data
            preview_rows = rows[:10]  # First 10 rows
            
            # Try to identify coordinate columns
            coord_columns = []
            for i, header in enumerate(headers):
                header_lower = header.lower()
                if any(keyword in header_lower for keyword in ['lat', 'lon', 'long', 'x', 'y', 'coord']):
                    coord_columns.append(i)
            
            return {
                'headers': headers,
                'total_rows': len(rows),
                'preview_rows': preview_rows,
                'coordinate_columns': coord_columns,
                'file_content_preview': content[:1000] + '...' if len(content) > 1000 else content
            }
        except Exception as e:
            return {
                'error': f'Error parsing CSV file: {str(e)}',
                'headers': [],
                'total_rows': 0,
                'preview_rows': []
            }
    
    def _parse_shapefile(self, file):
        """Parse Shapefile and extract preview data"""
        try:
            # For now, return basic file info since shapefile parsing requires additional libraries
            return {
                'file_type': 'shapefile',
                'file_extension': os.path.splitext(file.name)[1].lower(),
                'file_content_preview': f'Shapefile: {file.name}\nSize: {file.size} bytes\nNote: Full parsing requires additional GIS libraries.'
            }
        except Exception as e:
            return {
                'error': f'Error parsing Shapefile: {str(e)}',
                'file_type': 'shapefile'
            }

class FilePreviewView(LoginRequiredMixin, View):
    def get(self, request):
        """Display file preview page"""
        preview_data = request.session.get('preview_data')
        
        if not preview_data:
            messages.error(request, 'No file to preview. Please upload a file first.')
            return redirect('uploads')
        
        return render(request, 'userdashboard/file_preview.html', {
            'preview_data': preview_data
        })
    
    def post(self, request):
        """Handle file confirmation or rejection"""
        preview_data = request.session.get('preview_data')
        
        if not preview_data:
            messages.error(request, 'No file to process. Please upload a file first.')
            return redirect('uploads')
        
        if 'confirm_upload' in request.POST:
            # Process the confirmed file
            try:
                # Here you would typically save to database, process the file, etc.
                messages.success(request, f'File "{preview_data["file_name"]}" uploaded successfully!')
                
                # Clean up temp file
                if 'file_path' in preview_data:
                    default_storage.delete(preview_data['file_path'])
                
                # Clear preview data from session
                del request.session['preview_data']
                
                return redirect('my_survey')
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
                return redirect('file_preview')
        
        elif 'reject_upload' in request.POST:
            # Clean up temp file
            if 'file_path' in preview_data:
                default_storage.delete(preview_data['file_path'])
            
            # Clear preview data from session
            del request.session['preview_data']
            
            messages.info(request, 'File upload cancelled.')
            return redirect('uploads')
        
        return redirect('file_preview')

class MySurveyView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            # Get user's KML surveys
            kml_surveys = KMLData.objects.filter(kml_file__user=request.user).order_by('-created_at')
            
            # Get user's file uploads that are surveys
            file_surveys = FileUpload.objects.filter(
                user=request.user,
                file_type__in=['kml', 'csv', 'shapefile']
            ).order_by('-created_at')
            
            # Get user's parcels
            parcels = UploadedParcel.objects.filter(user=request.user).order_by('-created_at')
            
            # Count statistics
            total_surveys = kml_surveys.count() + file_surveys.count()
            total_parcels = parcels.count()
            
            # Get recent survey activities
            recent_surveys = []
            
            # Add KML surveys
            for kml in kml_surveys[:5]:
                recent_surveys.append({
                    'type': 'kml',
                    'name': kml.placemark_name or kml.kitta_number or f"KML Survey {kml.id}",
                    'date': kml.created_at,
                    'status': 'Completed',
                    'details': f"Coordinates: {kml.latitude}, {kml.longitude}" if kml.latitude and kml.longitude else "No coordinates"
                })
            
            # Add file surveys
            for file in file_surveys[:5]:
                recent_surveys.append({
                    'type': file.file_type,
                    'name': file.original_filename,
                    'date': file.created_at,
                    'status': 'Uploaded',
                    'details': f"File size: {file.file.size} bytes" if file.file else "No file"
                })
            
            # Sort by date
            recent_surveys.sort(key=lambda x: x['date'], reverse=True)
            
            context = {
                'kml_surveys': kml_surveys[:10],  # Show last 10
                'file_surveys': file_surveys[:10],  # Show last 10
                'parcels': parcels[:10],  # Show last 10
                'total_surveys': total_surveys,
                'total_parcels': total_parcels,
                'recent_surveys': recent_surveys[:10],
            }
            
            return render(request, 'userdashboard/my_survey.html', context)
            
        except Exception as e:
            print(f"MySurvey error: {e}")
            context = {
                'kml_surveys': [],
                'file_surveys': [],
                'parcels': [],
                'total_surveys': 0,
                'total_parcels': 0,
                'recent_surveys': [],
            }
            return render(request, 'userdashboard/my_survey.html', context)



class HistoryView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            # Get user's file upload history
            file_history = FileUpload.objects.filter(user=request.user).order_by('-created_at')
            
            # Get user's KML upload history
            kml_history = KMLData.objects.filter(kml_file__user=request.user).order_by('-created_at')
            
            # Get download history
            download_history = DownloadLog.objects.filter(user=request.user).order_by('-downloaded_at')
            
            # Get contact form submissions
            contact_history = ContactFormSubmission.objects.filter(user=request.user).order_by('-submitted_at')
            
            # Get recent activities from session
            recent_activities = request.session.get('recent_activities', [])[::-1][:50]
            
            # Combine all activities
            all_activities = []
            
            # Add file uploads
            for file in file_history[:20]:
                all_activities.append({
                    'type': 'upload',
                    'title': f'Uploaded {file.original_filename}',
                    'description': f'File type: {file.file_type}, Size: {file.file.size if file.file else "Unknown"} bytes',
                    'timestamp': file.created_at,
                    'icon': '📁'
                })
            
            # Add KML activities
            for kml in kml_history[:20]:
                all_activities.append({
                    'type': 'survey',
                    'title': f'Created survey: {kml.placemark_name or kml.kitta_number or "KML Data"}',
                    'description': f'Coordinates: {kml.latitude}, {kml.longitude}' if kml.latitude and kml.longitude else 'No coordinates',
                    'timestamp': kml.created_at,
                    'icon': '🗺️'
                })
            
            # Add downloads
            for download in download_history[:20]:
                all_activities.append({
                    'type': 'download',
                    'title': f'Downloaded {download.file.original_filename if download.file else "file"}',
                    'description': f'Downloaded at {download.downloaded_at.strftime("%Y-%m-%d %H:%M")}',
                    'timestamp': download.downloaded_at,
                    'icon': '⬇️'
                })
            
            # Add contact submissions
            for contact in contact_history[:10]:
                all_activities.append({
                    'type': 'contact',
                    'title': f'Contact form: {contact.subject}',
                    'description': f'Submitted on {contact.submitted_at.strftime("%Y-%m-%d %H:%M")}',
                    'timestamp': contact.submitted_at,
                    'icon': '📧'
                })
            
            # Add session activities
            for activity in recent_activities:
                if isinstance(activity, dict) and 'timestamp' in activity:
                    all_activities.append({
                        'type': 'session',
                        'title': activity.get('action', 'Activity'),
                        'description': activity.get('description', ''),
                        'timestamp': activity.get('timestamp', timezone.now()),
                        'icon': '👤'
                    })
            
            # Sort by timestamp
            all_activities.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Paginate activities
            paginator = Paginator(all_activities, 20)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            # Calculate statistics
            total_uploads = file_history.count()
            total_surveys = kml_history.count()
            total_downloads = download_history.count()
            total_contacts = contact_history.count()
            
            context = {
                'file_history': file_history[:10],
                'kml_history': kml_history[:10],
                'download_history': download_history[:10],
                'contact_history': contact_history[:5],
                'activities': page_obj,
                'total_uploads': total_uploads,
                'total_surveys': total_surveys,
                'total_downloads': total_downloads,
                'total_contacts': total_contacts,
            }
            
            return render(request, 'userdashboard/history.html', context)
            
        except Exception as e:
            print(f"History error: {e}")
            context = {
                'file_history': [],
                'kml_history': [],
                'download_history': [],
                'contact_history': [],
                'activities': [],
                'total_uploads': 0,
                'total_surveys': 0,
                'total_downloads': 0,
                'total_contacts': 0,
            }
            return render(request, 'userdashboard/history.html', context)

class HelpView(LoginRequiredMixin, View):
    def get(self, request):
        # Get any success/error messages from session
        contact_msg = request.session.get('contact_msg', '')
        contact_status = request.session.get('contact_status', '')
        
        # Get user's contact form history
        contact_history = ContactFormSubmission.objects.filter(user=request.user).order_by('-submitted_at')[:5]
        # Get recent activities from session
        recent_activities = request.session.get('recent_activities', [])[::-1][:20]
        # Clear messages from session after retrieving
        if 'contact_msg' in request.session:
            del request.session['contact_msg']
        if 'contact_status' in request.session:
            del request.session['contact_status']
        
        return render(request, 'userdashboard/help.html', {
            'contact_msg': contact_msg,
            'contact_status': contact_status,
            'contact_history': contact_history,
            'recent_activities': recent_activities,
        })
    
    def post(self, request):
        """Handle contact form submission"""
        if 'contact_submit' in request.POST:
            try:
                # Get form data
                name = request.POST.get('name', '').strip()
                email = request.POST.get('email', '').strip()
                subject = request.POST.get('subject', '').strip()
                message = request.POST.get('message', '').strip()
                
                # Validate form data
                if not name or len(name) < 2:
                    msg = 'Please enter a valid name (at least 2 characters).'
                    status = 'error'
                elif not email or not self._is_valid_email(email):
                    msg = 'Please enter a valid email address.'
                    status = 'error'
                elif not subject:
                    msg = 'Please select a subject.'
                    status = 'error'
                elif not message or len(message) < 10:
                    msg = 'Please enter a message (at least 10 characters).'
                    status = 'error'
                else:
                    # Process the contact form (you can add email sending logic here)
                    self._process_contact_form(name, email, subject, message, request.user)
                    msg = 'Thank you for your message! We will get back to you soon.'
                    status = 'success'
                    
                    # Add activity to user's history
                    self._add_activity(request, f"Submitted contact form: {subject}")
                
            except Exception as e:
                msg = f'Error submitting form: {str(e)}'
                status = 'error'
            
            # Store message in session
            request.session['contact_msg'] = msg
            request.session['contact_status'] = status
            
            # Redirect back to help page
            return redirect('help')
        
        return redirect('help')
    
    def _is_valid_email(self, email):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _process_contact_form(self, name, email, subject, message, user):
        """Process contact form submission"""
        # Save to database
        ContactFormSubmission.objects.create(
            user=user,
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        # Log the submission
        print(f"Contact Form Submission:")
        print(f"  From: {name} ({email})")
        print(f"  Subject: {subject}")
        print(f"  Message: {message}")
        print(f"  User: {user.email}")
        print(f"  Timestamp: {timezone.now()}")
        
        # TODO: Add email notification logic here
        # You can integrate with Django's email backend to send notifications
    
    def _add_activity(self, request, activity):
        """Add activity to user's session"""
        activities = request.session.get('recent_activities', [])
        activities.append(f"{timezone.now().strftime('%Y-%m-%d %H:%M')} - {activity}")
        # Keep only last 50 activities
        if len(activities) > 50:
            activities = activities[-50:]
        request.session['recent_activities'] = activities

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            total_files = FileUpload.objects.filter(user=request.user).count()
            total_surveys = KMLData.objects.filter(kml_file__user=request.user).count()
            
            # Calculate profile completion percentage
            personal_fields = [
                bool(request.user.full_name),
                bool(request.user.phone_number),
                bool(request.user.date_of_birth),
                bool(request.user.address),
                bool(request.user.city),
                bool(request.user.state),
                bool(request.user.country),
                bool(request.user.postal_code),
                bool(request.user.avatar and request.user.avatar.url)
            ]
            
            social_fields = [
                bool(request.user.github),
                bool(request.user.linkedin),
                bool(request.user.facebook)
            ]
            
            personal_completion = int((sum(personal_fields) / len(personal_fields)) * 100)
            social_completion = int((sum(social_fields) / len(social_fields)) * 100)
            
            # Overall completion: 80% for personal info + 20% for social links
            if personal_completion == 100 and social_completion == 100:
                profile_completion = 100
                is_verified = True
            elif personal_completion == 100:
                profile_completion = 80
                is_verified = False
            else:
                profile_completion = personal_completion
                is_verified = False
            
            # Get recent activities from session
            recent_activities = request.session.get('recent_activities', [])
            
            context = {
                'user': request.user,
                'total_files': total_files,
                'total_surveys': total_surveys,
                'profile_completion': profile_completion,
                'personal_completion': personal_completion,
                'social_completion': social_completion,
                'is_verified': is_verified,
                'recent_activities': recent_activities[::-1][:10],
            }
            
            return render(request, 'userdashboard/profile.html', context)
            
        except Exception as e:
            print(f"Profile error: {e}")
            context = {
                'user': request.user,
                'total_files': 0,
                'total_surveys': 0,
                'profile_completion': 0,
                'personal_completion': 0,
                'social_completion': 0,
                'is_verified': False,
                'recent_activities': [],
            }
            return render(request, 'userdashboard/profile.html', context)

    def post(self, request):
        user = request.user
        
        # Profile update
        if 'update_profile' in request.POST:
            try:
                # Get form data
                full_name = request.POST.get('full_name', '').strip()
                phone = request.POST.get('phone_number', '').strip()
                date_of_birth = request.POST.get('date_of_birth', '').strip()
                address = request.POST.get('address', '').strip()
                city = request.POST.get('city', '').strip()
                state = request.POST.get('state', '').strip()
                country = request.POST.get('country', '').strip()
                postal_code = request.POST.get('postal_code', '').strip()
                
                # Validation
                if full_name and len(full_name) < 2:
                    messages.error(request, 'Full name must be at least 2 characters long.')
                elif full_name and len(full_name) > 150:
                    messages.error(request, 'Full name must be less than 150 characters.')
                elif phone and not self._is_valid_phone(phone):
                    messages.error(request, 'Please enter a valid phone number.')
                else:
                    # Update user data
                    user.full_name = full_name
                    user.phone_number = phone
                    user.date_of_birth = date_of_birth if date_of_birth else None
                    user.address = address
                    user.city = city
                    user.state = state
                    user.country = country
                    user.postal_code = postal_code
                    
                    # Handle avatar upload
                    avatar = request.FILES.get('avatar')
                    if avatar:
                        if avatar.size > 5 * 1024 * 1024:  # 5MB limit
                            messages.error(request, 'Avatar file size must be less than 5MB.')
                        elif not avatar.content_type.startswith('image/'):
                            messages.error(request, 'Please upload a valid image file (JPG, PNG, GIF).')
                        elif not self._is_valid_image_extension(avatar.name):
                            messages.error(request, 'Please upload a valid image file (JPG, PNG, GIF).')
                        else:
                            user.avatar = avatar
                    
                    user.save()
                    messages.success(request, 'Profile updated successfully!')
                    self._add_activity(request, "Updated profile information")
                    
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
            
            return redirect('profile')
        
        elif 'update_social' in request.POST:
            try:
                # Get social links
                github = request.POST.get('github', '').strip()
                linkedin = request.POST.get('linkedin', '').strip()
                facebook = request.POST.get('facebook', '').strip()
                
                # Validation
                if github and not self._is_valid_url(github):
                    messages.error(request, 'Please enter a valid GitHub URL.')
                elif linkedin and not self._is_valid_url(linkedin):
                    messages.error(request, 'Please enter a valid LinkedIn URL.')
                elif facebook and not self._is_valid_url(facebook):
                    messages.error(request, 'Please enter a valid Facebook URL.')
                else:
                    # Update social links
                    user.github = github
                    user.linkedin = linkedin
                    user.facebook = facebook
                    user.save()
                    
                    messages.success(request, 'Social links updated successfully!')
                    self._add_activity(request, "Updated social links")
                    
            except Exception as e:
                messages.error(request, f'Error updating social links: {str(e)}')
            
            return redirect('profile')
        
        elif 'update_settings' in request.POST:
            try:
                # Get settings
                email_notifications = request.POST.get('email_notifications') == 'on'
                two_factor_enabled = request.POST.get('two_factor_enabled') == 'on'
                public_profile = request.POST.get('public_profile') == 'on'
                
                # Update settings
                user.email_notifications = email_notifications
                user.two_factor_enabled = two_factor_enabled
                user.public_profile = public_profile
                user.save()
                
                messages.success(request, 'Settings updated successfully!')
                self._add_activity(request, "Updated account settings")
                
            except Exception as e:
                messages.error(request, f'Error updating settings: {str(e)}')
            
            return redirect('profile')
            
        elif 'change_password' in request.POST:
            try:
                current_password = request.POST.get('current_password', '').strip()
                new_password = request.POST.get('new_password', '').strip()
                confirm_password = request.POST.get('confirm_password', '').strip()
                
                # Validation
                if not user.check_password(current_password):
                    messages.error(request, 'Current password is incorrect.')
                elif not new_password:
                    messages.error(request, 'New password is required.')
                elif len(new_password) < 8:
                    messages.error(request, 'New password must be at least 8 characters long.')
                elif new_password != confirm_password:
                    messages.error(request, 'New passwords do not match.')
                else:
                    # Update password
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    
                    messages.success(request, 'Password changed successfully!')
                    self._add_activity(request, "Changed password")
                    
            except Exception as e:
                messages.error(request, f'Error changing password: {str(e)}')
            
            return redirect('profile')
        
        elif 'delete_account' in request.POST:
            try:
                # Delete all associated data
                FileUpload.objects.filter(user=user).delete()
                KMLData.objects.filter(kml_file__user=user).delete()
                KMLFile.objects.filter(user=user).delete()
                UploadedParcel.objects.filter(user=user).delete()
                DownloadLog.objects.filter(user=user).delete()
                ContactFormSubmission.objects.filter(user=user).delete()
                
                # Delete user
                user.delete()
                logout(request)
                messages.success(request, 'Your account has been deleted successfully.')
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'Error deleting account: {str(e)}')
                return redirect('profile')

    def _is_valid_phone(self, phone):
        """Validate phone number format"""
        import re
        phone_pattern = r'^\+?1?\d{9,15}$'
        return re.match(phone_pattern, phone) is not None

    def _is_valid_url(self, url):
        """Validate URL format"""
        import re
        url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
        return re.match(url_pattern, url) is not None

    def _is_valid_image_extension(self, filename):
        """Validate image file extension"""
        import os
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        file_extension = os.path.splitext(filename)[1].lower()
        return file_extension in allowed_extensions

    def _add_activity(self, request, activity_type):
        """Add activity to user's recent activities"""
        recent_activities = request.session.get('recent_activities', [])
        activity = {
            'type': activity_type,
            'timestamp': timezone.now().isoformat(),
        }
        recent_activities.append(activity)
        
        # Keep only last 20 activities
        if len(recent_activities) > 20:
            recent_activities = recent_activities[-20:]
        
        request.session['recent_activities'] = recent_activities
