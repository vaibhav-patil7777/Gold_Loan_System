from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_customer, name='add_customer'),
]
