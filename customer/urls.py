
from django.urls import path
#now import the views.py file into this code
from . import views
urlpatterns=[
  path('',views.index, name='index'),
  path('registercustomer', views.registercustomer, name='registercustomer'),
  path('logincustomer', views.logincustomer, name='logincustomer'),
  path('logoutcustomer', views.logoutcustomer, name='logoutcustomer'),
  path('products', views.homepage, name='products'),
  path('addtocart', views.addproducttocart, name='addtocart'),
  path('removefromcart', views.removeproductfromcart, name='removefromcart'),
  path('viewcustomercart', views.viewcustomercart, name='viewcustomercart'),
  path('removefromcartpage/<int:cart_item_id>', views.removeproductcartpage, name='removeproductcartpage'),
  path('checkoutcustomer', views.checkoutcustomer, name='checkoutcustomer'),
  path('markpaymentsuccess', views.markpaymentsuccess, name='markpaymentsuccess'),
]