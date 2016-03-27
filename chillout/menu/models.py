from django.db import models
from django.core.urlresolvers import reverse


class Ingredient(models.Model):
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.SmallIntegerField()
    min_amount = models.SmallIntegerField(null=True)
    # for 100g
    proteins = models.SmallIntegerField(null=True)
    fats = models.SmallIntegerField(null=True)
    carbohydrates = models.SmallIntegerField(null=True)
    calories = models.SmallIntegerField(null=True)
    
    def __str__(self):
        return self.name


class Dish(models.Model):
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    price = models.SmallIntegerField()
    amount = models.CharField(max_length=50, default='')
    description = models.TextField(default='')
    belongs_to = models.CharField(max_length=102, default='id1')
    popularity = models.IntegerField(default=0)
    
    ingredients = models.ManyToManyField(Ingredient, related_name='dishes',
                                         blank=True)
    category = models.ForeignKey('Category', related_name='dishes')
    
    class Meta:
        
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('dish_detail',
            kwargs={'category_slug': self.category.slug,
                    'dish_slug': self.slug})
    
    def get_truncated_name(self):
        if len(self.name) > 15:
            return self.name[:15] + '...'
        return self.name
    
    def is_anonymous(self):
        return False


class Category(models.Model):
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    
    class Meta:
        
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})