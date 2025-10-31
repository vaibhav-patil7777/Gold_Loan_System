# history/views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Sum
from customers.models import Customer
from gold.models import GoldItem
from loans.models import Loan
from payments.models import Payment, Receipt

# 🟢 History List – Show all customers + Loan Status & Remaining Balance
def history_list(request):
    query = request.GET.get('q', '').strip()

    # base queryset
    customers_qs = Customer.objects.all()

    if query:
        customers_qs = customers_qs.filter(
            Q(name__icontains=query) |
            Q(mobile__icontains=query) |
            Q(address__icontains=query)
        )

    customer_data = []
    for customer in customers_qs:
        loans = Loan.objects.filter(customer=customer)

        # If there are no loans for this customer
        if not loans.exists():
            loan_status = "No Loan"
            remaining_balance = 0.0
            total_loan = 0.0
            total_paid = 0.0
        else:
            # Sum of loan principal amounts
            total_loan = loans.aggregate(total=Sum('loan_amount'))['total'] or 0.0

            # Sum of payments for all loans of this customer (use amount_paid field)
            total_paid = Payment.objects.filter(loan__in=loans).aggregate(total=Sum('amount_paid'))['total'] or 0.0

            remaining_balance = round((total_loan - total_paid), 2)

            if remaining_balance <= 0:
                loan_status = "Completed"
            else:
                loan_status = "Active"

        customer_data.append({
            'id': customer.id,
            'name': customer.name,
            'mobile': customer.mobile,
            'address': customer.address,
            'loan_status': loan_status,
            'remaining_balance': remaining_balance,
            'total_loan': total_loan,
            'total_paid': total_paid,
        })

    context = {
        'customers': customer_data,
        'query': query,
    }
    return render(request, 'history/history_list.html', context)


# 🟢 History Detail – Show all info of selected customer (keeps previous behaviour)
def history_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    gold_items = GoldItem.objects.filter(customer=customer)
    loans = Loan.objects.filter(customer=customer)
    payments = Payment.objects.filter(loan__in=loans).order_by('-payment_date')
    receipts = Receipt.objects.filter(payment__in=payments)

    # Also compute per-loan remaining amounts (optional helpful data)
    per_loan_info = []
    for loan in loans:
        principal = loan.loan_amount or 0.0
        paid = Payment.objects.filter(loan=loan).aggregate(total=Sum('amount_paid'))['total'] or 0.0

        # calculate interest if you want to include it here, else just remaining principal
        remaining = round(principal - paid, 2)
        status = "Completed" if remaining <= 0 else "Active"
        per_loan_info.append({
            'loan': loan,
            'principal': principal,
            'paid': paid,
            'remaining': remaining,
            'status': status
        })

    return render(request, 'history/history_details.html', {
        'customer': customer,
        'gold_items': gold_items,
        'loans': loans,
        'payments': payments,
        'receipts': receipts,
        'per_loan_info': per_loan_info,
    })
