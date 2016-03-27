from smtplib import SMTPException

from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site


class ActivationMailFormMixin:
    
    activation_email_template = 'user/activation_email.txt'
    error_message = ''
    
    @property
    def mail_sent(self):
        if hasattr(self, '_mail_sent'):
            return self._mail_sent
        return False
    
    def get_message(self, context):
        return render_to_string(self.activation_email_template, context)
    
    def get_context_data(self, user, request, context=None):
        if context is None:
            context = {}
        current_site = get_current_site(request)
        protocol = 'https' if request.is_secure() else 'http'
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        context.update({'site_name': current_site.name, 'protocol': protocol,
                        'domain': current_site.domain, 'uid': uid,
                        'token': token})
        return context
    
    def _send_mail(self, user, request):
        context = self.get_context_data(user, request)
        mail_kwargs = {
            'subject': '[Chill-out] Account Activation',
            'message': self.get_message(context),
            'from_email': settings.DEFAULT_FROM_EMAIL,
            'recipient_list': [user.email]
        }
        
        try:
            number_sent = send_mail(**mail_kwargs)
        except Exception as error:
            if isinstance(error, BadHeaderError):
                err_code = 'badheader'
            elif isinstance(error, SMTPException):
                err_code = 'smtperror'
            else:
                err_code = 'unexpectederror'
            return (False, err_code)
        else:
            if number_sent > 0:
                return (True, None)
        return (False, 'unknownerror')
    
    def send_mail(self, user, request):
        self._mail_sent, error = self._send_mail(user, request)
        if not self.mail_sent:
            self.add_error(None, ValidationError(self.error_message,
                                                 code=error))
        return self.mail_sent