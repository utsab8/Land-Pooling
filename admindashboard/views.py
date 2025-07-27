from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Create your views here.

class AdminDashboardView(LoginRequiredMixin, View):
    login_url = '/api/account/login-page/'
    
    def get(self, request):
        # Check if user is staff/admin
        if not request.user.is_staff:
            return redirect('/api/account/login-page/')
        return render(request, 'admindashboard/dashboard.html')
