from __future__ import unicode_literals

from django.db import migrations


ingredient_list = [
    {
     'name': 'картофель',
     'category': 'овощи',
     'price': 20
    },
    {
     'name': 'свекла',
     'category': 'овощи',
     'price': 30
    },
    {
     'name': 'морковь',
     'category': 'овощи',
     'price': 30
    },
    {
     'name': 'огурцы маринованные',
     'category': 'овощи',
     'price': 40
    },
    {
     'name': 'капуста',
     'category': 'овощи',
     'price': 35
    },
    {
     'name': 'лук репчатый',
     'category': 'овощи',
     'price': 20
    },
    {
     'name': 'горох',
     'category': 'овощи',
     'price': 20
    },
    {
     'name': 'огурцы свежие',
     'category': 'овощи',
     'price': 35
    },
    {
     'name': 'помидоры',
     'category': 'овощи',
     'price': 45
    },
    {
     'name': 'перец болгарский',
     'category': 'овощи',
     'price': 30
    },
    {
     'name': 'свинина',
     'category': 'мясо',
     'price': 100,
     'proteins': 20,
     'fats': 3,
     'carbohydrates': 10,
     'calories': 70
    },
    {
     'name': 'говядина',
     'category': 'мясо',
     'price': 120,
     'proteins': 22,
     'fats': 4,
     'carbohydrates': 12,
     'calories': 75
    },
    {
     'name': 'куриные крылышки',
     'category': 'курица',
     'price': 110,
     'proteins': 17,
     'fats': 6,
     'carbohydrates': 11,
     'calories': 68
    },
    {
     'name': 'куриная грудка',
     'category': 'курица',
     'price': 150,
     'proteins': 23,
     'fats': 5,
     'carbohydrates': 15,
     'calories': 77
    },
    {
     'name': 'лосось',
     'category': 'рыба',
     'price': 125,
     'proteins': 14,
     'fats': 14,
     'carbohydrates': 10,
     'calories': 61
    },
    {
     'name': 'омуль',
     'category': 'рыба',
     'price': 100,
     'proteins': 10,
     'fats': 16,
     'carbohydrates': 13,
     'calories': 63
    },
]


def add_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('menu', 'Ingredient')
    for ingredient in ingredient_list:
        Ingredient.objects.create(**ingredient)


def remove_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('menu', 'Ingredient')
    ingredient_names = [ingredient['name'] for ingredient in ingredient_list]
    Ingredient.objects.filter(name__in=ingredient_names).delete()
    

class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_ingredients, remove_ingredients),
    ]
