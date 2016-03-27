from django.conf.urls import url
from django.views.generic import TemplateView

from . import views


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='menu/category_list.html'),
        name='category_list'),
    url(r'^(?P<slug>[-\w]+)/$', views.CategoryDetail.as_view(),
        name='category_detail'),
]