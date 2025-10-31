from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from datetime import date
from customers.models import Customer
from gold.models import GoldItem
from .models import Loan
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# 🟡 ADD LOAN VIEW
def add_loan(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    gold_items = GoldItem.objects.filter(customer=customer)

    if request.method == 'POST':
        gold_item_id = request.POST.get('gold_item')
        loan_amount = request.POST.get('loan_amount')
        interest_rate = request.POST.get('interest_rate')
        loan_type = request.POST.get('loan_type')
        duration_type = request.POST.get('duration_type')
        duration_value = request.POST.get('duration_value')
        start_date = request.POST.get('start_date')

        # ✅ Input validation
        if not all([gold_item_id, loan_amount, interest_rate, loan_type, duration_type, duration_value, start_date]):
            messages.error(request, "⚠️ Please fill all fields!")
            return render(request, 'loans/add_loan.html', {'customer': customer, 'gold_items': gold_items})

        # ✅ Convert numeric fields
        try:
            duration_value = int(duration_value)
            loan_amount = float(loan_amount)
            interest_rate = float(interest_rate)
        except ValueError:
            messages.error(request, "⚠️ Invalid number format!")
            return render(request, 'loans/add_loan.html', {'customer': customer, 'gold_items': gold_items})

        gold_item = GoldItem.objects.get(id=gold_item_id)

        # ✅ Create loan
        loan = Loan.objects.create(
            customer=customer,
            gold_item=gold_item,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            loan_type=loan_type,
            duration_type=duration_type,
            duration_value=duration_value,
            start_date=start_date
        )

        # ✅ Success message and show download button
        messages.success(request, "✅ Loan added successfully! 🧾 You can now download the receipt below.")
        return render(request, 'loans/add_loan.html', {
            'customer': customer,
            'gold_items': gold_items,
            'loan': loan,
            'show_receipt': True  # To display the download button
        })

    return render(request, 'loans/add_loan.html', {'customer': customer, 'gold_items': gold_items})


# 🧾 DOWNLOAD RECEIPT (PDF)
# 🧾 DOWNLOAD RECEIPT (PROFESSIONAL GOLD RECEIPT)
# 🧾 DOWNLOAD RECEIPT (COMPLETE PROFESSIONAL VERSION)
def download_receipts(request, loan_id):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from datetime import timedelta, date

    loan = get_object_or_404(Loan, id=loan_id)

    # 🧮 Calculate End Date Automatically
    if loan.start_date and loan.duration_value:
        duration_type = str(loan.duration_type).lower()
        if duration_type in ["month", "months"]:
            end_date = loan.start_date + timedelta(days=30 * loan.duration_value)
        elif duration_type in ["year", "years"]:
            end_date = loan.start_date + timedelta(days=365 * loan.duration_value)
        else:
            end_date = None
    else:
        end_date = None

    # 🧮 Financial Calculations
    principal = loan.loan_amount
    rate = loan.interest_rate / 100
    months = loan.duration_value if "month" in loan.duration_type.lower() else loan.duration_value * 12

    # Total Interest (Simple Interest)
    total_interest = round((principal * rate * months) / 12, 2)
    total_payable = round(principal + total_interest, 2)
    emi = round(total_payable / months, 2)

    # Response setup
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Gold_Loan_Receipt_{loan.id}.pdf"'

    # PDF setup
    doc = SimpleDocTemplate(response, pagesize=A4,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    title = styles['Title']

    # 🏦 HEADER
    header = Paragraph(
        "<b><font size=16 color='#B8860B'>🏦 SHREE SAI GOLD FINANCE</font></b><br/>"
        "<font size=11>Amalner - Jalgaon, Maharashtra</font><br/>"
        "<font size=10 color='gray'>Contact: +91 9876543210 | Email: shreesaigold@gmail.com</font>",
        styles['Title']
    )
    elements.append(header)
    elements.append(Spacer(1, 12))

    # 🔸 Line Separator
    line_data = [["" for _ in range(1)]]
    line_table = Table(line_data, colWidths=[450])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.gold),
        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.gold)
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 15))

    # 📄 RECEIPT TITLE
    receipt_title = Paragraph(f"<b><font size=14 color='#DAA520'>GOLD LOAN RECEIPT</font></b>", styles['Title'])
    elements.append(receipt_title)
    elements.append(Spacer(1, 12))

    # 👤 CUSTOMER DETAILS
    customer_data = [
        ["Customer Name", f"{loan.customer.name}"],
        ["Mobile No.", f"{loan.customer.mobile}"],
        ["Address", f"{loan.customer.address}"],
        ["Loan ID", f"{loan.id}"],
        ["Date of Issue", f"{loan.start_date}"],
    ]
    customer_table = Table(customer_data, colWidths=[150, 350])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('BOX', (0, 0), (-1, -1), 1, colors.gold),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 20))

    # 💰 LOAN DETAILS TABLE
    loan_data = [
        ["Gold Type", loan.gold_item.gold_type],
        ["Weight (g)", loan.gold_item.weight],
        ["Purity (%)", loan.gold_item.purity],
        ["Valuation (₹)", f"{loan.gold_item.valuation}"],
        ["Loan Amount (₹)", f"{loan.loan_amount}"],
        ["Interest Rate (%)", f"{loan.interest_rate}"],
        ["Loan Type", loan.loan_type],
        ["Duration", f"{loan.duration_value} {loan.duration_type}"],
        ["Start Date", str(loan.start_date)],
        ["End Date", str(end_date) if end_date else "N/A"],
    ]
    loan_table = Table(loan_data, colWidths=[200, 300])
    loan_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1.2, colors.gold),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(loan_table)
    elements.append(Spacer(1, 25))

    # 📊 FINANCIAL SUMMARY BOX
    summary_data = [
        ["Total Loan Amount (₹)", f"{principal}"],
        ["Total Interest (₹)", f"{total_interest}"],
        ["Total Payable (₹)", f"{total_payable}"],
        ["Total EMIs", f"{months}"],
        ["Monthly EMI (₹)", f"{emi}"],
    ]
    summary_table = Table(summary_data, colWidths=[250, 250])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gold),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('BOX', (0, 0), (-1, -1), 1.2, colors.gold),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 25))

    # ✍️ SIGNATURE AREA
    sign_table = Table([
        ["Authorized Signatory", "", "Customer Signature"],
        ["(Shree Sai Gold Finance)", "", f"({loan.customer.name})"]
    ], colWidths=[200, 100, 200])
    sign_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('LINEABOVE', (0, 1), (0, 1), 1, colors.gray),
        ('LINEABOVE', (2, 1), (2, 1), 1, colors.gray),
    ]))
    elements.append(sign_table)
    elements.append(Spacer(1, 20))

    # 🟨 FOOTER NOTE
    footer = Paragraph(
        "<font size=9 color='gray'>This is a computer-generated receipt. No signature required.<br/>"
        "Thank you for trusting <b>Shree Sai Gold Finance</b>. 💛</font>",
        normal
    )
    elements.append(footer)

    # Save PDF
    doc.build(elements)
    return response
