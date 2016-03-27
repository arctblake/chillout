import calendar

from django.conf import settings
from django.db.models import Prefetch
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, resolve_url, redirect
from django.views.generic import View, ListView
from django.utils.http import is_safe_url
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import deprecate_current_app
from django.contrib.messages import success, error

from .models import Order, Notification, PagesData
from menu.models import Dish, Category
from user.models import Profile
from user.decorators import class_staff_only, class_superuser_only


class MainPage(View):

    @method_decorator(csrf_protect)
    def get(self, request):
        data_obj = PagesData.objects.get(pk=1)
        return render(request, 'main/main_page.html',
                      {'offer': data_obj.main_page_offer,
                       'offer_text': data_obj.main_page_offer_text})
    
    @method_decorator(deprecate_current_app)
    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def post(self, request):
        redirect_to = request.POST.get('next')
        bound_form = AuthenticationForm(request, data=request.POST)
        if bound_form.is_valid():
            if redirect_to is not None:
                if not is_safe_url(url=redirect_to, host=request.get_host()):
                    redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            else:
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            login(request, bound_form.get_user())

            return HttpResponseRedirect(redirect_to)
        
        error(request, 'Ошибка авторизации, попробуйте ещё раз.')
        data_obj = PagesData.objects.get(pk=1)
        return render(request, 'main/main_page.html',
                      {'offer': data_obj.main_page_offer,
                       'offer_text': data_obj.main_page_offer_text})


class ProfileData(View):
    
    def get(self, request):
        if request.user.is_authenticated():
            profile = request.user.profile
            return JsonResponse({'name': profile.get_full_name(),
                                 'tel': profile.tel,
                                 'address': profile.address})
        return JsonResponse({})


class MakeOrder(View):
    
    def post(self, request):
        basket = {key: value for key, value in request.POST.items()
                  if key != 'csrfmiddlewaretoken'}
        name = basket.pop('name')
        tel = basket.pop('tel')
        address = basket.pop('address')
        comment = basket.pop('comment')
        delivery_time = basket.pop('delivery_time')
        payment_by = basket.pop('payment_by')
        
        if not comment: comment = 'Empty'
        if not delivery_time: delivery_time = 'Empty'
        
        dishes = ''
        anon_dishes = ''
        slug_list = []
        for key, value in basket.items():
            if key.startswith('anonimous'):
                anon_dishes += value + ';'
            else:
                dishes += key + '|' + value + ';'
                slug_list.append(key)
        
        dish_list = list(Dish.objects.filter(slug__in=slug_list))
        for dish in dish_list:
            dish.popularity += 1
            dish.save()

        order = Order.objects.create(dishes=dishes.rstrip(';'),
                                     anon_dishes=anon_dishes.rstrip(';'))
        if request.user.is_authenticated():
            order.made_by = request.user.profile
            order.save()
        
        details = '{}***{}***{}***{}***{}***{}'.format(name, tel, address,
            comment, delivery_time, payment_by)

        Notification.objects.create(details=details, order=order).profiles.add(
            *Profile.objects.filter(user__is_staff=True))
        
        success(request, 'Ваша заявка принята на обработку. В ближайшее '
                'время ожидайте звонка с подтверждением. Спасибо за заказ!')
        return redirect('main_page')


@class_staff_only
class NotificationDetail(View):
    
    def get_object(self, pk):
        queryset = Notification.objects.filter(pk=pk).select_related('order')
        try:
            notification = queryset.get()
        except Notification.DoesNotExist:
            raise Http404()
        return notification

    def get(self, request, pk):
        notification = self.get_object(pk)
        add_serving = False
        if not notification.is_active: add_serving = True
        notification.is_active = False
        notification.save()
        info = dict(zip(
            ('name','tel','address','comment','delivery_time','payment_by'),
            notification.details.split('***')
        ))
        
        if info['comment'] == 'Empty': info['comment'] = ''
        if info['delivery_time'] == 'Empty': info['delivery_time'] = ''

        dish_list = (notification.order.get_dish_objects +
                     notification.order.get_anon_dish_objects)
        
        total = notification.order.get_total()
        
        response_dict = {'info': info, 'dishes': dish_list, 'total': total}
        if add_serving:
            response_dict['serving'] = 'serving'

        return JsonResponse(response_dict)

    def post(self, request, pk):
        notification = self.get_object(pk)
        basket = {key: value for key, value in request.POST.items()
                  if key != 'csrfmiddlewaretoken'}
        action = 'delete' if request.GET.get('action') == 'delete' else 'edit'
        if action == 'edit':
            name = basket.pop('name')
            tel = basket.pop('tel')
            address = basket.pop('address')
            comment = basket.pop('comment')
            delivery_time = basket.pop('delivery_time')
            payment_by = basket.pop('payment_by')
            
            if not comment: comment = 'Empty'
            if not delivery_time: delivery_time = 'Empty'
            
            old_slug_list = [dish['slug']
                             for dish in notification.order.get_dish_objects]
        
            dishes = ''
            anon_dishes = ''
            slug_list = []
            for key, value in basket.items():
                if key.startswith('anonimous'):
                    anon_dishes += value + ';'
                else:
                    dishes += key + '|' + value + ';'
                    slug_list.append(key)
            
            new_slugs = [slug for slug in slug_list
                         if slug not in old_slug_list]
            del_slugs = [slug for slug in old_slug_list
                         if slug not in slug_list]
            
            if del_slugs:
                del_dish_list = list(Dish.objects.filter(slug__in=del_slugs))
                for dish in del_dish_list:
                    dish.popularity -= 1
                    dish.save()
            
            if new_slugs:
                new_dish_list = list(Dish.objects.filter(slug__in=new_slugs))
                for dish in new_dish_list:
                    dish.popularity += 1
                    dish.save()
            
            details = '{}***{}***{}***{}***{}***{}'.format(name, tel, address,
                comment, delivery_time, payment_by)
            
            notification.details = details
            notification.order.dishes = dishes.rstrip(';')
            notification.order.anon_dishes = anon_dishes.rstrip(';')
            notification.order.save()
            notification.save()
        else:
            slug_list = [dish['slug']
                         for dish in notification.order.get_dish_objects]
            dish_list = list(Dish.objects.filter(slug__in=slug_list))
            for dish in dish_list:
                dish.popularity -= 1
                dish.save()

            notification.order.delete()

        return JsonResponse({})


@class_superuser_only
class OrderArchiveYear(View):
    
    def get(self, request, year):
        orders = list(Order.objects.filter(made_on__year=year))
        month_data_list = [0] * 13
        for order in orders:
            month_data_list[order.made_on.month] += order.get_total()
        month_data_list[0] = sum(month_data_list[1:])
        return render(request, 'main/order_archive_year.html',
                      {'year': year,
                       'total': month_data_list[0],
                       'month_data_list': month_data_list[1:]})


@class_superuser_only
class OrderArchiveMonth(View):
    
    def get(self, request, year, month):
        orders = list(Order.objects.filter(made_on__year=year,
                                           made_on__month=month))
        factor = 1 + max(calendar.Calendar().itermonthdays(int(year),
                                                           int(month)))
        day_data_list = [0] * factor
        for order in orders:
            day_data_list[order.made_on.day] += order.get_total()
        day_data_list[0] = sum(day_data_list[1:])
        days = ' '.join(str(i) for i in range(1, factor))
        return render(request, 'main/order_archive_month.html',
                      {'year': year,
                       'month': month,
                       'total': day_data_list[0],
                       'day_data_list': day_data_list[1:],
                       'days': days})


@class_superuser_only
class CategoryDishesPopularity(View):
    
    def get(self, request, slug):
        queryset = Category.objects.filter(slug__iexact=slug).prefetch_related(
            Prefetch('dishes', queryset=Dish.objects.filter(belongs_to='id1')))
        try:
            category = queryset.get()
        except Category.DoesNotExist:
            raise Http404()
        
        dish_list = []
        for dish in category.dishes.all():
            dish_list.append({'name': dish.name, 'popularity': dish.popularity})
        
        return render(request, 'main/category_dishes_popularity.html',
                      {'dish_list': dish_list,
                       'category': category.name})