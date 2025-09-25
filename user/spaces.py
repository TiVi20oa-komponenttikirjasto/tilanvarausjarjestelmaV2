# Ylimäärinen sivu, joka ei ole käytössä tässä projektissa.
# Tämä tiedosto on tarkoitettu esimerkkinä siitä, miten voit määritellä tiloja, vuokrauksia ja lainoja Django-malleina.
from django.db import models
from django.contrib.auth.models import User

class Space(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.location})"

class Rental(models.Model):
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    renter = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Rental of {self.space.name} by {self.renter.username}"

class Loan(models.Model):
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_date = models.DateField()
    return_date = models.DateField()

    def __str__(self):
        return f"Loan of {self.space.name} to {self.borrower.username}"