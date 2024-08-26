from django.core.exceptions import ValidationError


def validate_phone_number(value):
    if not (value.isdigit() and len(value) == 11 and value.startswith('09')):
        raise ValidationError('لطفا یک شماره موبایل معتبر وارد کنید',
                              code="invalid_phone_number")

