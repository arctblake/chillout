from django.shortcuts import render, redirect
from django.db.models import Prefetch
from django.http import Http404, JsonResponse, HttpResponseBadRequest
from django.views.generic import View, DetailView, ListView
from django.contrib.auth.forms import AuthenticationForm

from .models import Dish, Category
from user.decorators import class_login_required


class CategoryDetail(View):
    
    def get(self, request, slug):
        #if not request.is_ajax():
        #    return HttpResponseBadRequest()

        if request.user.is_authenticated():
            kwargs = {'belongs_to__in': ['id1', request.user.profile.slug]}
        else:
            kwargs = {'belongs_to': 'id1'}

        queryset = Category.objects.filter(slug__iexact=slug).prefetch_related(
            Prefetch('dishes', queryset=Dish.objects.filter(**kwargs)))
        try:
            category = queryset.get()
        except Category.DoesNotExist:
            raise Http404()
        
        dishes = {}
        for dish in category.dishes.all():
            dishes[dish.name] = {'slug': dish.slug, 'price': dish.price,
                                 'description': (dish.amount + ' ' +
                                                 dish.description),
                                 'popularity': dish.popularity,
                                 'truncated_name': dish.get_truncated_name()}
        
        return JsonResponse(dishes)


class DishDetail(DetailView):
    
    model = Dish


@class_login_required
class DishCreate(View):
    ...
    # Если такое блюдо уже было создано каким-то другим пользователем...