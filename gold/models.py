from django.db import models
from customers.models import Customer

class GoldItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    gold_type = models.CharField(max_length=50)
    weight = models.FloatField()
    purity = models.CharField(max_length=20)
    valuation = models.FloatField()
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.gold_type} - {self.customer.name}"
