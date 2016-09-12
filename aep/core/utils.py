from django.utils.crypto import get_random_string


def make_AEP_ID():
    return get_random_string(length=8, allowed_chars='0123456789')


def make_slug():
    return get_random_string(length=5)
