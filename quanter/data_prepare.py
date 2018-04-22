from quanter.models import Stock
import tushare as ts
from sqlalchemy import create_engine
from sqlalchemy import VARCHAR
from sqlalchemy import Date
import pandas as pd


class DataPrepare(object):

    def ma_data_prepare(self, start, end):
        all_stock = Stock.objects.all()[2898:]
        for stock in all_stock:
            code = stock.code
            print(code)
            df = ts.get_hist_data(code, start, end)
            if df is not None:
                data = {'ma20': df['ma20'], 'code': code}
                res = pd.DataFrame(data=data)
                engine = create_engine('mysql+mysqlconnector://root:liufengnju@114.212.242.143:3306/quanter?charset=utf8')
                res.to_sql('quanter_tqmadata', engine, if_exists='append', dtype={'date': Date, 'code': VARCHAR(50)})
            else:
                print("无数据")

    def test(self):
        df = ts.get_hist_data('601965', '2014-01-01', '2018-04-20')
        if df is None:
            print("无数据")
        else:
            data = {'ma20': df['ma20'], 'code': '601965'}
            res = pd.DataFrame(data=data)
            engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test2?charset=utf8')
            res.to_sql('quanter_ma20data', engine, if_exists='append', dtype={'date': Date, 'code': VARCHAR(50)})
        # stock = Stock.objects.all()[2895]
        # print(stock.code)


