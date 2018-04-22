from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from quanter.models import Dailydata


class ThreeKStrategy(object):
    def __init__(self, start_date, end_date, initial_money=100000.0):
        self.start_date = start_date
        self.end_date = end_date
        self.initial_money = initial_money

    def get_date_series(self):
        hs300_query_set = Dailydata.objects.filter(date__range=(self.start_date, self.end_date), code='399300')
        dates_arry = hs300_query_set.values("date")
        print(dates_arry)
        print("type of dates_arry: ", type(dates_arry))







    # def __init__(self, start_date, end_date, initial_money=100000.0):
    #     self.start_date = start_date
    #     self.end_date = end_date
    #     self.initial_money = initial_money

    # 判断均线趋势是向上还是向下：1向上，-1向下，0持平
    # 均线趋势向上，正乖离值不大【0<x<=3.6】->买
    # 正乖离过大获利【x>3.6】->卖出
    # def generate_ma_and_departure_value_signal(self, prices):
    #     # 产生买信号
    #     buy_flag = np.where((prices['close'] > prices['ma20']) & (prices['ma20_departure_value'] <= 3.6) &
    #                        (prices['ma20_departure_value'] > 0), 1, 0)
    #     # ma_series = pd.Series(ma_buy_flag, prices.index)
    #     # 产生卖信号
    #     sell_flag = np.where(prices['ma20_departure_value'] > 22, -1, buy_flag)
    #     buy_and_sell_series = pd.Series(sell_flag, prices.index)
    #     print('buy_and_sell_series: ', buy_and_sell_series)
    #     return buy_and_sell_series

    # 计算乖离值存入数据库
    # def cal_departure_value(self, datas):
    #     # 计算MA5、MA20
    #     ma5 = self.get_ma(datas['close'], 5)
    #     ma20 = self.get_ma(datas['close'], 20)
    #     ma_data = {'ma5': ma5, 'ma20': ma20}
    #     ma_res = pd.DataFrame(data=ma_data).set_index(datas.index)
    #     ma_res['ma20_departure_value'] = ((datas['close'] - ma_res['ma20'])/ma_res['ma20'])*100
    #     ma_res_round = ma_res.round(2)
    #     ma_res_round['close'] = datas['close']
    #     print('ma20_departure_value_median', self.ma20_departure_value_median(ma_res_round))
    #     engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test2?charset=utf8')
    #     ma_res_round.to_sql('quanter_ma', engine, if_exists='append')

    # 计算乖离值得中位数
    # def ma20_departure_value_median(self, df):
    #     above_zero_ma20_departure_value = df[df.ma20_departure_value > 0].ma20_departure_value
    #     below_zero_ma20_departure_value = df[df.ma20_departure_value < 0].ma20_departure_value
    #     return above_zero_ma20_departure_value.median(), below_zero_ma20_departure_value.median()

    # 计算移动平均值
    # def get_ma(self, prices, window, period=1):
    #     ma_price = prices.rolling(window, period).mean()
    #     return ma_price

    # for each trading bar:
    # do_something_with_prices();
    # buy_sell_or_hold_something();
    # next_bar();
    # def automatic_trade(self, stock_ids):
    #     daily_stock_yields = [] #股票每日收益率
    #     # 回测流程：
    #     # 1、判断是否满足某种型态
    #     # 2、买、卖或继续持有
    #     # 3、下一个交易日
    #     return daily_stock_yields



