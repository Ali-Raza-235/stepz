from django.urls import path
from . import views

urlpatterns = [
    path('place_order_cod/', views.place_order_cod, name='place_order_cod'),
]
