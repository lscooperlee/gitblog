# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-10-31 07:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitblog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visit',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
