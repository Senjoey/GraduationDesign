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


class MyStock(models.Model):
    id = models.IntegerField(max_length=11, primary_key=True)
    code = models.TextField(max_length=255)
    name = models.TextField()
    c_name = models.TextField()


class TqStock(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.TextField()
    name = models.TextField()
    profit = models.FloatField()
    isInPool = models.IntegerField()
    isChecked = models.IntegerField()


class TqBasicStockBool(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.TextField()
    name = models.TextField()


class TqSellWhenLargeDepartureStrategyOne(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.TextField()
    name = models.TextField()
    profit = models.FloatField()
    isInPool = models.IntegerField()
    isChecked = models.IntegerField()


class TqBuyWhenLargeDepartureStrategyTwo(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.TextField()
    name = models.TextField()
    profit = models.FloatField()
    isInPool = models.IntegerField()
    isChecked = models.IntegerField()


class TqPoolDate(models.Model):
    id = models.IntegerField(primary_key=True)
    start_date = models.TextField()
    end_date = models.TextField()


class TqStrategySetting(models.Model):
    id = models.IntegerField(primary_key=True)
    negative_departure = models.FloatField()
    positive_departure = models.FloatField()
    stop_profit = models.FloatField()
    stop_loss = models.FloatField()


class FilterStock2014(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=11)
    # name = models.CharField(max_length=11)
    profit2014 = models.FloatField()


class FilterStock2015(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=11)
    # name = models.CharField(max_length=11)
    profit2015 = models.FloatField()


class FilterStock2016(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=11)
    # name = models.CharField(max_length=11)
    profit2016 = models.FloatField()


class FilterStock2017(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=11)
    # name = models.CharField(max_length=11)
    profit2017 = models.FloatField()


class FirstHundredStock2018yield(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=255)
    # name = models.CharField(max_length=255)
    yield2018 = models.FloatField()


