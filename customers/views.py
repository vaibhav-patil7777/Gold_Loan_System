from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customer
from .forms import CustomerForm

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customer

def add_customer(request):
    if request.method == 'POST':
        # Create new customer
        customer = Customer.objects.create(
            name=request.POST['name'],
            mobile=request.POST['mobile'],
            address=request.POST['address'],
            aadhaar=request.POST['aadhaar'],
            pan=request.POST['pan'],
            dob=request.POST['dob'],
            email=request.POST['email']
        )
        messages.success(request, f"Customer '{customer.name}' added successfully!")
        # Redirect to Add Gold page with customer_id
        return redirect(f'/gold/add/{customer.id}/')
    return render(request, 'customers/add_customer.html')
