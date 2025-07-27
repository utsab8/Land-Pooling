from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSignupSerializer, UserLoginSerializer
from .models import User
from django.contrib.auth import login as django_login
from django.conf import settings

# Render login page
from django.views import View

class LoginPageView(View):
    def get(self, request):
        # If user is already authenticated, redirect to appropriate dashboard
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect('/admin-dashboard/')
            else:
                return redirect('/dashboard/')
        
        next_url = request.GET.get('next', '/dashboard/')
        return render(request, 'account/login.html', {'next': next_url})

class SignupPageView(View):
    def get(self, request):
        # If user is already authenticated, redirect to appropriate dashboard
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect('/admin-dashboard/')
            else:
                return redirect('/dashboard/')
        return render(request, 'account/signup.html')

class SignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Log in the user for session-based auth
            django_login(request, user)
            refresh = RefreshToken.for_user(user)
            
            # Determine redirect URL based on user type and permissions
            next_url = request.data.get('next', '/dashboard/')
            
            # Check if user is admin/staff
            if user.is_staff:
                redirect_url = '/admin-dashboard/'
            else:
                # Regular users go to user dashboard
                redirect_url = next_url if next_url != '/api/account/login-page/' else '/dashboard/'
            
            return Response({
                'user': {
                    'email': user.email,
                    'full_name': user.full_name,
                    'phone_number': user.phone_number,
                },
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'redirect_url': redirect_url,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
