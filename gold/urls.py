from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:customer_id>/', views.add_gold, name='add_gold'),

]
