from urllib.parse import urlencode

from django.core import paginator
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView

from product.forms import ProductFilterForm
from product.models import Product, Category

PRODUCT_MODEL = Product


class ProductDetailView(DetailView):
    template_name = "product/product_detail.html"
    model = Product


class ProductListView(ListView):
    model = PRODUCT_MODEL
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    paginate_by = 6
    form_class = ProductFilterForm

    def dispatch(self, request, *args, **kwargs):
        self.ordering = request.GET.get('ordering')
        self.search_query = None
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        template_name = super(ProductListView, self).get_template_names()
        if self.ordering:
            template_name = 'product/Product_list.html'
        return template_name

    def get_queryset(self):
        queryset = PRODUCT_MODEL.objects.all()
        form = self.get_form()
        if form.is_valid():
            cleaned_data = form.cleaned_data
            filter_data = {}
            if cleaned_data.get('available'):
                filter_data['stock__gt'] = 0
            if cleaned_data.get('min_price'):
                filter_data['price__gte'] = cleaned_data['min_price']
            if cleaned_data.get('max_price'):
                filter_data['price__lte'] = cleaned_data['max_price']
            if cleaned_data.get('categories'):
                filter_data['categories__in'] = cleaned_data['categories']
            if filter_data:
                queryset = queryset.filter(**filter_data)
        return self.product_list_ordering(queryset, self.ordering)

    @staticmethod
    def product_list_ordering(queryset, ordering):
        match ordering:
            case 'most-expensive':
                queryset = queryset.order_by('-stock', '-price')
            case 'cheapest':
                queryset = queryset.order_by('-stock', 'price')
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super(ProductListView, self).get_context_data()
        form = self.get_form()
        query_string = self.construct_query_string(form)
        context_updates = {
            'page_hero_title': 'تمام محصولات',
            'page_hero_description': 'تمام محصولات روبیک مارکت',
            'page_hero_current': 'محصولات',
            'ordering': self.request.GET.get('ordering'),
            'product_count': self.get_queryset().count(),
            'form': form,
            'query_string': "&" + query_string if query_string else ''
        }
        context.update(context_updates)
        return context

    def get_form(self):
        return self.form_class(self.request.GET)

    def construct_query_string(self, form):
        query_params = self.request.GET.copy()
        if query_params.get('ordering'):
            del query_params['ordering']
        if query_params.get('page'):
            del query_params['page']
        return urlencode(query_params)


def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)

    return render(request, 'product/Category_list.html', {
        'category': category,
        'products': products,
    })


class SearchProductListView(ProductListView):
    def get_queryset(self):
        self.search_query = self.request.GET.get('q')
        queryset = super().get_queryset().filter(title__icontains=self.search_query)
        ordering = self.request.GET.get('ordering')

        return self.product_list_ordering(queryset, ordering)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['page_hero_title'] = f'نتایج جستجو برای "{self.search_query}"'
        context['page_hero_description'] = ''
        context['page_hero_mid'] = 'تمام محصولات'
        context['page_hero_current'] = "جستجو"
        print(context['query_string'])
        return context
