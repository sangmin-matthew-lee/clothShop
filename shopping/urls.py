from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
path('shopping/', views.index, name='ShopHome'),
path('shopping/all-products/', views.all_products, name='AllProducts'),
path('shopping/about/', views.about, name='AboutUs'),
path('shopping/contact/', views.contact,name='ContactUs'),
path('shopping/tracker/', views.tracker,name='TrackingStatus'),
path('shopping/cancel/<int:order_id>/', views.cancel_order, name='CancelOrder'),
path('shopping/search/', views.search,name='Search'),
path('shopping/products/<int:myid>', views.productView,name='ProductView'),
path('shopping/checkout/', views.checkout,name='Checkout'),
path('shopping/recommend/', views.recommend_chatbot, name='Recommend'),
]
