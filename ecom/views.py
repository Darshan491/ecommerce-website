from django.shortcuts import redirect, render
from ecom.form import CustomUserForm
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse
import json


def search_venue(request):
    if request.method == "POST":
        searched = request.POST.get('searched')
        venues = Product.objects.filter(name__icontains=searched)
        return render(request, "ecom_pikachu/search_venue.html", {'searched': searched, 'venues': venues})
    else:  # GET request
        return render(request, "ecom_pikachu/search_venue.html")



def home(request):
    products = Product.objects.filter(trending=1)
    return render(request,"ecom_pikachu/index.html",{"products":products})


def remove_cart(request,cid):
    cartitem=Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect('/cart')

def cart_page(request):
    if request.user.is_authenticated:
        cart=Cart.objects.filter(user=request.user)
        return render(request,"ecom_pikachu/cart.html",{"cart":cart})
    else:
        return redirect("/")

def add_to_cart(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            product_qty=data['product_qty']
            product_id=data['pid']
            product_status=Product.objects.get(id=product_id)
            if product_status:
                if Cart.objects.filter(user=request.user.id,product_id=product_id):
                    return JsonResponse({'status': 'Product Already in Card'}, status=200)
                else:
                    if product_status.quantity>=product_qty:
                        Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
                        return JsonResponse({'status': 'Product Added to Card'}, status=200)
                    else:
                        return JsonResponse({'status':'Product Stock Not Available'}, status=200)
        else:
            return JsonResponse({'status': 'Login to Add Cart'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)


def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logout success")
    return redirect("/")

def login_page(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method=='POST':
            name=request.POST.get('username')
            pwd=request.POST.get('password')
            user=authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                messages.success(request,"Logged in successfully")
                return redirect("/")
            else:
                messages.error(request,"Invalid username or password")
                return redirect("/login")
        return render(request,"ecom_pikachu/login.html")

def signup(request):
    form=CustomUserForm()
    if request.method=='POST':
        form=CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registration success you can Login Now!")
            return redirect('/login')
    return render(request,"ecom_pikachu/signup.html",{'form':form})

def collections(request):
    category = Category.objects.filter(status=0)
    return render(request,"ecom_pikachu/collections.html",{"category":category})

def collectionsview(request,name):
    if(Category.objects.filter(name=name,status=0)):
        products=Product.objects.filter(Category__name=name)
        return render(request,"ecom_pikachu/products/index.html",{"products":products,"category_name":name})
    else:
        messages.warning(request,"No such category found")
        return redirect('collections')

def product_details(request,cname,pname):
    if(Category.objects.filter(name=cname,status=0)):
        if(Product.objects.filter(name=pname,status=0)):
            products=Product.objects.filter(name=pname,status=0).first()
            return render(request,"ecom_pikachu/products/product_details.html",{"products":products})
        else:
            messages.error(request,"No such category found")
            return redirect('collections')
    else:
        messages.error(request,"No such category found")
        return redirect('collections')
