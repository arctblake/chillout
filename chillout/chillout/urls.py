from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

from main import views as main_views
from user import views as user_views
from menu import urls as menu_urls


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', main_views.MainPage.as_view(), name='main_page'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^menu/', include(menu_urls)),
    url(r'^registration/$', user_views.Registration.as_view(),
        name='registration'),
    url(r'^activation/(?P<uid64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        user_views.ActivateAccount.as_view(), name='activation'),
    url(r'^make-order/$', main_views.MakeOrder.as_view(), name='make_order'),
    url(r'^profile/$', user_views.ProfileDetail.as_view(),
        name='profile_detail'),
    url(r'^profile-data/$', main_views.ProfileData.as_view()),
    url(r'^profile/new-notifications/$', user_views.NN.as_view()),
    url(r'^profile/notifications/(?P<pk>\d+)/$',
        main_views.NotificationDetail.as_view(), name='notification_detail'),
    url(r'^statistics/order/(?P<year>\d{4})/$',
        main_views.OrderArchiveYear.as_view(), name='order_archive_year'),
    url(r'^statistics/order/(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        main_views.OrderArchiveMonth.as_view(), name='order_archive_month'),
    url(r'^statistics/popularity/(?P<slug>[-\w]+)/$',
        main_views.CategoryDishesPopularity.as_view(),
        name='category_dishes_popularity')
]
