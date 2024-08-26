from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from .models import User, Address


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='گذرواژه', widget=forms.PasswordInput)
    password2 = forms.CharField(label='تایید گذرواژه', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_number',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('phone_number', 'fullname', 'email', 'password', 'is_active', 'is_admin')


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_phone(self):
        username = self.cleaned_data.get('phone')
        if len(username) > 11:
            raise ValidationError(
                'invalid value: %(value)s is not valid',
                code='validation',
                params={'value': f'{username}'}
            )


class RegisterForm(forms.Form):
    fullname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class AddressCreationForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ('user', 'is_active')
        widgets = {
            'address': forms.Textarea(attrs={"id": "address", "class": "form-control", 'style': 'resize:none;', 'rows': 2}),
            'phone': forms.TextInput(attrs={"id": "tel", "class": "form-control"}),
            'postal_code': forms.TextInput(attrs={"id": "postal_code", "class": "form-control"}),
            'receiver': forms.TextInput(attrs={"id": "receiver", "class": "form-control"}),
        }

    def __init__(self, user, *args, **kwargs):
        super(AddressCreationForm, self).__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        # Set the user before saving
        instance = super(AddressCreationForm, self).save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance
