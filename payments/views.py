from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import FileResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import date
import random, string
from io import BytesIO

from customers.models import Customer
from loans.models import Loan
from .models import Payment, Receipt
from .forms import PaymentForm

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Loan

@csrf_exempt
@login_required
def delete_loan(request, loan_id):
    if request.method == "POST":
        loan = get_object_or_404(Loan, id=loan_id)

        if loan.status == "Completed":
            loan.delete()
            return JsonResponse({"success": True, "message": "Loan deleted successfully!"})
        else:
            return JsonResponse({"success": False, "message": "Only completed loans can be deleted."}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)


# 🟢 Step 1: Customer List
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'payments/customers.html', {'customers': customers})


# 🟢 Step 2: Make Payment
@login_required
def make_payment(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    loans = Loan.objects.filter(customer=customer)
    payments = Payment.objects.filter(loan__in=loans).order_by('-payment_date')

    form = PaymentForm(request.POST or None)
    form.fields['loan'].queryset = loans  # Only this customer’s loans

    if request.method == 'POST' and form.is_valid():
        payment = form.save(commit=False)
        loan = payment.loan

        # 🧮 Duration & Interest Calculation
        duration_value = getattr(loan, 'duration_value', 12)
        duration_type = getattr(loan, 'duration_type', 'months').lower()
        interest_rate = loan.interest_rate

        # Convert years → months
        total_months = duration_value * 12 if duration_type in ['year', 'years'] else duration_value

        # Calculate interest & total payable
        interest = (loan.loan_amount * interest_rate * (total_months / 12)) / 100
        total_value = loan.loan_amount + interest

        # Calculate paid & remaining
        prev_paid = sum(p.amount_paid for p in Payment.objects.filter(loan=loan))
        remaining = total_value - prev_paid

        # ✅ If already fully paid
        if remaining <= 0:
            messages.warning(request, "🎉 Payment already completed! No remaining balance.")
            return redirect('make_payment', customer_id=customer.id)

        paid_now = payment.amount_paid

        # ✅ Prevent Overpayment
        if paid_now > remaining:
            messages.error(request, f"⚠ You entered ₹{paid_now}, but only ₹{remaining:.2f} is remaining.")
            return redirect('make_payment', customer_id=customer.id)

        # ✅ Valid Payment
        payment.remaining_amount = remaining - paid_now
        payment.payment_date = date.today()
        payment.save()

        # 🧾 Generate Receipt
        receipt_no = 'RCPT-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        Receipt.objects.create(payment=payment, receipt_no=receipt_no)

        # 🔒 Mark completed if done
        if payment.remaining_amount <= 0:
            loan.status = "Completed"
            loan.save()
            messages.success(request, "🎉 Final Payment Completed! Loan Closed Successfully.")
        else:
            messages.success(request, f"✅ Payment Successful! Remaining ₹{payment.remaining_amount:.2f}")

        return redirect('make_payment', customer_id=customer.id)

    last_payment = payments.first() if payments.exists() else None

    return render(request, 'payments/make_payment.html', {
        'customer': customer,
        'form': form,
        'payments': payments,
        'last_payment': last_payment,
    })


# 🟢 Step 3: Download PDF Receipt
@login_required
def download_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    loan = payment.loan

    # Interest Calculations
    duration_value = getattr(loan, 'duration_value', 12)
    duration_type = getattr(loan, 'duration_type', 'months').lower()
    interest_rate = loan.interest_rate
    total_months = duration_value * 12 if duration_type in ['year', 'years'] else duration_value

    interest_amount = (loan.loan_amount * interest_rate * (total_months / 12)) / 100
    total_value = loan.loan_amount + interest_amount
    total_paid = sum(p.amount_paid for p in Payment.objects.filter(loan=loan))
    remaining_amount = total_value - total_paid

    # 🧾 PDF setup
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    header = Paragraph(
        "<b><font size=16 color='#B8860B'>🏦 SHREE SAI GOLD FINANCE</font></b><br/>"
        "<font size=11>Amalner - Jalgaon, Maharashtra</font><br/>"
        "<font size=10 color='gray'>Contact: +91 9876543210 | Email: shreesaigold@gmail.com</font>",
        styles['Title']
    )
    elements.append(header)
    elements.append(Spacer(1, 12))

    # Divider line
    line = Table([[""]], colWidths=[450])
    line.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.gold)]))
    elements.append(line)
    elements.append(Spacer(1, 15))

    # Receipt Title
    elements.append(Paragraph("<b><font size=14 color='#DAA520'>PAYMENT RECEIPT</font></b>", styles['Title']))
    elements.append(Spacer(1, 12))

    # Customer Info
    customer_data = [
        ["Customer Name", f"{loan.customer.name}"],
        ["Mobile No.", f"{loan.customer.mobile}"],
        ["Address", f"{loan.customer.address}"],
        ["Loan ID", f"{loan.id}"],
        ["Payment Date", str(payment.payment_date)],
    ]
    customer_table = Table(customer_data, colWidths=[150, 350])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('BOX', (0, 0), (-1, -1), 1, colors.gold),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 20))

    # Loan Info
    loan_data = [
        ["Gold Type", loan.gold_item.gold_type],
        ["Loan Amount (₹)", f"{loan.loan_amount:.2f}"],
        ["Interest Rate (%)", f"{loan.interest_rate:.2f}"],
        ["Total Value (₹)", f"{total_value:.2f}"],
        ["Paid Till Now (₹)", f"{total_paid:.2f}"],
        ["This Payment (₹)", f"{payment.amount_paid:.2f}"],
        ["Remaining (₹)", f"{remaining_amount:.2f}"],
    ]
    loan_table = Table(loan_data, colWidths=[200, 300])
    loan_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1.2, colors.gold),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(loan_table)
    elements.append(Spacer(1, 25))

    # Signatures
    sign_table = Table([
        ["Authorized Signatory", "", "Customer Signature"],
        ["(Shree Sai Gold Finance)", "", f"({loan.customer.name})"]
    ], colWidths=[200, 100, 200])
    sign_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LINEABOVE', (0, 1), (0, 1), 1, colors.gray),
        ('LINEABOVE', (2, 1), (2, 1), 1, colors.gray),
    ]))
    elements.append(sign_table)
    elements.append(Spacer(1, 15))

    # Footer Note
    footer = Paragraph(
        "<font size=9 color='gray'>This is a computer-generated receipt. "
        "No signature required.<br/>Thank you for trusting <b>Shree Sai Gold Finance</b>. 💛</font>",
        styles['Normal']
    )
    elements.append(footer)

    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"payment_receipt_{payment.id}.pdf")
