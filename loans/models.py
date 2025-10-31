from django.db import models
from datetime import timedelta
from customers.models import Customer
from gold.models import GoldItem

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    gold_item = models.ForeignKey(GoldItem, on_delete=models.CASCADE)
    loan_amount = models.FloatField()
    interest_rate = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)  # ✅ Auto-calculated
    duration_type = models.CharField(max_length=20, default='months')  # "months" or "years"
    duration_value = models.IntegerField(default=12)
    loan_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='Active')

    def save(self, *args, **kwargs):
        """Auto-calculate the end date based on start_date and duration."""
        if self.start_date and self.duration_value:
            try:
                duration_value = int(self.duration_value)
                duration_type = self.duration_type.lower().strip()

                if duration_type in ["month", "months"]:
                    self.end_date = self.start_date + timedelta(days=30 * duration_value)
                elif duration_type in ["year", "years"]:
                    self.end_date = self.start_date + timedelta(days=365 * duration_value)
                else:
                    # Default fallback (in case of unexpected input)
                    self.end_date = self.start_date + timedelta(days=30 * duration_value)

            except Exception as e:
                print("⚠️ Error calculating end_date:", e)
                self.end_date = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.name} - {self.gold_item.gold_type} ({self.gold_item.weight}g)"
