from django.shortcuts import render
from django.views import View

# Create your views here.

class AdminDashboardView(View):
    def get(self, request):
        return render(request, 'admindashboard/dashboard.html')
