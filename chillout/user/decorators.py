from django.views.generic import View
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import (login_required, permission_required,
                                            user_passes_test)


def require_authenticated_permission(*perms):
    def wrapper(cls):
        if not isinstance(cls, type) or not issubclass(cls, View):
            raise ImproperlyConfigured('{} class must be subclass of View class'
                                       .format(cls.__name__))
        check_login = method_decorator(login_required)
        check_perms = method_decorator(permission_required(perms,
            raise_exception=True))
        cls.dispatch = check_login(check_perms(cls.dispatch))
        return cls
    return wrapper


def class_login_required(cls):
    if not isinstance(cls, type) or not issubclass(cls, View):
        raise ImproperlyConfigured('{} class must be subclass of View class'
                                   .format(cls.__name__))
    check_login = method_decorator(login_required)
    cls.dispatch = check_login(cls.dispatch)
    return cls


def staff_only(func):
    
    def check_is_staff(user):
        if user.is_staff:
            return True
        else:
            raise PermissionDenied()

    return user_passes_test(check_is_staff)(func)


def class_staff_only(cls):
    if not isinstance(cls, type) or not issubclass(cls, View):
        raise ImproperlyConfigured('{} class must be subclass of View class'
                                   .format(cls.__name__))
    check_login = method_decorator(login_required)
    check_is_staff = method_decorator(staff_only)
    cls.dispatch = check_login(check_is_staff(cls.dispatch))
    return cls


def superuser_only(func):
    
    def check_is_superuser(user):
        if user.is_superuser:
            return True
        else:
            raise PermissionDenied()

    return user_passes_test(check_is_superuser)(func)


def class_superuser_only(cls):
    if not isinstance(cls, type) or not issubclass(cls, View):
        raise ImproperlyConfigured('{} class must be subclass of View class'
                                   .format(cls.__name__))
    check_login = method_decorator(login_required)
    check_is_superuser = method_decorator(superuser_only)
    cls.dispatch = check_login(check_is_superuser(cls.dispatch))
    return cls