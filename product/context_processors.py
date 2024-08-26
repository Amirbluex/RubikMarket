from product.models import Product, Category
from django.core.paginator import Paginator


def categories_processor(request):
    categories = Category.objects.all()
    return {'categories': categories}


def recent_product(request):
    recent_products = Product.objects.all()
    return {'recent_products': recent_products}


def paginate_product(request):
    products = Product.objects.all()
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return {'page_obj': page_obj}

