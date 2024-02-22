from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Product
from category.models import Category
from carts.views import _cart_id, CartItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

def getPaginator(request, products):
    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    paged_product = paginator.get_page(page)
    return paged_product    

def store(request, category_slug=None):
    categories = None
    products = None
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paged_product = getPaginator(request, products)
        products_count = products.count()
    else:  
        products = Product.objects.all().filter(is_available=True)
        paged_product = getPaginator(request, products)
        products_count = products.count()
    
    context = {
        'products': paged_product,
        'products_count': products_count
    }
    
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        
    except Exception as err:
        raise err
    
    context = {
        'single_product': single_product,
        "in_cart": in_cart
    }
    
    return render(request, 'store/product_detail.html', context)
