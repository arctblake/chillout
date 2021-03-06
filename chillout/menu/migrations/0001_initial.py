# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-27 12:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('price', models.SmallIntegerField()),
                ('amount', models.CharField(default='', max_length=50)),
                ('description', models.TextField(default='')),
                ('belongs_to', models.CharField(default='id1', max_length=102)),
                ('popularity', models.IntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dishes', to='menu.Category')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=100)),
                ('price', models.SmallIntegerField()),
                ('min_amount', models.SmallIntegerField(null=True)),
                ('proteins', models.SmallIntegerField(null=True)),
                ('fats', models.SmallIntegerField(null=True)),
                ('carbohydrates', models.SmallIntegerField(null=True)),
                ('calories', models.SmallIntegerField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='dish',
            name='ingredients',
            field=models.ManyToManyField(blank=True, related_name='dishes', to='menu.Ingredient'),
        ),
    ]
