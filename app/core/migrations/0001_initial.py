# Generated by Django 2.2.11 on 2020-03-08 17:40

import core.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('account_name', models.CharField(max_length=30)),
                ('account_color', models.CharField(max_length=30)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('action_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('category_color', models.CharField(max_length=30)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('caterory_name', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=30)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('tag_color', models.CharField(max_length=30)),
                ('tag_name', models.CharField(max_length=30, unique=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Company')),
            ],
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('transfer_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('from_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_account', to='core.Account')),
                ('to_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_account', to='core.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('transaction_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Account')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Category')),
                ('tags', models.ManyToManyField(blank=True, to='core.Tag')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20, unique=True)),
                ('phone_confirmed', models.BooleanField(default=False)),
                ('image', models.ImageField(null=True, upload_to=core.models.customer_image_file_path)),
                ('is_admin', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profiles', to='core.Company')),
            ],
        ),
    ]
