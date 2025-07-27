# 🔐 Authentication Flow Documentation

## Overview
The GeoSurvey application implements a secure authentication flow that ensures users must log in before accessing the dashboard.

## 🔄 Flow Description

### 1. **Server Startup**
When you run `python manage.py runserver`, the server starts and listens on `http://127.0.0.1:8000/`

### 2. **Root URL Access**
- **URL**: `http://127.0.0.1:8000/`
- **Action**: Automatically redirects to login page
- **Redirect**: `http://127.0.0.1:8000/api/account/login-page/`

### 3. **Login Page**
- **URL**: `http://127.0.0.1:8000/api/account/login-page/`
- **Features**:
  - Email and password input fields
  - Form validation
  - Error handling
  - Link to signup page
  - Responsive design

### 4. **Authentication Process**
- **Login API**: `POST /api/account/login/`
- **Process**:
  1. User enters credentials
  2. Frontend sends AJAX request to login API
  3. Backend validates credentials
  4. If valid: Creates session and JWT tokens
  5. Redirects to dashboard

### 5. **Post-Login Redirect**
- **Regular Users**: Redirected to `/dashboard/`
- **Admin Users**: Redirected to `/admin-dashboard/` (if email matches admin criteria)

### 6. **Dashboard Access**
- **URL**: `http://127.0.0.1:8000/dashboard/`
- **Protection**: Requires authentication
- **Features**: Full dashboard with navigation and user profile

### 7. **Logout**
- **URL**: `http://127.0.0.1:8000/logout/`
- **Action**: Clears session and redirects to login page

## 🛡️ Security Features

### Authentication Protection
- All dashboard views use `LoginRequiredMixin`
- Unauthenticated users are automatically redirected to login
- Session-based authentication with JWT tokens

### URL Configuration
```python
# Main URLs (geosurvey/urls.py)
path('', lambda request: redirect('/api/account/login-page/'), name='root')
path('login/', lambda request: redirect('/api/account/login-page/'), name='login_redirect')
path('logout/', LogoutView.as_view(), name='logout')
path('dashboard/', include('userdashboard.urls'))
```

### Settings Configuration
```python
# Settings (geosurvey/settings.py)
LOGIN_URL = '/api/account/login-page/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/api/account/login-page/'
```

## 🧪 Testing

### Manual Testing
1. Start server: `python manage.py runserver`
2. Open browser: `http://127.0.0.1:8000/`
3. Should redirect to login page
4. Enter credentials and login
5. Should redirect to dashboard

### Automated Testing
Run the test script: `python test_auth_flow.py`

## 📱 User Experience

### Responsive Design
- Login page works on all devices
- Smooth transitions and animations
- Error handling with user-friendly messages

### Navigation
- Clear login/signup links
- Profile dropdown with logout option
- Breadcrumb navigation in dashboard

## 🔧 Customization

### Adding New Protected Views
```python
from django.contrib.auth.mixins import LoginRequiredMixin

class MyProtectedView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'my_template.html')
```

### Custom Redirect URLs
```python
# In views.py
class LoginView(APIView):
    def post(self, request):
        # Custom redirect logic
        if user.is_admin:
            redirect_url = '/admin-dashboard/'
        else:
            redirect_url = '/dashboard/'
```

## 🚀 Quick Start

1. **Clone and setup project**
2. **Run migrations**: `python manage.py migrate`
3. **Create superuser**: `python manage.py createsuperuser`
4. **Start server**: `python manage.py runserver`
5. **Access application**: `http://127.0.0.1:8000/`

The authentication flow is now fully functional and secure! 🎉 