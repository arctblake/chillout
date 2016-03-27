from __future__ import unicode_literals

from django.db import migrations


dish_list = [
    {
     'name': 'Винегрет',
     'slug': 'vinegret',
     'price': 130,
     'amount': '150г',
     'description': ('Картофель, свекла, морковь, огурцы соленые, капуста, '
                     'лук репчатый, горох'),
     'category': 'salaty'
    },
    {
     'name': 'Овощной',
     'slug': 'ovoshnoy',
     'price': 140,
     'amount': '150г',
     'description': ('Огурцы, помидоры, болгарский перец, лист салата, зелень, '
                     'специи'),
     'category': 'salaty'
    },
    {
     'name': 'Греческий',
     'slug': 'grecheskiy',
     'price': 150,
     'amount': '150г',
     'description': ('Помидоры, огурцы, перец болгарский, зелень, маслины, '
                     'сыр фетта, лист салата, специи'),
     'category': 'salaty'
    },
    {
     'name': 'Цезарь с курицей',
     'slug': 'cesar-s-kuricey',
     'price': 165,
     'amount': '150г',
     'description': ('Отварное филе куриной грудки, чесночок, лист салата, '
                     'помидоры Черри, сыр Пармезан, сухарики, майонез, соус'),
     'category': 'salaty'
    },
    {
     'name': 'Цезарь с семгой',
     'slug': 'cesar-s-semgoy',
     'price': 185,
     'amount': '150г',
     'description': ('Семга, лист салата, помидоры Черри, сыр Пармезан, '
                     'сухарики, майонез, соевый соус, соус для салата Цезарь, '
                     'лимон'),
     'category': 'salaty'
    },
    {
     'name': 'Стрелецкий',
     'slug': 'streleckiy',
     'price': 190,
     'amount': '150г',
     'description': ('Отварное мясо говядины, перец болгарский, лук репчатый, '
                     'помидоры, зелень, специи, соус'),
     'category': 'salaty'
    },
    {
     'name': 'Чалагач',
     'slug': 'chalagach',
     'price': 135,
     'amount': '100г',
     'description': ('Свинина на косточке, приправленная ароматными специя, '
                     'чесноком и провансальскими травами'),
     'category': 'goryachee'
    },
    {
     'name': 'Золотая рыбка',
     'slug': 'zolotaya-rybka',
     'price': 240,
     'amount': '250г',
     'description': 'Сочная и хрустящая мойва в панировочных сухариках',
     'category': 'goryachee'
    },
    {
     'name': 'Куриные крылышки',
     'slug': 'kurinye-krylyshki',
     'price': 220,
     'amount': '200г',
     'description': 'Крылышки куриные, обжаренные в остром соусе',
     'category': 'goryachee'
    },
    {
     'name': 'Шашлычки из курицы на шпажках',
     'slug': 'shashlychki-iz-kuricy',
     'price': 230,
     'amount': '150г',
     'description': ('Шашлычки из сочного куриного филе, приправленные '
                     'ароматными специями'),
     'category': 'goryachee'
    },
    {
     'name': 'Шашлычки из лосося на шпажках',
     'slug': 'shashlychki-iz-lososya',
     'price': 250,
     'amount': '150г',
     'description': 'Изысканные шашлычки из нежного лосося на шпажках',
     'category': 'goryachee'
    },
    {
     'name': 'Бефстроганов',
     'slug': 'befstroganov',
     'price': 150,
     'amount': '100г',
     'description': 'Тонкие ломтики говядины, приправленные легким соусом',
     'category': 'goryachee'
    },
    {
     'name': 'Буузы рубленые',
     'slug': 'buuzy-rublenye',
     'price': 85,
     'amount': '2шт',
     'description': ('Традиционное бурятское блюдо из рубленого фарша, '
                     'завернутого в тесто'),
     'category': 'goryachee'
    },
    {
     'name': 'Позы жареные',
     'slug': 'pozy-zharenye',
     'price': 90,
     'amount': '90г',
     'description': ('Хрустящие бурятские позы, зажаренные до золотистой '
                     'корочки'),
     'category': 'goryachee'
    },
    {
     'name': 'Яичница глазунья с колбасой',
     'slug': 'yaichnica-glazuniya',
     'price': 90,
     'amount': '150г',
     'category': 'goryachee'
    },
    {
     'name': 'Сосиски отварные',
     'slug': 'sosiski-otvarnye',
     'price': 70,
     'amount': '105г',
     'description': 'Маленькие отварные колбаски',
     'category': 'goryachee'
    },
]


def add_dishes(apps, schema_editor):
    Dish = apps.get_model('menu', 'Dish')
    Category = apps.get_model('menu', 'Category')
    dish_categories = list({dish['category'] for dish in dish_list})
    categories = Category.objects.filter(slug__in=dish_categories)
    categories = {category.slug: category for category in categories}
    for dish in dish_list:
        dish['category'] = categories[dish['category']]
        Dish.objects.create(**dish)


def remove_dishes(apps, schema_editor):
    Dish = apps.get_model('menu', 'Dish')
    dish_slugs = [dish['slug'] for dish in dish_list]
    Dish.objects.filter(slug__in=dish_slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0003_categories_add'),
    ]

    operations = [
        migrations.RunPython(add_dishes, remove_dishes),
    ]
