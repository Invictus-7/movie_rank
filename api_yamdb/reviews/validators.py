import re
from datetime import date

from django.core.exceptions import ValidationError

from api_yamdb.settings import USERNAME_REGEX

NOT_ALLOWED_CHAR_MSG = '{chars} недопустимые символы в имени пользователя.'
NOT_ALLOWED_ME_MSG = (
    'Регистрация с ником "me" запрещена, придумайте другой логин.'
)
NOT_ALLOWED_YEAR_MSG = (
    'Год выпуска произведения не должен быть позже текущего года: {year}.'
)


def validate_username(value):
    if not re.compile(USERNAME_REGEX).match(value):
        raise ValidationError(
            NOT_ALLOWED_CHAR_MSG.format(
                chars=''.join(set(re.sub(USERNAME_REGEX, '', value)))
            )
        )
    if value == 'me':
        raise ValidationError(NOT_ALLOWED_ME_MSG)
    return value


def validate_year(value):
    year = date.today().year
    if value > year:
        raise ValidationError(NOT_ALLOWED_YEAR_MSG.format(year=year))
    return value
