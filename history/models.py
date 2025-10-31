from django.db import models
from customers.models import Customer
from gold.models import GoldItem
from loans.models import Loan
from payments.models import Payment


class History(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    gold_item = models.ForeignKey(GoldItem, on_delete=models.SET_NULL, null=True, blank=True)
    loan = models.ForeignKey(Loan, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=50)  # e.g. "Loan Created", "Payment Done", "Loan Closed"
    date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.customer.name} - {self.action_type} on {self.date.strftime('%d-%m-%Y')}"
