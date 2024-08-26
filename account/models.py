from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .validators import validate_phone_number


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None):

        if not phone_number:
            raise ValueError('Users must have a phone number')

        user = self.model(
            phone_number=self.normalize_email(phone_number),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None):
        user = self.create_user(
            phone_number,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='آدرس ایمیل',
        max_length=255,
        null=True,
        blank=True,
        unique=True,
    )
    fullname = models.CharField(max_length=50, null=True, blank=True, verbose_name='نام کامل')
    phone_number = models.CharField(max_length=12, unique=True,validators=[validate_phone_number], verbose_name='شماره همراه')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_admin = models.BooleanField(default=False, verbose_name='ادمین')

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربرها'

    def __str__(self):
        return self.phone_number

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='کاربر')
    receiver = models.CharField(max_length=127, verbose_name='تحویل گیرنده')
    phone = models.CharField(max_length=11, verbose_name='شماره تماس', validators=[validate_phone_number])
    address = models.TextField(verbose_name='نشانی کامل')
    postal_code = models.CharField(max_length=10, verbose_name='کد پستی')
    is_active = models.BooleanField(default=True, verbose_name='آدرس فعال')

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس ها"
        ordering = ['-is_active']

    def __str__(self):
        return self.postal_code


@receiver(post_save, sender=Address)
def deactivate_other_addresses(sender, instance, **kwargs):
    if instance.is_active:
        Address.objects.exclude(pk=instance.pk, user=instance.user).update(is_active=False)


@receiver(pre_delete, sender=Address)
def activate_last_address(sender, instance, **kwargs):
    if instance.is_active:
        # If the deleted address was active, activate the last one (if exists)
        last_address = Address.objects.filter(user=instance.user).exclude(pk=instance.pk).last()
        if last_address:
            last_address.is_active = True
            last_address.save()
