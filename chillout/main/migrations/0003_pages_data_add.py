from __future__ import unicode_literals

from django.db import migrations


def add_pages_data(apps, schema_editor):
    PagesData = apps.get_model('main', 'PagesData')
    text = ('Donec pellentesque odio sed placerat ullamcorper. Integer ligula '
            'libero, vestibulum eu ante a, sollicitudin molestie enim. Cras '
            'dapibus augue vitae nisi imperdiet, sit amet mattis sapien congue.'
            ' Nam in mi laoreet, ullamcorper mauris quis, convallis lectus.')
    PagesData.objects.create(main_page_offer='Совет дня',
                             main_page_offer_text=text)


def remove_pages_data(apps, schema_editor):
    PagesData = apps.get_model('main', 'PagesData')
    PagesData.objects.get(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20160327_2021'),
    ]

    operations = [
        migrations.RunPython(add_pages_data, remove_pages_data),
    ]
