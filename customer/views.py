from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User, auth

from admins.models import Products
from .models import CustomerCart
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

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
    
  
