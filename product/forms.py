from django import forms
from product.models import Category


class ProductFilterForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), required=False,
                                                widget=forms.CheckboxSelectMultiple())
    min_price = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    max_price = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    available = forms.BooleanField(required=False, label='فقط کالاهای موجود')

