from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.views.generic import DetailView, ListView

from .models import User, Address
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import View
from .forms import LoginForm, RegisterForm, AddressCreationForm
from django.contrib.auth import login, authenticate, logout

from order.models import Order


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        last_order = Order.objects.filter(
            user=request.user,
            is_paid=True
        ).only('total_price', 'payment_date',
               'status', 'post_code').prefetch_related('items').order_by('-payment_date').first()
        context = {
            'last_order': last_order,
        }
        return render(request, 'account/Profile.html', context)


class UserLogin(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "account/Login.html", {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                form.add_error('username', 'اطلاعات نامعتبر')
        else:
            form.add_error('password', 'اطلاعات نامعتبر')
        return render(request, "account/Login.html", {'form': form})


def user_logout(request):
    logout(request)
    return redirect("/")


class UserRegister(View):
    def get(self, request):
        form = RegisterForm
        return render(request, "account/Register.html", {'form': form})

    def post(self, request):
        context = {'errors': []}

        if request.user.is_authenticated:
            return redirect('home:home')

        if request.method == "POST":
            fullname = request.POST.get('fullname')
            phone_number = request.POST.get('phone_number')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 != password2:
                context['errors'].append('Passwords are not match')
                return render(request, "account/Register.html", context)

            user = User.objects.create_user(fullname=fullname, password=password1, phone_number=phone_number)
            login(request, user)
        return redirect('home:home')


class UserOrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'account/Factor.html'
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset.filter(user=self.request.user, is_paid=True).order_by('-payment_date')
        return queryset


class AddressListCreationView(LoginRequiredMixin, View):
    def get(self, request):
        form = AddressCreationForm(user=request.user)
        addresses = Address.objects.filter(user=request.user)

        return render(request, 'account/Addresses.html', {'form': form, 'addresses': addresses})

    def post(self, request):
        form = AddressCreationForm(data=request.POST, user=request.user)
        addresses = Address.objects.filter(user=request.user)
        user_address_count = Address.objects.filter(user=request.user).count()
        try:
            if user_address_count >= 5:
                raise ValidationError("نمی توانید بیش از 5 آدرس ثبت کنید")
            if form.is_valid():
                address = form.save(commit=False)
                address.user = request.user
                address.save()
        except:
            form.add_error(None, "نمی توانید بیش از 5 آدرس ثبت کنید")

        next_page = request.POST.get('next')
        if next_page:
            return redirect(next_page)

        return render(request, 'account/Addresses.html', {'form': form, 'addresses': addresses})


class AddressDelete(LoginRequiredMixin, View):
    def get(self, request, pk):
        address = get_object_or_404(Address, pk=pk)
        address.delete()

        return redirect('accounts:add_list_address')


class AddressSetActive(LoginRequiredMixin, View):
    def get(self, request, pk):
        address = get_object_or_404(Address, pk=pk)
        address.is_active = True
        address.save()

        return redirect('accounts:add_list_address')

