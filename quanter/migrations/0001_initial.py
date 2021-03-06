# Generated by Django 2.0.2 on 2018-04-05 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dailydata',
            fields=[
                ('id', models.IntegerField(max_length=11, primary_key=True, serialize=False)),
                ('index', models.BigIntegerField()),
                ('date', models.DateField()),
                ('open', models.FloatField()),
                ('close', models.FloatField()),
                ('high', models.FloatField()),
                ('low', models.FloatField()),
                ('volume', models.FloatField()),
                ('code', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FirstHundredStock2014yield',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('yield2014', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='FirstHundredStock2015yield',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('yield2015', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='FirstHundredStock2016yield',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('yield2016', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='FirstHundredStock2017yield',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('yield2017', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='FirstHundredStock2018yield',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('yield2018', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Ma',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('ma20', models.FloatField()),
                ('ma5', models.FloatField()),
                ('ma20_departure_value', models.FloatField()),
                ('close', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Mystock',
            fields=[
                ('id', models.IntegerField(max_length=11, primary_key=True, serialize=False)),
                ('code', models.TextField(max_length=255)),
                ('name', models.TextField()),
                ('c_name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('isInPool', models.BooleanField(default=1)),
            ],
        ),
    ]
