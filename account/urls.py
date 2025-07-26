from django.urls import path
from .views import SignupView, LoginView, LoginPageView, SignupPageView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup_api'),
    path('login/', LoginView.as_view(), name='login_api'),
    path('signup-page/', SignupPageView.as_view(), name='signup_page'),
    path('login-page/', LoginPageView.as_view(), name='login_page'),
] 