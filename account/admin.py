from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserCreationForm, UserChangeForm
from account.models import User, Address


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('phone_number', 'fullname', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = [
        ("اطلاعات ورود به حساب", {"fields": ["phone_number", "password"]}),
        ("اطلاعات شخصی", {"fields": ["fullname", "email"]}),
        ("دسترسی ها", {"fields": ["is_admin", 'groups', 'user_permissions']})]
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'fullname', 'password1', 'password2'),
        }),
    )
    search_fields = ('phone_number',)
    ordering = ('phone_number',)
    filter_horizontal = ()


admin.site.register(Address)
admin.site.register(User, UserAdmin)

