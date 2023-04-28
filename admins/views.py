from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import LoginForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .models import Products
from django.contrib import messages

from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy, reverse

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import os




# Create your views here.
def checksuperuser(user):
    return user.is_superuser


@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))
def logoutadmin(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))
def admindashboard(request):
    return render(request,'adminpannel/admindashboard.html',{})


def loginadmin(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admindashboard') )
    else:	
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data['username']
                password = login_form.cleaned_data['password']

                user = authenticate(username=username, password=password)
                                
                if user is not None:
                    if user.is_active and user.is_superuser:
                        login(request,user)	
                        return HttpResponseRedirect(reverse('admindashboard') )
                    else:
                        return HttpResponse('Your account is not active')
                else:
                    return HttpResponse('The Account does not exists')
            else:
                login_form = LoginForm()
                return render(request, "adminpannel/login.html",{"form":login_form})
        else:
            login_form = LoginForm()
        return render(request,'adminpannel/login.html',{"form":login_form})
    
    



@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))  
def addproduct(request):
    return render(request,'adminpannel/addproduct.html') 


    
@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))    
def manageproducts(request):
    products = Products.objects.all()
    return render(request,'adminpannel/manageproducts.html',{'products':products})



@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))  
def addproduct(request):
    if request.method == 'POST':
            product_name = request.POST['product_name']
            product_description = request.POST['product_description']
            price = request.POST['price']
            product_image = request.FILES['product_image']

            product_instance = Products(product_name = product_name, 
                                        product_description = product_description,
                                        price = price,
                                        product_picture = product_image)
            product_instance.save()
            # messages.success(request, "Producted added successfully")
            return redirect('/manage-products')
           
    else:  
        return render(request,'adminpannel/addproduct.html')


@csrf_exempt
@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))
def changestatus(request):
    if request.is_ajax():
        product_id = int(request.POST['product'])
        action = request.POST['action']
        product_instance = Products.objects.get(id=product_id)
        if action == "disable":
            product_instance.is_active = 0
        else:
            product_instance.is_active = 1
        product_instance.save()
        return JsonResponse({'result':'success'})
   
@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))
def editproduct(request, product_id):
    if request.method == 'POST':
        name = request.POST['product_name']
        description = request.POST['product_description']
        price =  request.POST['price']
        
        
    
        
       
        
        product_instance = Products.objects.get(id=product_id)
            
        product_instance.product_name =  name
        product_instance.product_description = description
        product_instance.price = price
        if request.FILES:
            product_image = request.FILES['product_image']
            product_instance.product_picture = product_image
        product_instance.save()
        messages.success(request,"Product updated successfully")
        return HttpResponseRedirect(reverse('manageproducts')) 
        
    else:
        product_instance = Products.objects.get(id= product_id)
        return render(request, 'adminpannel\editproduct.html', {'productform':product_instance})
    

    
@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))    
def deleteproduct(request, product_id):
    product_instance = Products.objects.get(id = product_id)
    product_instance.delete()
    return HttpResponseRedirect(reverse('manageproducts'))
        
            
   
       
        



    