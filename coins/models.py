from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class Coin(models.Model):
    coin_quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    price_type = models.CharField(max_length=100)

    def __str__(self):
        return self.price_type
    
    def get_total_price(self):
        return self.coin_quantity * self.price

class CoinWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.user.username}'s Coin Wallet"
    
    def deposit(self, amount):
        self.balance += amount
        self.save()
    
    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
        else:
            raise ValueError("Insufficient balance")
    
    
    
