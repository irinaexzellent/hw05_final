# Generated by Django 2.2.9 on 2021-12-21 08:12

from django.db import migrations
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_auto_20211221_1110'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': [django.db.models.expressions.OrderBy(django.db.models.expressions.F('pub_date'), descending=True, nulls_last=True)]},
        ),
    ]
