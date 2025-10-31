from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from customers.models import Customer
from .models import GoldItem

def add_gold(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        gold_type = request.POST.get('gold_type')
        weight = request.POST.get('weight')
        purity = request.POST.get('purity')
        valuation = request.POST.get('valuation')

        print("🟡 DEBUG:", gold_type, weight, purity, valuation)  # Add this line

        if not all([gold_type, weight, purity, valuation]):
            messages.error(request, "Please fill all fields!")
            return render(request, 'gold/add_gold.html', {'customer': customer})

        GoldItem.objects.create(
            customer=customer,
            gold_type=gold_type,
            weight=weight,
            purity=purity,
            valuation=valuation
        )

        messages.success(request, "Gold item added successfully!")
        return redirect(f'/loans/add/{customer.id}/')

    return render(request, 'gold/add_gold.html', {'customer': customer})
