from __future__ import unicode_literals

from django.db import migrations


category_list = [
    {
     'name': 'Салаты',
     'slug': 'salaty'
    },
    {
     'name': 'Горячие блюда',
     'slug': 'goryachee'
    },
    {
     'name': 'Закуски',
     'slug': 'zakuski'
    },
    {
     'name': 'Супы',
     'slug': 'supy'
    },
    {
     'name': 'Десерты',
     'slug': 'deserty'
    },
    {
     'name': 'Пасты',
     'slug': 'pasty'
    },
    {
     'name': 'Гарниры',
     'slug': 'garniry'
    },
    {
     'name': 'Чай',
     'slug': 'chai'
    },
    {
     'name': 'Авторский чай',
     'slug': 'avtorskiy-chai'
    },
    {
     'name': 'Кофе',
     'slug': 'coffee'
    },
    {
     'name': 'Коктейли',
     'slug': 'cocktail'
    },
    {
     'name': 'Другие напитки',
     'slug': 'drugie-napitki'
    },
]


def add_categories(apps, schema_editor):
    Category = apps.get_model('menu', 'Category')
    for category in category_list:
        Category.objects.create(**category)


def remove_categories(apps, schema_editor):
    Category = apps.get_model('menu', 'Category')
    category_slugs = [category['slug'] for category in category_list]
    Category.objects.filter(slug__in=category_slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0002_ingredients_add'),
    ]

    operations = [
        migrations.RunPython(add_categories, remove_categories),
    ]
