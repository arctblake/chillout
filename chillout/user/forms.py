from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.core.exceptions import ValidationError

from .models import User, Profile
from .form_utils import ActivationMailFormMixin


class UserCreationForm(ActivationMailFormMixin, BaseUserCreationForm):

    error_message = ('Inactive user created. Cound not send activation email. '
                     'Try "Resend activation email" some time later.')

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    tel = forms.CharField(max_length=30)
    address = forms.CharField(max_length=300)
    
    class Meta(BaseUserCreationForm.Meta):
        
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2',
                  'tel', 'address')
    
    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        for i in first_name:
            if i in '0123456789':
                raise ValidationError('First name cannot contain digits.')
        return first_name.title()
    
    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        for i in last_name:
            if i in '0123456789':
                raise ValidationError('Last name cannot contain digits.')
        if '-' in last_name:
            temp = last_name.split('-')
            last_name = '-'.join(part.title() for part in temp)
        return last_name
    
    def clean_tel(self):
        tel = self.cleaned_data['tel']
        tel = ''.join(i for i in tel if i in '0123456789')
        return tel
    
    def save(self, request):
        user = super().save(commit=False)
        if user.pk:
            need_send_mail = False
        else:
            need_send_mail = True
            user.is_active = False
        user.save()
        self.save_m2m()
        
        Profile.objects.update_or_create(user=user,
            defaults={'slug': 'id{}'.format(user.pk),
                      'first_name': self.cleaned_data['first_name'],
                      'last_name': self.cleaned_data['last_name'],
                      'tel': self.cleaned_data['tel'],
                      'address': self.cleaned_data['address']})
        
        if need_send_mail:
            self.send_mail(user, request)
        
        return user

    def get_context_data(self, user, request, context=None):
        context = super().get_context_data(user, request, context)
        context.update({'domain': '127.0.0.1:8000'})
        return context


class ResendActivationEmailForm(ActivationMailFormMixin, forms.Form):
    
    error_message = 'Could not resend activation email. Try again later.'
    
    email = forms.EmailField()

    def save(self, request):
        User = get_user_model()
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email__iexact=email)
            if user.is_active:
                self.add_error(None, ValidationError('User with email {} '
                    'is already activated.'.format(email)))
                return None
        except User.DoesNotExist:
            self.add_error(None,
                ValidationError('No user with email {}.'.format(email)))
            return None

        self.send_mail(user, request)
        return user

    def get_context_data(self, user, request, context=None):
        context = super().get_context_data(user, request, context)
        context.update({'domain': '127.0.0.1:8000'})
        return context