from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout
from django.http import JsonResponse, HttpResponse
from account.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import ContactFormSubmission
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
            return redirect('/api/account/login-page/')
        return render(request, 'userdashboard/dashboard.html')

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
        return render(request, 'userdashboard/my_survey.html')



class HistoryView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'userdashboard/history.html')

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
        # Get recent activities from session
        recent_activities = request.session.get('recent_activities', [])
        
        # Calculate profile completion percentage
        completion_fields = [
            bool(request.user.full_name),
            bool(request.user.phone_number),
            bool(request.user.linkedin),
            bool(request.user.github),
            bool(request.user.avatar and request.user.avatar.url != '/media/avatars/default.png')
        ]
        completion_percentage = int((sum(completion_fields) / len(completion_fields)) * 100)
        
        # Get user statistics
        user_stats = {
            'days_since_joined': (timezone.now() - request.user.date_joined).days,
            'last_login': request.user.last_login,
            'is_active': request.user.is_active,
            'is_staff': request.user.is_staff,
        }
        
        return render(request, 'userdashboard/profile.html', {
            'user': request.user,
            'recent_activities': recent_activities[::-1][:10],  # Show last 10 activities
            'completion_percentage': completion_percentage,
            'user_stats': user_stats,
            'profile_msg': request.session.get('profile_msg', ''),
            'password_msg': request.session.get('password_msg', ''),
        })

    def post(self, request):
        user = request.user
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Profile update
        if 'avatar' in request.FILES or 'full_name' in request.POST or 'linkedin' in request.POST or 'github' in request.POST:
            try:
                # Validate and clean data
                full_name = request.POST.get('full_name', '').strip()
                phone_number = request.POST.get('phone_number', '').strip()
                linkedin = request.POST.get('linkedin', '').strip()
                github = request.POST.get('github', '').strip()
                
                # Enhanced validation
                if full_name and len(full_name) < 2:
                    msg = 'Full name must be at least 2 characters long.'
                elif full_name and len(full_name) > 150:
                    msg = 'Full name must be less than 150 characters.'
                elif phone_number and not self._is_valid_phone(phone_number):
                    msg = 'Please enter a valid phone number.'
                elif linkedin and not self._is_valid_url(linkedin):
                    msg = 'Please enter a valid LinkedIn URL.'
                elif github and not self._is_valid_url(github):
                    msg = 'Please enter a valid GitHub URL.'
                else:
                    # Update user data
                    user.full_name = full_name
                    user.phone_number = phone_number
                    user.linkedin = linkedin
                    user.github = github
                    
                    # Handle avatar upload
                    avatar = request.FILES.get('avatar')
                    if avatar:
                        # Enhanced file validation
                        if avatar.size > 5 * 1024 * 1024:  # 5MB limit
                            msg = 'Avatar file size must be less than 5MB.'
                        elif not avatar.content_type.startswith('image/'):
                            msg = 'Please upload a valid image file (JPG, PNG, GIF).'
                        elif not self._is_valid_image_extension(avatar.name):
                            msg = 'Please upload a valid image file (JPG, PNG, GIF).'
                        else:
                            user.avatar = avatar
                    
                    user.save()
                    msg = 'Profile updated successfully!'
                    self._add_activity(request, f"Updated profile information")
                    
                    # Clear any previous error messages
                    request.session.pop('profile_msg', None)
                    request.session['profile_msg'] = msg
                    
            except Exception as e:
                msg = f'Error updating profile: {str(e)}'
                request.session['profile_msg'] = msg
            
            if is_ajax:
                return JsonResponse({'status': 'success' if 'successfully' in msg else 'error', 'message': msg})
            return self.get(request)
            
        # Password change
        if 'current_password' in request.POST and 'new_password' in request.POST and 'confirm_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not current_password:
                msg = 'Current password is required.'
            elif not user.check_password(current_password):
                msg = 'Current password is incorrect.'
            elif not new_password:
                msg = 'New password is required.'
            elif new_password != confirm_password:
                msg = 'New passwords do not match.'
            elif len(new_password) < 8:
                msg = 'New password must be at least 8 characters long.'
            elif len(new_password) > 128:
                msg = 'New password must be less than 128 characters.'
            elif new_password == current_password:
                msg = 'New password must be different from current password.'
            elif not self._is_strong_password(new_password):
                msg = 'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character.'
            else:
                try:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    msg = 'Password updated successfully!'
                    self._add_activity(request, f"Changed password")
                    request.session.pop('password_msg', None)
                    request.session['password_msg'] = msg
                except Exception as e:
                    msg = f'Error changing password: {str(e)}'
                    request.session['password_msg'] = msg
            
            if is_ajax:
                return JsonResponse({'status': 'success' if 'successfully' in msg else 'error', 'message': msg})
            return self.get(request)
            
        # Export user data
        if 'export_data' in request.POST:
            try:
                # Enhanced user data export
                user_data = {
                    'user_info': {
                        'email': user.email,
                        'full_name': user.full_name,
                        'phone_number': user.phone_number,
                        'linkedin': user.linkedin,
                        'github': user.github,
                        'date_joined': user.date_joined.isoformat(),
                        'last_login': user.last_login.isoformat() if user.last_login else None,
                        'is_active': user.is_active,
                        'is_staff': user.is_staff,
                        'profile_completion': self._calculate_profile_completion(user)
                    },
                    'account_stats': {
                        'days_since_joined': (timezone.now() - user.date_joined).days,
                        'total_activities': len(request.session.get('recent_activities', [])),
                        'export_date': timezone.now().isoformat()
                    },
                    'recent_activities': request.session.get('recent_activities', []),
                    'export_metadata': {
                        'exported_at': timezone.now().isoformat(),
                        'export_version': '1.0',
                        'data_format': 'JSON'
                    }
                }
                
                response = HttpResponse(
                    json.dumps(user_data, indent=2, default=str),
                    content_type='application/json'
                )
                response['Content-Disposition'] = f'attachment; filename="geosurvey_user_data_{user.email}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
                self._add_activity(request, f"Exported user data")
                return response
                
            except Exception as e:
                msg = f'Error exporting data: {str(e)}'
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': msg})
                request.session['profile_msg'] = msg
                return self.get(request)
        
        # Account deletion
        if 'delete_account' in request.POST:
            try:
                self._add_activity(request, f"Account deletion requested")
                user.delete()
                logout(request)
                return redirect('/api/account/login-page/')
            except Exception as e:
                msg = f'Error deleting account: {str(e)}'
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': msg})
                request.session['profile_msg'] = msg
                return self.get(request)
                
        return self.get(request)

    def _add_activity(self, request, activity):
        """Add activity to user's recent activities"""
        activities = request.session.get('recent_activities', [])
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
        activities.append(f"{activity} - {timestamp}")
        request.session['recent_activities'] = activities[-20:]  # Keep last 20 activities
    
    def _is_valid_phone(self, phone):
        """Validate phone number format"""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        # Check if it's a valid phone number (7-15 digits, optionally starting with +)
        return re.match(r'^\+?[\d\s\-\(\)]{7,15}$', phone) is not None
    
    def _is_valid_url(self, url):
        """Validate URL format"""
        if not url:
            return True
        # Check if it's a valid URL
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    def _is_valid_image_extension(self, filename):
        """Validate image file extension"""
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        return any(filename.lower().endswith(ext) for ext in allowed_extensions)
    
    def _is_strong_password(self, password):
        """Validate password strength"""
        # Check for at least one uppercase, lowercase, number, and special character
        has_upper = re.search(r'[A-Z]', password)
        has_lower = re.search(r'[a-z]', password)
        has_digit = re.search(r'\d', password)
        has_special = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        
        return has_upper and has_lower and has_digit and has_special
    
    def _calculate_profile_completion(self, user):
        """Calculate profile completion percentage"""
        completion_fields = [
            bool(user.full_name),
            bool(user.phone_number),
            bool(user.linkedin),
            bool(user.github),
            bool(user.avatar and user.avatar.url != '/media/avatars/default.png')
        ]
        return int((sum(completion_fields) / len(completion_fields)) * 100)
