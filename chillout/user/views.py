import datetime

from django.conf import settings
from django.utils import timezone
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View, DetailView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.contrib.messages import success, error
from django.template.response import TemplateResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from .forms import UserCreationForm, ResendActivationEmailForm
from .models import Profile
from main.models import Order, Notification, PagesData
from menu.models import Dish, Category
from user.decorators import class_staff_only, class_login_required


class Registration(View):
    
    form_class = UserCreationForm
    template_name = 'user/registration_form.html'
    
    @method_decorator(csrf_protect)
    def get(self, request):
        return render(request, self.template_name,
                      {'form': self.form_class(),
                       'form_login': AuthenticationForm(request)})
    
    @method_decorator(csrf_protect)
    @method_decorator(sensitive_post_parameters('password1', 'password2'))
    def post(self, request):
        bound_form = self.form_class(request.POST)
        if bound_form.is_valid():
            bound_form.save(request)
            if bound_form.mail_sent:
                success(request, 'Activation email was successfully sent. '
                        'Check your email account.')
            else:
                for err in bound_form.non_field_errors():
                    error(request, err)
            return redirect('main_page')
        return TemplateResponse(request, self.template_name,
                                {'form': bound_form,
                                 'form_login': AuthenticationForm(request)})


class ActivateAccount(View):
    
    @method_decorator(never_cache)
    def get(self, request, uid64, token):
        User = get_user_model()
        try:
            pk = force_text(urlsafe_base64_decode(uid64))
            user = User.objects.get(pk=pk)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if (user is not None and default_token_generator.check_token(user,
                                                                     token)):
            user.is_active = True
            user.save()
            return redirect(settings.LOGIN_URL)
        else:
            error(request, 'This activation link is no longer valid. '
                  'Try "Resend activation email".')
            return redirect('main_page')


class ResendActivationEmail(View):

    form_class = ResendActivationEmailForm
    template_name = 'user/resend_activation_form.html'

    @method_decorator(csrf_protect)
    def get(self, request):
        return TemplateResponse(request, self.template_name,
                                {'form': self.form_class()})

    @method_decorator(csrf_protect)
    def post(self, request):
        bound_form = self.form_class(request.POST)
        if bound_form.is_valid():
            user = bound_form.save(request)
            if user is not None and not bound_form.mail_sent:
                for err in bound_form.non_field_errors():
                    error(request, err)
            elif user is not None and bound_form.mail_sent:
                success(request, 'Activation email sent. '
                        'Check your email account.')
            return redirect('main_page')
        return TemplateResponse(request, self.template_name,
                                {'form': bound_form})


@class_login_required
class ProfileDetail(View):
    
    def get(self, request):
        data_obj = PagesData.objects.get(pk=1)
        notification_list = None
        now = None
        dish_list = None
        if request.user.is_staff:
            now = timezone.now()
            tz = datetime.timezone(datetime.timedelta(hours=8))
            today_midnight = datetime.datetime(now.year, now.month, now.day,
                                               tzinfo=tz)
            notifications = list(Notification.objects.filter(
                date_time__gte=today_midnight))
            notification_list = []
            for notif in notifications:
                name, tel, other = notif.details.split('***', 2)
                notification_list.append(
                    {'css_class': 'active' if notif.is_active else 'inactive',
                     'from': name, 'tel': tel, 'date_time': notif.date_time,
                     'href': notif.pk}
                )
            
            dish_list = Dish.objects.filter(belongs_to='id1')
        
        order_dates = None
        category_list = None
        if request.user.is_superuser:
            order_dates = Order.objects.dates('made_on', 'year')
            category_list = Category.objects.all()

        return render(request, 'user/profile_detail.html',
                      {'profile': request.user.profile,
                       'show_bonus': data_obj.profile_page_show_bonus,
                       'notification_list': notification_list,
                       'now': now,
                       'dish_list': dish_list,
                       'order_dates': order_dates,
                       'category_list': category_list})


@class_staff_only
class NN(View):
    
    def get(self, request):
        since = request.GET.get('since')
        notification_list = []
        if since is not None:
            t, dt = since.split()
            h, m = t.split(':')
            d, mnth, y = dt.split('.')
            mnth = mnth.lstrip('0')
            d = d.lstrip('0')
            h = h.lstrip('0') if h != '00' else '0'
            m = m.lstrip('0') if m != '00' else '0'
            tz = datetime.timezone(datetime.timedelta(hours=8))
            since = datetime.datetime(int(y), int(mnth), int(d), int(h), int(m),
                                      tzinfo=tz)
            new_notifications = list(
                Notification.objects.filter(date_time__gte=since)
            )
            notification_list = []
            for notif in new_notifications:
                local_date = notif.date_time + datetime.timedelta(hours=8)
                h = (local_date.hour if local_date.hour >= 10 else
                     '0' + str(local_date.hour))
                m = (local_date.minute if local_date.minute >= 10 else
                     '0' + str(local_date.minute))
                d = (local_date.day if local_date.day >= 10 else
                     '0' + str(local_date.day))
                mnth = (local_date.month if local_date.month >= 10
                        else '0' + str(local_date.month))
                y = local_date.year
                name, tel, other = notif.details.split('***', 2)
                notification_list.append(
                    {'css_class': 'active' if notif.is_active else 'inactive',
                     'from': name, 'tel': tel, 'href': notif.pk,
                     'date_time': '{}:{} {}.{}.{}'.format(h, m, d, mnth, y)}
                )

        pks = request.GET.get('pks')
        inactive_notifications = []
        deleted_notifications = []
        if pks:
            pk_list = [int(pk) for pk in pks.split('.')]
            all_notifications = list(Notification.objects.filter(
                pk__in=pk_list))
            new_pk_list = [notif.pk for notif in all_notifications]
            for pk in pk_list:
                if pk not in new_pk_list:
                    deleted_notifications.append(pk)
            
            inactive_notifications = [notif.pk for notif in all_notifications
                                      if not notif.is_active]

        amount = Notification.objects.filter(is_active=True).count()
        return JsonResponse({'new': amount, 'notifications': notification_list,
                             'inactive': inactive_notifications,
                             'deleted': deleted_notifications})