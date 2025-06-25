from django.contrib.auth.decorators import user_passes_test

def superuser_required(function=None):
    return user_passes_test(lambda u: u.is_superuser, login_url='/') (function)
