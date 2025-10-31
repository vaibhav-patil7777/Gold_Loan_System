from django.urls import path
from . import views

urlpatterns = [
   path('add/<int:customer_id>/', views.add_loan, name='add_loan'),
   path('receipts/<int:loan_id>/download/', views.download_receipts, name='download_receipts'),
]
