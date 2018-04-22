from django.http import HttpResponse
from quanter.stock_data import StockDataService
from quanter.three_k_strategy import ThreeKStrategy
from quanter.models import FirstHundredStock2014yield, FirstHundredStock2015yield, FirstHundredStock2016yield, \
    FirstHundredStock2017yield, FirstHundredStock2018yield, TqSellWhenLargeDepartureStrategyOne, TqPoolDate, Stock, TqStrategySetting
import pandas as pd
import json
import datetime
import numpy as np
from sqlalchemy import create_engine
from django.shortcuts import render
from quanter import multi_back_test


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
        start_date = datetime.date(2014, 1, 1)
        end_date = datetime.date(2016, 12, 31)
        close_datas = data_service.get_stock_data(stock.code, start_date, end_date)
        if len(close_datas) == 0:
            stock_yield = 0
            capital_item = {'code': stock.code, 'name': stock.name, 'yield': stock_yield}
            print('处理stock: ', capital_item)
            capital_list.append(capital_item)
            continue

        # print('close_datas的大小: ', len(close_datas))

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
        start_date = datetime.date(2014, 1, 1)
        end_date = datetime.date(2014, 12, 31)
        close_datas = data_service.get_stock_data(stock.code, start_date, end_date)
        if len(close_datas) == 0:
            stock_yield = 0
            capital_item = {'code': stock.code, 'name': stock.name, 'yield2014': stock_yield}
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
        sell_flag = np.where((prices_and_ma_related['ma20_departure_value'] > -1), -1, buy_flag)
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
        capital_item = {'code': stock.code, 'name': stock.name, 'yield2014': stock_yield}
        print('处理stock: ', capital_item)
        capital_list.append(capital_item)
    capital = pd.DataFrame(capital_list)
    engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test2?charset=utf8')
    capital.to_sql('quanter_firsthundredstock2014buywhenlargedeparturetry', engine, if_exists='append')
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
        start_date = datetime.date(2017, 1, 1)
        end_date = datetime.date(2017, 12, 31)
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
        sell_flag = np.where(prices_and_ma_related['ma20_departure_value'] > -1, -1, buy_flag)
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
        capital.to_sql('quanter_buylargedeparture2017one', engine, if_exists='append')
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


'''
主要的几个页面
'''


def three_k_index(request):
    strategy_set = TqStrategySetting.objects.all()[0]
    context = {'setting': strategy_set}
    return render(request, 'quanter/StrategyIntroduction.html', context)


def stock_charts(request):
    # 查看当前strayegy
    # current_strategy = tqcurrentstrategy.objects.all()[0]
    objs = TqSellWhenLargeDepartureStrategyOne.objects
    # if current_strategy.strategy_num == 2:
    #     print('当前是策略二！')
    #     objs = tq_buy_when_large_departure_strategy_two.objects

    # 获取我的自选股list
    query_set = list(objs.filter(isInPool=1, isChecked=1))
    my_stock = []

    for obj in query_set:
        item = {}
        item['code'] = obj.code
        my_stock.append(item)

    raw_data = []
    # for day_data in zhong_shan_gong_yong:
    raw_data.append(['2017-01-01', 0])
    raw_data.append(['2017-01-02', 0])
    raw_data.append(['2017-01-03', 0])
    return render(request, 'quanter/StockCharts.html', {'my_stock_list': json.dumps(my_stock), 'list': raw_data})


def strategy_introduction(request):
    strategy_set = TqStrategySetting.objects.all()[0]
    context = {'setting': strategy_set}
    return render(request, 'quanter/StrategyIntroduction.html', context)


def stock_table(request):
    objs = TqSellWhenLargeDepartureStrategyOne.objects
    pool_date_objs = TqPoolDate.objects
    context = {'res_list': objs.filter(isInPool=1), 'pool_date': pool_date_objs.all()[0]}
    return render(request, 'quanter/StockTable.html', context)


def check_stock(request, code, operation):
    # current_strategy = tqcurrentstrategy.objects.all()[0]
    objs = TqSellWhenLargeDepartureStrategyOne.objects
    # if current_strategy.strategy_num == 2:
    #     print('当前是策略二！')
    #     objs = tq_buy_when_large_departure_strategy_two.objects

    # 数据库操作，将对应股票从我的自选股中加入或删除
    if operation == 1:  # 股票池中的操作
        stock = objs.filter(code=code)[0]
        if stock.isChecked == 0:
            stock.isChecked = 1
        else:
            stock.isChecked = 0
        stock.save()
        context = {'res_list': objs.filter(isInPool=1)}
        return render(request, 'quanter/StockTable.html', context)
    else:  # 我的选股中的操作
        stock = objs.filter(code=code)[0]
        if stock.isInPool == 0:  # 删除该股票
            stock.delete()
        else:
            stock.isChecked = 0
            stock.save()
        context = {'res_list': objs.filter(isChecked=1)}
        return render(request, 'quanter/StockMine.html', context)


def stock_mine(request):
    # current_strategy = tqcurrentstrategy.objects.all()[0]
    objs = TqSellWhenLargeDepartureStrategyOne.objects
    # if current_strategy.strategy_num == 2:
    #     objs = tq_buy_when_large_departure_strategy_two.objects

    context = {'res_list': objs.filter(isChecked=1)}
    return render(request, 'quanter/StockMine.html', context)


'''
修改股票池筛选时间
'''


def change_filter_time(request):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    filter_date = TqPoolDate.objects.all()[0]
    filter_date.start_date = start_date
    filter_date.end_date = end_date
    filter_date.save()

    # 重新运行策略选股，选取排名前30的股票，且年化收益率大于10%
    objs = TqSellWhenLargeDepartureStrategyOne.objects
    context = {'res_list': objs.filter(isInPool=1), 'pool_date': filter_date}
    return render(request, 'quanter/StockTable.html', context)


'''
添加自选股
'''


def check_database(request):
    code = request.GET.get('code')
    stock_query_set = Stock.objects.filter(code=code)
    my_stock_query_set = TqSellWhenLargeDepartureStrategyOne.objects.filter(isChecked=1, code=code)
    is_in_stock = 1
    is_already_in_my_stock = 0
    if len(stock_query_set) == 0:
        is_in_stock = 0
    if len(my_stock_query_set) > 0:
        is_already_in_my_stock = 1
    res = {
        'is_in_stock': is_in_stock,
        'is_already_in_my_stock': is_already_in_my_stock
    }
    return HttpResponse(json.dumps(res), content_type='application/json')


def add_my_stock(request):
    code = request.GET.get('code')
    # 先看是否在股票池中
    pool_query_set = TqSellWhenLargeDepartureStrategyOne.objects.filter(code=code)
    # 在股票池中，直接修改股票池
    if len(pool_query_set) > 0:
        stock = pool_query_set[0]
        stock.isChecked = 1
        stock.save()
    # 不在股票池中，加一条数据到股票池
    else:
        stock_query_set = Stock.objects.filter(code=code)
        name = stock_query_set[0].name
        profit = 0.0  # 调用策略进行回测，算出筛选股票池期间的收益
        new_stock = TqSellWhenLargeDepartureStrategyOne(code=code, name=name, profit=profit, isInPool=0, isChecked=1)
        new_stock.save()
    context = {'res_list': TqSellWhenLargeDepartureStrategyOne.objects.filter(isChecked=1)}
    return render(request, 'quanter/StockMine.html', context)


'''
修改策略设置
'''


def strategy_setting(request):
    positive_departure = request.GET.get('positiveDeparture')
    negative_departure = request.GET.get('negativeDeparture')
    stop_profit = request.GET.get('stopProfit')
    stop_loss = request.GET.get('stopLoss')

    strategy_set = TqStrategySetting.objects.all()[0]
    strategy_set.positive_departure = positive_departure
    strategy_set.negative_departure = negative_departure
    strategy_set.stop_profit = stop_profit
    strategy_set.stop_loss = stop_loss
    strategy_set.save()

    context = {'setting': strategy_set}
    return render(request, 'quanter/StrategyIntroduction.html', context)

'''
选择策略部分
'''


# def choose_strategy_one(request):
#     current_strategy = tqcurrentstrategy.objects.all()[0]
#     current_strategy.strategy_num = 1
#     current_strategy.strategy_name = '策略一'
#     current_strategy.save()
#
#     objs = tq_sell_when_large_departure_strategy_one.objects
#     context = {'res_list': objs.filter(isInPool=1),  'strategy_name': current_strategy.strategy_name}
#     return render(request, 'quanter/StockTable.html', context)
#
#
# def choose_strategy_two(request):
#     current_strategy = tqcurrentstrategy.objects.all()[0]
#     current_strategy.strategy_num = 2
#     current_strategy.strategy_name = '策略二'
#     current_strategy.save()
#     objs = tq_buy_when_large_departure_strategy_two.objects
#     context = {'res_list': objs.filter(isInPool=1), 'strategy_name': current_strategy.strategy_name}
#     return render(request, 'quanter/StockTable.html', context)


'''
回测部分 
'''


def back_test_nulti_code(request):
    return back_test_multi_code_sell_when_large_departure(request)
    # print("In back_test_nulti_code")
    # current_strategy = tqcurrentstrategy.objects.all()[0]
    # if current_strategy.strategy_num == 1:
    #     return back_test_multi_code_sell_when_large_departure(request)
    # else:
    #     return back_test_multi_code_buy_when_large_departure(request)


# 利用均线趋势向上的背景买入，然后在正乖离大的位置卖出
def back_test_multi_code_sell_when_large_departure(request):
    print("====回测策略一：利用均线趋势向上的背景买入，然后在正乖离大的位置卖出====")
    # 获取参数
    code_to_test = request.GET.get('code').split(',')
    print("type(code_to_test): ", type(code_to_test))
    print('code_to_test: ', code_to_test)
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    total_money = float(request.GET.get('totalMoney'))
    res_df = multi_back_test.multi_test_sell_when_large_departure(start_date, end_date, code_to_test, total_money)
    # 需要的数据
    date_list = []
    asset_list = []
    flag_list = []
    order_code_list = []
    order_name_list = []
    order_hold_num_list = []
    price_list = []
    profit_list = []

    date_index = res_df.index
    asset_series = res_df['asset']
    flag_series = res_df['flag']
    order_code_series = res_df['order_code']
    order_name_series = res_df['order_name']
    order_hold_num_series = res_df['order_hold_num']
    price_series = res_df['price_series']
    profit_series = res_df['profit_series']
    for i, x in enumerate(price_series):
        today = date_index[i]
        date_list.append(str(today))
        asset_list.append(asset_series[today])
        flag_list.append(flag_series[today])
        order_code_list.append(order_code_series[today])
        order_name_list.append(order_name_series[today])
        order_hold_num_list.append(order_hold_num_series[today])
        price_list.append(x)
        profit_list.append(profit_series[today])
    data = {
        'date_list': date_list,
        'asset_list': asset_list,
        'flag_list': flag_list,
        'order_code_list': order_code_list,
        'order_name_list': order_name_list,
        'order_hold_num_list': order_hold_num_list,
        'price_list': price_list,
        'profit_list': profit_list
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


# 利用均线趋势向下的背景里的负乖离买反弹，然后在接近向下均线的位置卖出
def back_test_multi_code_buy_when_large_departure(request):
    print("====回测策略二：利用均线趋势向下的背景里的负乖离买反弹，然后在接近向下均线的位置卖出====")
    # 获取参数
    code_to_test = request.GET.get('code').split(',')
    print("type(code_to_test): ", type(code_to_test))
    print('code_to_test: ', code_to_test)
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    total_money = float(request.GET.get('totalMoney'))
    res_df = multi_back_test.multi_test_buy_when_large_departure(start_date, end_date, code_to_test, total_money)
    # 需要的数据
    date_list = []
    asset_list = []
    flag_list = []
    order_code_list = []
    order_name_list = []
    order_hold_num_list = []
    price_list = []
    profit_list = []

    date_index = res_df.index
    asset_series = res_df['asset']
    flag_series = res_df['flag']
    order_code_series = res_df['order_code']
    order_name_series = res_df['order_name']
    order_hold_num_series = res_df['order_hold_num']
    price_series = res_df['price_series']
    profit_series = res_df['profit_series']
    for i, x in enumerate(price_series):
        today = date_index[i]
        date_list.append(str(today))
        asset_list.append(asset_series[today])
        flag_list.append(flag_series[today])
        order_code_list.append(order_code_series[today])
        order_name_list.append(order_name_series[today])
        order_hold_num_list.append(order_hold_num_series[today])
        price_list.append(x)
        profit_list.append(profit_series[today])
    data = {
        'date_list': date_list,
        'asset_list': asset_list,
        'flag_list': flag_list,
        'order_code_list': order_code_list,
        'order_name_list': order_name_list,
        'order_hold_num_list': order_hold_num_list,
        'price_list': price_list,
        'profit_list': profit_list
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


















