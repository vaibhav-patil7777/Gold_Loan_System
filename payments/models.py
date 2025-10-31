from django.db import models
from loans.models import Loan

class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount_paid = models.FloatField()
    payment_date = models.DateField(auto_now_add=True)
    remaining_amount = models.FloatField(default=0.0)

    def __str__(self):
        return f"Payment for Loan #{self.loan.id} - ₹{self.amount_paid}"



class Receipt(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="payment_receipt")
    loan = models.ForeignKey(Loan, on_delete=models.SET_NULL, null=True, blank=True, related_name="loan_receipts")

    customer_name = models.CharField(max_length=100)
    customer_mobile = models.CharField(max_length=15)
    customer_address = models.TextField()

    gold_item = models.CharField(max_length=100, blank=True, null=True)
    gold_weight = models.FloatField(blank=True, null=True)
    gold_purity = models.CharField(max_length=50, blank=True, null=True)

    receipt_no = models.CharField(max_length=20, unique=True)
    total_amount = models.FloatField(default=0.0)  # ✅ FIXED HERE
    remaining_amount = models.FloatField(default=0.0)
    next_installment_date = models.DateField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    email = models.EmailField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Receipt #{self.receipt_no} - {self.customer_name}"
