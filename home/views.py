from django.db.models import Prefetch, Case, Value, When, IntegerField
from django.shortcuts import render
from django.views.generic import TemplateView
from product.models import Product


class Home(TemplateView):
    template_name = 'home/index.html'


