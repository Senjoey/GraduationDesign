from django.http import HttpResponse
from quanter.stock_data import StockDataService
from quanter.three_k_strategy import ThreeKStrategy
from quanter.models import FirstHundredStock2014yield, FirstHundredStock2015yield, FirstHundredStock2016yield, \
    FirstHundredStock2017yield, FirstHundredStock2018yield, tqstock
import pandas as pd
import json
import datetime
import numpy as np
from sqlalchemy import create_engine
from django.shortcuts import render
from quanter import strategy
from quanter.models import Dailydata
from quanter import multi_back_test
# 选股
# 1、先选出从16到18年每年数据等量的股票basicstockpool
# 2、再选出14 15 16 3年回测效果较好的股票


def choose_stock(request):
    len_2014 = 245
    len_2015 = 244
    len_2016 = 244
    len_2017 = 244
    len_2018 = 59
    day_len = []
    data_service = StockDataService()
    all_stock_query_set = data_service.get_all_stock()[94:]
    code_list = []
    name_list = []
    start_date_2014 = datetime.date(2014, 1, 1)
    end_date_2014 = datetime.date(2014, 12, 31)
    start_date_2015 = datetime.date(2015, 1, 1)
    end_date_2015 = datetime.date(2015, 12, 31)
    start_date_2016 = datetime.date(2016, 1, 1)
    end_date_2016 = datetime.date(2016, 12, 31)
    start_date_2017 = datetime.date(2017, 1, 1)
    end_date_2017 = datetime.date(2017, 12, 31)
    start_date_2018 = datetime.date(2018, 1, 1)
    end_date_2018 = datetime.date(2018, 3, 30)
    engine = create_engine('mysql+mysqlconnector://root:liufengnju@114.212.242.143:3306/quanter?charset=utf8')
    for stock in all_stock_query_set:
        print('查看stock: ', stock.code, ' ,', stock.name)
        len14 = len(Dailydata.objects.filter(date__range=(start_date_2014, end_date_2014), code__in=[stock.code]))
        print('len14: ', len14)
        len15 = len(Dailydata.objects.filter(date__range=(start_date_2015, end_date_2015), code__in=[stock.code]))
        print('len15: ', len15)
        len16 = len(Dailydata.objects.filter(date__range=(start_date_2016, end_date_2016), code__in=[stock.code]))
        print('len16: ', len16)
        len17 = len(Dailydata.objects.filter(date__range=(start_date_2017, end_date_2017), code__in=[stock.code]))
        print('len17: ', len17)
        len18 = len(Dailydata.objects.filter(date__range=(start_date_2018, end_date_2018), code__in=[stock.code]))
        print('len18: ', len18)
        if (len14 == len_2014) & (len15 == len_2015) & (len16 == len_2016) & (len17 == len_2017) & (len18 == len_2018):
            code_list.append(stock.code)
            name_list.append(stock.name)
            print('code: ', stock.code, ' name: ', stock.name)
            res_stock_df = pd.DataFrame(data={'code': code_list, 'name': name_list})
            res_stock_df.to_sql('quanter_tqbasicstockbool', engine, if_exists='append')
    return HttpResponse("获取数据成功")



