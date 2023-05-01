from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User, auth

from admins.models import Products
from .models import CustomerCart,CustomerCheckout,customerPayedProducts
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .forms import CustomerCheckoutForm
import uuid
import razorpay

# Create your views here.
def index(request):
    products = Products.objects.filter(is_active=1)
    return render(request,'customer/admintemplate.html',{'products':products})


def registercustomer(request):
    if request.method == 'POST':
       first_name = request.POST['fname']
       last_name = request.POST['lname']
       username = request.POST['username']
       email = request.POST['email']
       pass1 = request.POST['pass1']
       pass2 = request.POST['pass2']
       
       if pass1 == pass2:
           if User.objects.filter(username = username).exists():
                messages.info(request,"username already exist")
                return redirect('registercustomer')
            
           elif User.objects.filter(email = email).exists():
               messages.info(request,"email is already exists")
               return redirect('registercustomer')
           else:
               user = User.objects.create_user(
                   first_name = first_name,
                   last_name = last_name,
                   username = username,
                   email = email,
                   password = pass1  
               )
               user.save()
               messages.info(request,'user is created')
               return redirect('logincustomer')
               
                
       else:
            messages.info(request,"password not matched")
            return redirect('registration')  
       
    else:
        return render(request,'customer/register/registercustomer.html')
    
def logincustomer(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admindashboard') )
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            
            user = auth.authenticate(
                username = username,
                password = password
                )
            if user is not None:
                auth.login(request, user)
                return redirect('/')
            else:
                messages.info(request, 'invalid credintial')
                return redirect('logincustomer')
            
        else:
            return render(request, 'customer/register/logincustomer.html')
    
@login_required(login_url = reverse_lazy('logincustomer'))    
def logoutcustomer(request):
    auth.logout(request)
    return redirect('/')

def homepage(request):
    products = Products.objects.filter(is_active=1)
    usercart = []
    if request.user.is_authenticated:
        usercart = CustomerCart.objects.filter(customer = request.user)
    return render(request,'customer/products.html',{'products':products,'usercart':usercart})
    
    
@csrf_exempt
@login_required
def addproducttocart(request):
    if request.is_ajax():
        product_id = int(request.POST['product'])
        user = request.user
        cart_instance = CustomerCart(product_id = product_id,
                                    customer = user)
        cart_instance.save()
        return JsonResponse({'result':'success'})

@csrf_exempt
@login_required
def removeproductfromcart(request):
    if request.is_ajax():
        product_id = int(request.POST['product'])
        user = request.user
        cart_instance = CustomerCart.objects.filter(customer = user,product=product_id)
        cart_instance.delete()
        return JsonResponse({'result':'success'})
    
@login_required(login_url = reverse_lazy('logincustomer'))
def viewcustomercart(request):
    usercart = CustomerCart.objects.filter(customer = request.user).select_related('product')
    totalprice = sum(item.product.price for item in usercart)
    checkoutForm = CustomerCheckoutForm()
    return render(request,'customer/customercart.html',{
        'usercart':usercart,
        'totalprice':totalprice,
        'checkoutform':checkoutForm
    })
    
@login_required(login_url = reverse_lazy('logincustomer'))
def removeproductcartpage(request,cart_item_id):
    user = request.user
    cart_instance = CustomerCart.objects.filter(customer = user,id=cart_item_id)
    cart_instance.delete()
    return HttpResponseRedirect(reverse('viewcustomercart'))

@login_required
def checkoutcustomer(request):
    if request.method == 'POST':
        user = request.user
        address = request.POST['address']
        phone = request.POST['phone']
        usercart = CustomerCart.objects.filter(customer = request.user).select_related('product')
        totalprice = sum(item.product.price for item in usercart)
        receipt = str(uuid.uuid1())
        client = razorpay.Client(auth=("rzp_test_bAYqeZhjXN8pf0", "cgw5fGdAZHz9CO1GCGp2UJG6"))
        DATA = {
            'amount':totalprice*100,
            'currency':'INR',
            'receipt':'masupreiept',
            'payment_capture':1,
            'notes':{}
        }
        order_details = client.order.create(data=DATA)
        # return HttpResponse(order_details)
        customercheckout_order_instance = CustomerCheckout(customer = request.user,
                                            order_id = order_details.get('id'),
                                            total_amount = totalprice,
                                            reciept_num = receipt,
                                            delivery_address = address,
                                            delivery_phone = phone)
        customercheckout_order_instance.save()
        customercheckout = CustomerCheckout.objects.get(id = customercheckout_order_instance.id)
        for item in usercart:
            orderedproduct_instance = customerPayedProducts(customer = request.user,
                                                            product_name = item.product.product_name,
                                                            price = item.product.price,
                                                            product_description = item.product.product_description,
                                                            checkout_details = customercheckout)
            orderedproduct_instance.save()
                                                            
        context = {'order_id' : order_details.get('id'),
                    'amount' : totalprice,
                    'amountscript' : totalprice*100,
                    'currency' : 'INR',
                    'companyname' : 'Mashupcommrz',
                    'username' : request.user.first_name+' '+request.user.last_name,
                    'useremail' : request.user.email,
                    'phonenum' : phone,
                    'rzpkey' : 'rzp_test_bAYqeZhjXN8pf0'
                    }
        return render(request,'customer/checkoutform.html',context)
    else:
      return HttpResponseRedirect(reverse('products'))  

@csrf_exempt
@login_required(login_url = reverse_lazy('logincustomer'))
def markpaymentsuccess(request):
    if request.is_ajax():
        order_id = request.POST['order_id']
        payment_id = request.POST['payment_id']
        payment_signature = request.POST['payment_signature']
        user = request.user
        customercart_order_instance = CustomerCheckout.objects.get(order_id = order_id,
                                                                customer=user)
        customercart_order_instance.payment_signature = payment_signature
        customercart_order_instance.payment_id = payment_id
        customercart_order_instance.payment_complete = 1
        customercart_order_instance.save()
        customercart_instance = CustomerCart.objects.filter(customer = user)
        customercart_instance.delete()
        return JsonResponse({'result':'success'})


    
  
