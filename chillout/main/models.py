from django.db import models
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property

from user.models import Profile


class Order(models.Model):

    made_on = models.DateField(auto_now_add=True)
    dishes = models.TextField(default='')
    anon_dishes = models.TextField(default='')

    made_by = models.ForeignKey(Profile, related_name='orders', null=True)
    
    class Meta:
        
        ordering = ['-made_on']
    
    def __str__(self):
        return self.made_on.isoformat() + ' | ' + str(total)
    
    # slug|name|price|amount;
    @cached_property
    def get_dish_objects(self):
        if not self.dishes: return []
        dishes = self.dishes.split(';')
        dish_list = []
        for dish in dishes:
            slug, name, price, amount = dish.split('|')
            total = int(price) * int(amount)
            dish_list.append({'slug': slug, 'name': name, 'price': price,
                              'amount': amount, 'total': total})
        return dish_list
    
    # meat fried 200g, milk 100g|price|amount;
    @cached_property
    def get_anon_dish_objects(self):
        if not self.anon_dishes: return []
        anon_dishes = self.anon_dishes.split(';')
        anon_dish_list = []
        i = 1
        for dish in anon_dishes:
            description, price, amount = dish.split('|')
            anon_dish_list.append({'slug': 'anonymous' + str(i),
                                   'name': description,
                                   'price': price,
                                   'amount': amount,
                                   'total': int(price) * int(amount)})
            i += 1
        return anon_dish_list
    
    def get_total(self):
        dl = self.get_dish_objects + self.get_anon_dish_objects
        total = 0
        for d in dl:
            total += d['total']
        return total


class Notification(models.Model):
    
    details = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    order = models.OneToOneField(Order)
    profiles = models.ManyToManyField(Profile, related_name='notifications')
    
    class Meta:
        
        ordering = ['-date_time']
    
    def __str__(self):
        return self.date_time.isoformat()
    
    def get_absolute_url(self):
        return reverse('notification_detail', kwargs={'pk': self.pk})
    
    def get_css_class_name(self):
        return 'active' if self.is_active else 'read'


class PagesData(models.Model):
    
    main_page_offer = models.CharField(max_length=300, default='')
    main_page_offer_text = models.TextField(default='')
    
    profile_page_show_bonus = models.BooleanField(default=False)