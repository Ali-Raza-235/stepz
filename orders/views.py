from django.shortcuts import render, redirect
from cart.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, OrderProduct, Payment
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages

def place_order(request):
    current_user = request.user

    # If the cart count is less than or equal to 0, redirect to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    delivery_fee = 300  # Fixed delivery fee
    total = sum(item.product.price * item.quantity for item in cart_items)
    grand_total = total + delivery_fee  # Grand total includes delivery fee

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            order = Order()
            order.user = current_user
            order.name = form.cleaned_data['name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.order_total = grand_total  # Only product total
            order.delivery_fee = delivery_fee
            order.ip = request.META.get('REMOTE_ADDR')
            order.is_ordered = True  # Set order as confirmed immediately for COD
            order.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            current_date = datetime.date(yr, mt, dt).strftime("%Y%m%d")  # e.g., 20231009
            order.order_number = current_date + str(order.id)
            order.save()

            payment = Payment.objects.create(
                payment_id = f"COD{order.order_number}",
                user = request.user,
                payment_method = "Cash On Delivery",
                amount_paid = order.order_total,
            )
            payment.save()

            order.payment = payment
            order.save()

            # Create OrderProduct entries for each cart item
            for cart_item in cart_items:
                order_product = OrderProduct.objects.create(
                    order=order,
                    user=current_user,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    product_price=cart_item.product.price,
                    ordered=True
                )
                order_product.payment = payment
                order_product.save()

                # Set variations for the OrderProduct
                variations = cart_item.variations.all()
                order_product.variations.set(variations)

                # Reduce the product stock
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()

            # Clear the cart
            cart_items.delete()

            # Send confirmation email to user
            mail_subject = 'Thank you for your order!'
            message = render_to_string('orders/order_recieved_email.html', {'order': order})
            to_email = current_user.email
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()

            # Display order confirmation message
            messages.success(request, 'Your order has been placed successfully!')

            # Redirect to order detail page
            return redirect('order_detail', order_id=order.order_number)
    else:
        return redirect('checkout')  # Redirect to checkout if not a POST request


def place_order_cod(request):
    return place_order(request)  # Call the place_order function as COD order
