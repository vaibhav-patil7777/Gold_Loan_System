from django.urls import path
from . import views

urlpatterns = [
    path('customers/', views.customer_list, name='customer_list'),
    path('make/<int:customer_id>/', views.make_payment, name='make_payment'),
    path('receipts/<int:payment_id>/download/', views.download_receipt, name='download_receipt'),
    path('loans/delete/<int:loan_id>/', views.delete_loan, name='delete_loan'),

]
