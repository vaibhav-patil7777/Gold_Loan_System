from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    aadhaar = models.CharField(max_length=20)
    pan = models.CharField(max_length=20)
    dob = models.DateField()
    email = models.EmailField()

    def __str__(self):
        return self.name
