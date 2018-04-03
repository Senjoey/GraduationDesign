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


def merge_three_year_yield(request):
    # 分别读取三年的收益率数据
    data_query_set = FirstHundredStock2014yield.objects.all()
    stock_2014_yield = pd.DataFrame(list(data_query_set.values('id', 'code', 'name', 'yield2014')))
    stock_2014_yield.set_index('id', inplace=True)
    stock_2014_yield.sort_index()

    data_query_set = FirstHundredStock2015yield.objects.all()
    stock_2015_yield = pd.DataFrame(list(data_query_set.values('id', 'code', 'yield2015')))
    stock_2015_yield.set_index('id', inplace=True)
    stock_2015_yield.sort_index()

    data_query_set = FirstHundredStock2016yield.objects.all()
    stock_2016_yield = pd.DataFrame(list(data_query_set.values('id', 'code', 'yield2016')))
    stock_2016_yield.set_index('id', inplace=True)
    stock_2016_yield.sort_index()

    data_query_set = FirstHundredStock2017yield.objects.all()
    stock_2017_yield = pd.DataFrame(list(data_query_set.values('id', 'code', 'yield2017')))
    stock_2017_yield.set_index('id', inplace=True)
    stock_2017_yield.sort_index()

    data_query_set = FirstHundredStock2018yield.objects.all()
    stock_2018_yield = pd.DataFrame(list(data_query_set.values('id', 'code', 'yield2018')))
    stock_2018_yield.set_index('id', inplace=True)
    stock_2018_yield.sort_index()
    # 构造合并数据的Dataframe
    three_year_yield = stock_2014_yield
    three_year_yield['yield2015'] = stock_2015_yield['yield2015']
    three_year_yield['yield2016'] = stock_2016_yield['yield2016']
    three_year_yield['yield2017'] = stock_2017_yield['yield2017']
    three_year_yield['yield2018'] = stock_2018_yield['yield2018']
    # 将数据写入数据库
    engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test2?charset=utf8')
    three_year_yield.to_sql('quanter_FirstHundredStockYield', engine, if_exists='append')
    return HttpResponse("合并数据成功.")


# 只有回测结束那一天的收益率
def test_all_stock_sell_when_large_departure(request):
    data_service = StockDataService()
    # 获取所有股票
    all_stocks = data_service.get_all_stock()[0:101]
    capital_list = []

    for stock in all_stocks:
        print('处理stock: ', stock.name)
        # 获取股票的收盘价
        start_date = datetime.date(2017, 1, 1)
        end_date = datetime.date(2017, 12, 31)
        close_datas = data_service.get_stock_data(stock.code, start_date, end_date)
        if len(close_datas) == 0:
            stock_yield = 0
            capital_item = {'code': stock.code, 'name': stock.name, 'yield2017': stock_yield}
            print('处理stock: ', capital_item)
            capital_list.append(capital_item)
            continue

        print('close_datas的大小: ', len(close_datas))

        # 计算ma20
        ma20_datas = close_datas['close'].rolling(20, 1).mean()
        ma_data = {'ma20': ma20_datas}
        ma_res = pd.DataFrame(data=ma_data, index=close_datas.index)
        # 计算乖离值
        ma_res['ma20_departure_value'] = ((close_datas['close'] - ma_res['ma20']) / ma_res['ma20']) * 100
        ma_res_round = ma_res.round(3)
        ma_res_round['close'] = close_datas['close']
        # print('ma_res_round: ', ma_res_round)
        # 产生买卖信号
        prices_and_ma_related = ma_res_round[4:]
        buy_flag = np.where((prices_and_ma_related['close'] > prices_and_ma_related['ma20']) &
                            (prices_and_ma_related['ma20_departure_value'] <= 3.6) &
                            (prices_and_ma_related['ma20_departure_value'] > 0), 1, 0)
        sell_flag = np.where(prices_and_ma_related['ma20_departure_value'] > 15, -1, buy_flag)
        buy_and_sell_signal = pd.Series(sell_flag, prices_and_ma_related.index)
        # print('buy_and_sell_signal: ', buy_and_sell_signal)
        # 计算三年的收益率
        asset = 100000.0
        hold_sum = 0
        date_index = prices_and_ma_related.index
        close_series = prices_and_ma_related['close']
        for i, x in enumerate(buy_and_sell_signal):
            # 买信号
            if x == 1:
                # 空仓，则买入
                if hold_sum == 0:
                    hold_sum = asset / close_series[date_index[i]]
                # 已经持有
                else:
                    asset = close_series[date_index[i]] * hold_sum
            elif x == -1:
                if hold_sum != 0:
                    asset = close_series[date_index[i]] * hold_sum
                    hold_sum = 0
        stock_yield = 100 * (asset - 100000.0) / 100000.0
        capital_item = {'code': stock.code, 'name': stock.name, 'yield2017': stock_yield}
        print('处理stock: ', capital_item)
        capital_list.append(capital_item)
    capital = pd.DataFrame(capital_list)
    engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test2?charset=utf8')
    capital.to_sql('quanter_firsthundredstock2017yieldfifteen', engine, if_exists='append')
    return HttpResponse("查询数据成功.")


# 有每一天的收益率
def test_one_stock_sell_when_large_departure(request):
    data_service = StockDataService()
    # 获取股票
    all_stocks = data_service.get_stock_by_code('000685')

    for stock in all_stocks:
        print('处理stock: ', stock.name)
        # 获取股票的收盘价
        start_date = datetime.date(2016, 1, 1)
        end_date = datetime.date(2016, 12, 31)
        close_datas = data_service.get_stock_data(stock.code, start_date, end_date)
        print('close_datas: ', close_datas)

        # 计算ma20
        ma20_datas = close_datas['close'].rolling(20, 1).mean()
        ma_data = {'ma20': ma20_datas}
        ma_res = pd.DataFrame(data=ma_data, index=close_datas.index)
        # 计算乖离值
        ma_res['ma20_departure_value'] = ((close_datas['close'] - ma_res['ma20']) / ma_res['ma20']) * 100
        ma_res_round = ma_res.round(3)
        ma_res_round['close'] = close_datas['close']
        print('ma_res_round: ', ma_res_round)
        # 产生买卖信号
        prices_and_ma_related = ma_res_round[4:]
        buy_flag = np.where((prices_and_ma_related['close'] > prices_and_ma_related['ma20']) &
                            (prices_and_ma_related['ma20_departure_value'] <= 3.6) &
                            (prices_and_ma_related['ma20_departure_value'] > 0), 1, 0)
        sell_flag = np.where(prices_and_ma_related['ma20_departure_value'] > 10, -1, buy_flag)
        buy_and_sell_signal = pd.Series(sell_flag, prices_and_ma_related.index)
        print('buy_and_sell_signal: ', buy_and_sell_signal)
        # 计算三年的收益率
        asset_series = pd.Series(index=prices_and_ma_related.index)  # 资产数 asset
        asset = 100000.0
        hold_sum_series = pd.Series(index=prices_and_ma_related.index)  # 持有股票的数量
        hold_sum = 0
        daily_stock_yield_series = pd.Series(index=prices_and_ma_related.index)  # 每日收益率 daily_stock_yield
        date_index = prices_and_ma_related.index
        close_series = prices_and_ma_related['close']
        for i, x in enumerate(buy_and_sell_signal):
            # 买信号
            if x == 1:
                # 空仓，则买入
                if hold_sum == 0:
                    hold_sum = asset / close_series[date_index[i]]
                # 已经持有
                else:
                    asset = close_series[date_index[i]] * hold_sum
            elif x == -1:
                if hold_sum != 0:
                    asset = close_series[date_index[i]] * hold_sum
                    hold_sum = 0
            hold_sum_series[date_index[i]] = hold_sum
            asset_series[date_index[i]] = asset
            daily_stock_yield_series[date_index[i]] = 100 * (asset_series[date_index[i]] - 100000.0) / 100000.0
        capital = pd.DataFrame(data={'hold': hold_sum_series, 'asset': asset_series, 'yield': daily_stock_yield_series},
                               index=prices_and_ma_related.index)
        engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test2?charset=utf8')
        capital.to_sql('quanter_zhongshangongyongten2016', engine, if_exists='append')
        return HttpResponse("查询数据成功.")


# 只有回测最后一天的收益率
def test_all_stock_buy_when_large_departure(request):
    # 利用均线趋势向下的背景里的负乖离买反弹，然后在接近向下均线的位置卖出
    data_service = StockDataService()
    # 获取所有股票
    all_stocks = data_service.get_all_stock()[0:101]
    capital_list = []

    for stock in all_stocks:
        print('处理stock: ', stock.name)
        # 获取股票的收盘价
        start_date = datetime.date(2017, 1, 1)
        end_date = datetime.date(2017, 12, 31)
        close_datas = data_service.get_stock_data(stock.code, start_date, end_date)
        if len(close_datas) == 0:
            stock_yield = 0
            capital_item = {'code': stock.code, 'name': stock.name, 'yield2017': stock_yield}
            print('处理stock: ', capital_item)
            capital_list.append(capital_item)
            continue

        print('close_datas的大小: ', len(close_datas))

        # 计算ma20
        ma20_datas = close_datas['close'].rolling(20, 1).mean()
        ma_data = {'ma20': ma20_datas}
        ma_res = pd.DataFrame(data=ma_data, index=close_datas.index)
        # 计算乖离值
        ma_res['ma20_departure_value'] = ((close_datas['close'] - ma_res['ma20']) / ma_res['ma20']) * 100
        ma_res_round = ma_res.round(3)
        ma_res_round['close'] = close_datas['close']
        # print('ma_res_round: ', ma_res_round)
        # 产生买卖信号
        prices_and_ma_related = ma_res_round[4:]
        buy_flag = np.where((prices_and_ma_related['close'] < prices_and_ma_related['ma20']) &
                            (prices_and_ma_related['ma20_departure_value'] <= -3.6), 1, 0)
        sell_flag = np.where((prices_and_ma_related['ma20_departure_value'] > 0) &
                             (prices_and_ma_related['ma20_departure_value'] < 15), -1, buy_flag)
        buy_and_sell_signal = pd.Series(sell_flag, prices_and_ma_related.index)
        # print('buy_and_sell_signal: ', buy_and_sell_signal)
        # 计算三年的收益率
        asset = 100000.0
        hold_sum = 0
        date_index = prices_and_ma_related.index
        close_series = prices_and_ma_related['close']
        for i, x in enumerate(buy_and_sell_signal):
            # 买信号
            if x == 1:
                # 空仓，则买入
                if hold_sum == 0:
                    hold_sum = asset / close_series[date_index[i]]
                # 已经持有
                else:
                    asset = close_series[date_index[i]] * hold_sum
            elif x == -1:
                if hold_sum != 0:
                    asset = close_series[date_index[i]] * hold_sum
                    hold_sum = 0
        stock_yield = 100 * (asset - 100000.0) / 100000.0
        capital_item = {'code': stock.code, 'name': stock.name, 'yield2017': stock_yield}
        print('处理stock: ', capital_item)
        capital_list.append(capital_item)
    capital = pd.DataFrame(capital_list)
    engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test2?charset=utf8')
    capital.to_sql('quanter_firsthundredstock2017buywhenlargedeparture', engine, if_exists='append')
    return HttpResponse("查询数据成功.")



# 有每一天的收益率
def test_one_stock_buy_when_large_departure(request):
    # 利用均线趋势向下的背景里的负乖离买反弹，然后在接近向下均线的位置卖出
    data_service = StockDataService()
    # 获取股票
    all_stocks = data_service.get_stock_by_code('000685')

    for stock in all_stocks:
        print('处理stock: ', stock.name)
        # 获取股票的收盘价
        start_date = datetime.date(2014, 1, 1)
        end_date = datetime.date(2014, 12, 31)
        close_datas = data_service.get_stock_data(stock.code, start_date, end_date)
        print('close_datas: ', close_datas)

        # 计算ma20
        ma20_datas = close_datas['close'].rolling(20, 1).mean()
        ma_data = {'ma20': ma20_datas}
        ma_res = pd.DataFrame(data=ma_data, index=close_datas.index)
        # 计算乖离值
        ma_res['ma20_departure_value'] = ((close_datas['close'] - ma_res['ma20']) / ma_res['ma20']) * 100
        ma_res_round = ma_res.round(3)
        ma_res_round['close'] = close_datas['close']
        print('ma_res_round: ', ma_res_round)
        # 产生买卖信号
        prices_and_ma_related = ma_res_round[4:]
        buy_flag = np.where((prices_and_ma_related['close'] < prices_and_ma_related['ma20']) &
                            (prices_and_ma_related['ma20_departure_value'] <= -3.6), 1, 0)
        sell_flag = np.where((prices_and_ma_related['ma20_departure_value'] > 0) &
                             (prices_and_ma_related['ma20_departure_value'] < 15), -1, buy_flag)
        buy_and_sell_signal = pd.Series(sell_flag, prices_and_ma_related.index)
        print('buy_and_sell_signal: ', buy_and_sell_signal)
        # 计算三年的收益率
        asset_series = pd.Series(index=prices_and_ma_related.index)  # 资产数 asset
        asset = 100000.0
        hold_sum_series = pd.Series(index=prices_and_ma_related.index)  # 持有股票的数量
        hold_sum = 0
        daily_stock_yield_series = pd.Series(index=prices_and_ma_related.index)  # 每日收益率 daily_stock_yield
        date_index = prices_and_ma_related.index
        close_series = prices_and_ma_related['close']
        for i, x in enumerate(buy_and_sell_signal):
            # 买信号
            if x == 1:
                # 空仓，则买入
                if hold_sum == 0:
                    hold_sum = asset / close_series[date_index[i]]
                # 已经持有
                else:
                    asset = close_series[date_index[i]] * hold_sum
            elif x == -1:
                if hold_sum != 0:
                    asset = close_series[date_index[i]] * hold_sum
                    hold_sum = 0
            hold_sum_series[date_index[i]] = hold_sum
            asset_series[date_index[i]] = asset
            daily_stock_yield_series[date_index[i]] = 100 * (asset_series[date_index[i]] - 100000.0) / 100000.0
        capital = pd.DataFrame(data={'hold': hold_sum_series, 'asset': asset_series, 'yield': daily_stock_yield_series},
                               index=prices_and_ma_related.index)
        engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test2?charset=utf8')
        capital.to_sql('quanter_buylargedeparture2014', engine, if_exists='append')
        return HttpResponse("查询数据成功.")


def index(request):
    # start_date = datetime.date(2014, 1, 1)
    # end_date = datetime.date(2016, 12, 31)
    data_service = StockDataService()
    # data_df = data_service.get_stock_data('000685', start_date, end_date)
    # 计算2014-1-1到2016-12-31的乖离值并存入数据库
    three_k_strategy = ThreeKStrategy()
    # three_k_strategy.cal_departure_value(data_df)

    # 产生买卖信号
    prices_and_ma_related = data_service.get_ma_related_data()
    buy_and_sell_signal = three_k_strategy.generate_ma_and_departure_value_signal(prices_and_ma_related[4:])

    # 资产数 asset
    asset_series = pd.Series(index=buy_and_sell_signal.index)
    asset = 100000.0
    # 持有股票的数量 hold_num
    hold_sum_series = pd.Series(index=buy_and_sell_signal.index)
    hold_sum = 0
    # 每日收益率 daily_stock_yield
    daily_stock_yield_series = pd.Series(index=buy_and_sell_signal.index)
    date_index = prices_and_ma_related.index
    close_series = prices_and_ma_related['close']

    for i, x in enumerate(buy_and_sell_signal):
        # 买信号
        if x == 1:
            # 空仓，则买入
            if hold_sum == 0:
                hold_sum = asset/close_series[date_index[i]]
                # hold_sum_series[index[i]] = hold_sum
            # 已经持有
            else:
                asset = close_series[date_index[i]] * hold_sum
        elif x == -1:
            if hold_sum != 0:
                asset = close_series[date_index[i]] * hold_sum
                hold_sum = 0
        hold_sum_series[date_index[i]] = hold_sum
        asset_series[date_index[i]] = asset
        daily_stock_yield_series[date_index[i]] = 100 * (asset_series[date_index[i]] - 100000.0)/asset_series[date_index[i]]
    capital = pd.DataFrame(data={'hold': hold_sum_series, 'asset': asset_series, 'yield': daily_stock_yield_series},
                           index=buy_and_sell_signal.index)
    engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test2?charset=utf8')
    capital.to_sql('quanter_res_twentytwo', engine, if_exists='append')
    return HttpResponse("查询数据成功.")


def back_test(request):
    stat_date = '2018-03-23'
    end_date = '2018-03-25'
    stock_id_list = ['000001']
    three_k_strategy = ThreeKStrategy()
    # 计算每日的收益率
    daily_stock_yields = three_k_strategy.automatic_trade(stock_id_list)
    return HttpResponse(json.dumps({'stock_id_list': stock_id_list}), content_type="application/json")


def test_three_k(request):
    pass



