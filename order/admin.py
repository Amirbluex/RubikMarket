from django.contrib import admin
from . import models


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'receiver_info', 'is_paid')
    inlines = (OrderItemInline,)
    list_filter = ('is_paid',)
