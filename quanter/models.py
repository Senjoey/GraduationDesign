from django.db import models


# Create your models here.
class Stock(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)
    isInPool = models.BooleanField(default=1)


class Dailydata(models.Model):
    id = models.IntegerField(max_length=11, primary_key=True)
    index = models.BigIntegerField()
    date = models.DateField()
    open = models.FloatField()
    close = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    volume = models.FloatField()
    code = models.CharField(max_length=50)


# test2数据库
class Ma(models.Model):
    date = models.DateField()
    ma20 = models.FloatField()
    ma5 = models.FloatField()
    ma20_departure_value = models.FloatField()
    close = models.FloatField()


class Mystock(models.Model):
    id = models.IntegerField(max_length=11, primary_key=True)
    code = models.TextField()
    name = models.TextField()
    c_name = models.TextField()





