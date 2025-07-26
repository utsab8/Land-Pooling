from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSignupSerializer, UserLoginSerializer
from .models import User
from django.contrib.auth import login as django_login

# Render login page
from django.views import View

class LoginPageView(View):
    def get(self, request):
        next_url = request.GET.get('next', '/dashboard/profile/')
        if request.user.is_authenticated:
            return redirect(next_url)
        return render(request, 'account/login.html', {'next': next_url})

class SignupPageView(View):
    def get(self, request):
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
            # Admin credentials check
            if user.email == 'acharyautsab390@gmail.com' and request.data.get('password') == 'utsab12@':
                redirect_url = '/admin-dashboard/'
            else:
                redirect_url = request.data.get('next') or '/dashboard/'
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
