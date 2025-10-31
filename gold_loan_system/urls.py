from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home_redirect(request):
    return redirect('login')  # redirects to login page

urlpatterns = [
    path('', home_redirect, name='home'),  # 👈 this fixes the 404
    path('admin/', admin.site.urls),
    path('login/', include('accounts.urls')),
    path('customers/', include('customers.urls')),
    path('gold/', include('gold.urls')),
    path('loans/', include('loans.urls')),
    path('payments/', include('payments.urls')),
    path('history/', include('history.urls')),
]
