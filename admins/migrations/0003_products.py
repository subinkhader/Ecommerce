# Generated by Django 2.2.28 on 2023-04-12 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('admins', '0002_delete_products'),
    ]

    operations = [
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200)),
                ('price', models.FloatField()),
                ('product_description', models.CharField(max_length=1000)),
                ('product_picture', models.FileField(upload_to='')),
                ('is_active', models.SmallIntegerField(default=1)),
            ],
        ),
    ]