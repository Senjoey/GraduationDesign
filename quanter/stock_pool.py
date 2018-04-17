from django.http import HttpResponse
from quanter.stock_data import StockDataService
import pandas as pd
import datetime
from sqlalchemy import create_engine
import tushare as ts
# 选股
# 1、先选出从16到18年每年数据等量的股票basicstockpool
# 2、再选出14 15 16 3年回测效果较好的股票


def choose_stock(request):
    len_2014 = 245
    len_2015 = 244
    len_2016 = 244
    len_2017 = 244
    len_2018 = 64
    day_len = []
    data_service = StockDataService()
    all_stock_query_set = data_service.get_all_stock()
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
        code = stock.code
        print('查看stock: ', code, ' ,', stock.name)
        # df = ts.get_k_data(code, start="2014-01-01", end="2018-04-10")
        # len14 = len(Dailydata.objects.filter(date__range=(start_date_2014, end_date_2014), code__in=[stock.code]))
        len14 = len(ts.get_k_data(code, '2014-01-01', "2014-12-31"))
        print('len14: ', len14)
        # len15 = len(Dailydata.objects.filter(date__range=(start_date_2015, end_date_2015), code__in=[stock.code]))
        len15 = len(ts.get_k_data(code, '2015-01-01', '2015-12-31'))
        print('len15: ', len15)
        # len16 = len(Dailydata.objects.filter(date__range=(start_date_2016, end_date_2016), code__in=[stock.code]))
        len16 = len(ts.get_k_data(code, '2016-01-01', '2016-12-31'))
        print('len16: ', len16)
        # len17 = len(Dailydata.objects.filter(date__range=(start_date_2017, end_date_2017), code__in=[stock.code]))
        len17 = len(ts.get_k_data(code, '2017-01-01', '2017-12-31'))
        print('len17: ', len17)
        # len18 = len(Dailydata.objects.filter(date__range=(start_date_2018, end_date_2018), code__in=[stock.code]))
        len18 = len(ts.get_k_data(code, '2018-01-01', '2018-04-10'))
        print('len18: ', len18)
        print(' ')
        if (len14 == len_2014) & (len15 == len_2015) & (len16 == len_2016) & (len17 == len_2017) & (len18 == len_2018):
            code_list.append(stock.code)
            name_list.append(stock.name)
            print('添加code: ', stock.code, ' name: ', stock.name)
    res_stock_df = pd.DataFrame(data={'code': code_list, 'name': name_list})
    res_stock_df.to_sql('quanter_tqbasicstockpool', engine, if_exists='append')
    return HttpResponse("获取数据成功")



