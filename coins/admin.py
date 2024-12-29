from django.contrib import admin

from .models import Coin, CoinWallet


@admin.register(CoinWallet)
class CoinWalletAdmin(admin.ModelAdmin):
    pass

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    pass 
