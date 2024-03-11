from django.contrib import admin
from .models import Payment, Order, Order_Product


admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(Order_Product)
