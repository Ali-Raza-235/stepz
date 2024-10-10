from django.contrib import admin
from .models import Payment, Order, OrderProduct

# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('product', 'quantity', 'product_price', 'ordered')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'phone', 'email', 'address', 'order_total', 'delivery_fee', 'status', 'is_ordered', 'created_at', 'payment_id']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'name', 'phone', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]

    def payment_id(self, obj):
        return obj.payment.payment_id if obj.payment else "No Payment"
    payment_id.short_description = 'Payment ID'  # Optional: set a short description for the column

    def full_name(self, obj):
        return obj.name  # Updated for the new structure

    full_name.short_description = 'Full Name'


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
