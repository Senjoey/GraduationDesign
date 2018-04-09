from django.http import HttpResponse
from quanter.stock_data import StockDataService
from quanter.three_k_strategy import ThreeKStrategy
from quanter.models import FirstHundredStock2014yield, FirstHundredStock2015yield, FirstHundredStock2016yield, \
    FirstHundredStock2017yield, FirstHundredStock2018yield
import pandas as pd
import json
import datetime
import numpy as np
from sqlalchemy import create_engine
from django.core import serializers


# 有每一天的收益率
def test_one_stock_sell_when_large_departure(code, start_date, end_date, initial_money):
    print('code: ', code, ' start_date: ', start_date, ' end_date: ', end_date, ' initial_money: ', initial_money)
    data_service = StockDataService()
    # 获取股票
    all_stocks = data_service.get_stock_by_code(code)

    for stock in all_stocks:
        print('处理stock: ', stock.name)
        # 获取股票的收盘价
        start = datetime.date(2016, 1, 1)
        end = datetime.date(2016, 12, 31)

        # start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        # end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

        close_datas = data_service.get_stock_data(stock.code, start, end)
        profit_day = []
        # close_datas.set_index('date')
        # close_datas.sort_index()
        # close_series = close_datas['close']
        # index = close_series.index
        # for i, x in enumerate(close_series):
        #     profit_day.append([str(index[i]), close_series[index[i]]])
        return close_datas['close']
        # return close_series.to_json(orient='split')


        # 计算ma20
        # ma20_datas = close_datas['close'].rolling(20, 1).mean()
        # ma_data = {'ma20': ma20_datas}
        # ma_res = pd.DataFrame(data=ma_data, index=close_datas.index)
        # # 计算乖离值
        # ma_res['ma20_departure_value'] = ((close_datas['close'] - ma_res['ma20']) / ma_res['ma20']) * 100
        # ma_res_round = ma_res.round(3)
        # ma_res_round['close'] = close_datas['close']
        # print('ma_res_round: ', ma_res_round)
        # # 产生买卖信号
        # prices_and_ma_related = ma_res_round[4:]
        # buy_flag = np.where((prices_and_ma_related['close'] > prices_and_ma_related['ma20']) &
        #                     (prices_and_ma_related['ma20_departure_value'] <= 3.6) &
        #                     (prices_and_ma_related['ma20_departure_value'] > 0), 1, 0)
        # sell_flag = np.where(prices_and_ma_related['ma20_departure_value'] > 10, -1, buy_flag)
        # buy_and_sell_signal = pd.Series(sell_flag, prices_and_ma_related.index)
        # print('buy_and_sell_signal: ', buy_and_sell_signal)
        # # 计算三年的收益率
        # asset_series = pd.Series(index=prices_and_ma_related.index)  # 资产数 asset
        # asset = 100000.0
        # hold_sum_series = pd.Series(index=prices_and_ma_related.index)  # 持有股票的数量
        # hold_sum = 0
        # daily_stock_yield_series = pd.Series(index=prices_and_ma_related.index)  # 每日收益率 daily_stock_yield
        # date_index = prices_and_ma_related.index
        # close_series = prices_and_ma_related['close']
        # for i, x in enumerate(buy_and_sell_signal):
        #     # 买信号
        #     if x == 1:
        #         # 空仓，则买入
        #         if hold_sum == 0:
        #             hold_sum = asset / close_series[date_index[i]]
        #         # 已经持有
        #         else:
        #             asset = close_series[date_index[i]] * hold_sum
        #     elif x == -1:
        #         if hold_sum != 0:
        #             asset = close_series[date_index[i]] * hold_sum
        #             hold_sum = 0
        #     hold_sum_series[date_index[i]] = hold_sum
        #     asset_series[date_index[i]] = asset
        #     daily_stock_yield_series[date_index[i]] = 100 * (asset_series[date_index[i]] - 100000.0) / 100000.0
        # capital = pd.DataFrame(data={'hold': hold_sum_series, 'asset': asset_series, 'yield': daily_stock_yield_series},
        #                        index=prices_and_ma_related.index)
        # engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test2?charset=utf8')
        # capital.to_sql('quanter_zhongshangongyongten2016', engine, if_exists='append')
        # return HttpResponse("查询数据成功.")