from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        BaseUserManager)

from menu.models import Dish


class UserManager(BaseUserManager):
    
    use_in_migrations = True
    
    def _create_user(self, email, password, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password):
        return self._create_user(email, password)
    
    def create_superuser(self, email, password):
        return self._create_user(email, password, is_staff=True,
                                 is_superuser=True)

    def get(self, *args, **kwargs):
        return (self.get_queryset().select_related('profile')
                .get(*args, **kwargs))


class User(AbstractBaseUser, PermissionsMixin):
    
    objects = UserManager()
    
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    
    def get_absolute_url(self):
        return self.profile.get_absolute_url()
    
    def get_full_name(self):
        return self.profile.get_full_name()
    
    def get_short_name(self):
        return self.profile.get_short_name()


class Profile(models.Model):
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    
    slug = models.SlugField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    tel = models.CharField(max_length=30)
    address = models.CharField(max_length=300)
    bonus = models.SmallIntegerField(default=10)
    joined = models.DateField(auto_now_add=True)
    
    class Meta:
        
        ordering = ['-joined']
    
    def __str__(self):
        return self.get_full_name() + ' | ' + self.slug
    
    def get_absolute_url(self):
        return reverse('profile_detail', kwargs={'slug': self.slug})
    
    def get_full_name(self):
        return self.first_name + ' ' + self.last_name
    
    def get_short_name(self):
        return self.first_name
    
    def get_truncated_first_name(self):
        if len(self.first_name) > 11:
            return self.first_name[:11] + '...'
        return self.first_name
    
    def get_truncated_last_name(self):
        if len(self.last_name) > 11:
            return self.last_name[:11] + '...'
        return self.last_name
    
    def get_number_of_active_notifications(self):
        amount = self.notifications.filter(is_active=True).count()
        return amount
    
    def get_own_dishes(self):
        return Dish.objects.filter(belongs_to=self.slug)