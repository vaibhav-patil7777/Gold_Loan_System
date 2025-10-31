from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('profile/',views.profile_view, name='profile'),
   path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-account/<str:email>/', views.reset_account, name='reset_account'),


    # ✅ add this new line
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
