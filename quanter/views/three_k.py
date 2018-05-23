from django.http import HttpResponse
from quanter.models import FilterStock2014, FilterStock2015, FilterStock2016, \
    FilterStock2017, TqStockPool, TqPoolYear, Stock, TqStrategySetting, StockProfit, BackTest, \
    BackTestTable
import pandas as pd
import json
import numpy as np
from sqlalchemy import create_engine
from django.shortcuts import render
from quanter import multi_back_test


def merge_three_year_yield(request):
    # 分别读取三年的收益率数据
    all_stocks = Stock.objects.all()
    data_query_set2014 = FilterStock2014.objects.all()
    data_query_set2015 = FilterStock2015.objects.all()
    data_query_set2016 = FilterStock2016.objects.all()
    data_query_set2017 = FilterStock2017.objects.all()
    code_list = []
    name_list = []
    profit2014_list = []
    profit2015_list = []
    profit2016_list = []
    profit2017_list = []

    for stock in all_stocks:
        code = stock.code
        code_list.append(code)
        name_list.append(stock.name)
        profit2014 = 0
        items = data_query_set2014.filter(code=code)
        if len(items) != 0:
            profit2014 = items[0].profit2014
        profit2014_list.append(profit2014)

        profit2015 = 0
        items = data_query_set2015.filter(code=code)
        if len(items) != 0:
            profit2015 = items[0].profit2015
        profit2015_list.append(profit2015)

        profit2016 = 0
        items = data_query_set2016.filter(code=code)
        if len(items) != 0:
            profit2016 = items[0].profit2016
        profit2016_list.append(profit2016)

        profit2017 = 0
        items = data_query_set2017.filter(code=code)
        if len(items) != 0:
            profit2017 = items[0].profit2017
        profit2017_list.append(profit2017)

    # 将数据写入数据库
    res_df = pd.DataFrame(data={"code": code_list, "name": name_list, "profit2014": profit2014_list, "profit2015": profit2015_list,
                                "profit2016": profit2016_list, "profit2017": profit2017_list})
    engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test3?charset=utf8')
    res_df.to_sql('quanter_stockprofit', engine, if_exists='append')
    return HttpResponse("合并数据成功.")

'''
主要的几个页面
'''


def three_k_index(request):
    strategy_set = TqStrategySetting.objects.all()[0]
    context = {'setting': strategy_set}

    return render(request, 'quanter/StrategySetting.html', context)


def stock_charts(request):
    # 查看当前strayegy
    objs = TqStockPool.objects

    # 获取我的自选股list
    query_set = list(objs.filter(isChecked=1))
    my_stock = []

    for obj in query_set:
        item = {}
        item['code'] = obj.code
        my_stock.append(item)

    raw_data = []
    back_test_res = BackTest.objects.all()
    back_test_start_date = str(back_test_res[0].date)
    back_test_end_date = str(back_test_res[len(back_test_res)-1].date)
    initial_money = back_test_res[0].left_money
    for test in back_test_res:
        raw_data.append([str(test.date), test.profit_series, test.flag])

    return render(request, 'quanter/StockCharts.html', {'my_stock_list': json.dumps(my_stock), 'list': raw_data,
                                                        'back_test_start_date': back_test_start_date,
                                                        'back_test_end_date': back_test_end_date,
                                                        'initial_money': initial_money})


def back_test_table(request):
    back_test_res = BackTest.objects.all()
    back_test_start_date = str(back_test_res[0].date)
    back_test_end_date = str(back_test_res[len(back_test_res) - 1].date)
    initial_money = back_test_res[0].left_money
    back_test_table_query_set = BackTestTable.objects.all()
    res_list = []
    for item in back_test_table_query_set:
        item.date = str(item.date)
        res_list.append(item)
    context = {'res_list': res_list, 'back_test_start_date': back_test_start_date,
               'back_test_end_date': back_test_end_date, 'initial_money': initial_money}
    return render(request, "quanter/BackTestTable.html", context)


def strategy_setting(request):
    strategy_set = TqStrategySetting.objects.all()[0]
    strategy_dict = {
        'negative_departure': strategy_set.negative_departure,
        'positive_departure': strategy_set.positive_departure,
        'stop_profit': strategy_set.stop_profit,
        'stop_loss': strategy_set.stop_loss
    }
    context = {'setting': strategy_set, 'strategyDict': json.dumps(strategy_dict)}

    return render(request, 'quanter/StrategySetting.html', context)


def strategy_introduction(request):
    return render(request, 'quanter/StrategyIntroduction.html')


def stock_table(request):
    pool = TqStockPool.objects.filter(isInPool=1)
    pool_date_objs = TqPoolYear.objects
    context = {'res_list': pool, 'pool_date': pool_date_objs.all()[0]}
    return render(request, 'quanter/StockTable.html', context)


def check_stock(request, code, operation):
    objs = TqStockPool.objects

    # 数据库操作，将对应股票从我的自选股中加入或删除
    if operation == 1:  # 股票池中的操作
        stock = objs.filter(code=code)[0]
        if stock.isChecked == 0:
            stock.isChecked = 1
        else:
            stock.isChecked = 0
        stock.save()
        context = {'res_list': objs.filter(isInPool=1),'pool_date': TqPoolYear.objects.all()[0]}
        return render(request, 'quanter/StockTable.html', context)
    else:  # 我的选股中的操作
        stock = objs.filter(code=code)[0]
        if stock.isInPool == 0:  # 删除该股票
            stock.delete()
        else:
            stock.isChecked = 0
            stock.save()
        context = {'res_list': objs.filter(isChecked=1), 'pool_date': TqPoolYear.objects.all()[0]}
        return render(request, 'quanter/StockMine.html', context)


def stock_mine(request):
    objs = TqStockPool.objects.filter(isChecked=1)
    context = {'res_list': objs}
    return render(request, 'quanter/StockMine.html', context)


'''
修改股票池筛选时间
'''


def change_filter_year(request):
    start_year = request.GET.get('start')
    end_year = request.GET.get('end')
    filter_date = TqPoolYear.objects.all()[0]
    filter_date.start_year = start_year
    filter_date.end_year = end_year
    filter_date.start_date = " "
    filter_date.end_date = " "
    filter_date.save()

    # 选取平均收益率排名前30的股票，且平均收益率大于10%
    year_list = []
    start = int(start_year)
    end = int(end_year)
    while start <= end:
        year_list.append("profit"+str(start))
        start += 1
    stock_profit_query_set = StockProfit.objects.all().values('code', 'name', 'profit2014', 'profit2015', 'profit2016', 'profit2017')
    stock_profit_df = pd.DataFrame(list(stock_profit_query_set))
    stock_profit_df.set_index('code', inplace=True)
    stock_profit_df.sort_index()
    profit_series = pd.Series(0.0, index=stock_profit_df.index)
    for profit_str in year_list:
        profit_series = profit_series + stock_profit_df[profit_str]
    profit_series = profit_series / len(year_list)
    stock_profit_df['avg_profit'] = profit_series

    sorted_stock_profit_df = stock_profit_df.sort_values("avg_profit", ascending=False)[0:30]  # 基于它排序过滤
    sorted_above_ten_avf_profit_df = sorted_stock_profit_df[sorted_stock_profit_df.avg_profit > 10]  # 过滤的结果
    is_in_pool_series = pd.Series(1, sorted_above_ten_avf_profit_df.index)
    is_checked_series = pd.Series(0, sorted_above_ten_avf_profit_df.index)
    res_df = pd.DataFrame(data={'name': sorted_above_ten_avf_profit_df['name'],
                                'profit': sorted_above_ten_avf_profit_df['avg_profit'],
                                'isInPool': is_in_pool_series,
                                'isChecked': is_checked_series}, index=sorted_above_ten_avf_profit_df.index)

    # 删除原有的股票池
    objs = TqStockPool.objects
    objs.all().delete()
    # 写入新的股票池
    engine = create_engine('mysql+mysqlconnector://root:liufengnju@114.212.242.143:3306/quanter?charset=utf8')
    table_name = 'quanter_tqstockpool'
    res_df.to_sql(table_name, engine, if_exists='append')

    context = {'res_list': objs.filter(isInPool=1), 'pool_date': filter_date}
    return render(request, 'quanter/StockTable.html', context)


def change_filter_date(request):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    filter_date = TqPoolYear.objects.all()[0]
    filter_date.start_year = " "
    filter_date.end_year = " "
    filter_date.start_date = start_date
    filter_date.end_date = end_date
    filter_date.save()
    #
    # # 对所有股票进行回测，将回测结果写入数据库
    stocks = Stock.objects.all()
    profit_list = []
    code_list = []
    name_list = []
    for stock in stocks:
        res_df = multi_back_test.multi_backtest(start_date, end_date, [stock.code], 100000.0)
        profit_series = res_df['profit_series']
        profit = profit_series[-1]
        print(profit)
        if profit is None:
            continue
        profit_list.append(np.round(profit, 2))
        code_list.append(stock.code)
        name_list.append(stock.name)
    res = pd.DataFrame(data={'code': code_list, 'profit': profit_list, 'name': name_list})
    engine = create_engine('mysql+mysqlconnector://root:liufengnju@114.212.242.143:3306/quanter?charset=utf8')
    table_name = 'quanter_filterstockpool'
    res.to_sql(table_name, engine, if_exists='append')
    # 从数据库读取收益，进行排序，返回结果
    res.set_index('code', inplace=True)
    res.sort_index()
    sorted_stock_profit_df = res.sort_values('profit', ascending=False)[0:30]  # 基于它排序过滤
    sorted_above_ten_stock_profit_df = sorted_stock_profit_df[sorted_stock_profit_df.profit > 10]  # 过滤的结果
    is_in_pool_series = pd.Series(1, sorted_above_ten_stock_profit_df.index)
    is_checked_series = pd.Series(0, sorted_above_ten_stock_profit_df.index)
    stock_pool_df = pd.DataFrame(data={
        'name': sorted_above_ten_stock_profit_df['name'],
        'profit': sorted_above_ten_stock_profit_df['profit'],
        'isInPool': is_in_pool_series,
        'isChecked': is_checked_series
    }, index=sorted_above_ten_stock_profit_df.index)

    # 删除原来的股票池
    objs = TqStockPool.objects
    objs.all().delete()
    # 写入新的股票池
    table_name = "quanter_tqsellwhenlargedeparturestrategyone"
    stock_pool_df.to_sql(table_name, engine, if_exists='append')
    context = {'res_list': objs.filter(isInPool=1), 'pool_date': filter_date}
    return render(request, 'quanter/StockTable.html', context)


'''
添加自选股
'''


def check_database(request):
    code = request.GET.get('code')
    stock_query_set = Stock.objects.filter(code=code)
    my_stock_query_set = TqStockPool.objects.filter(isChecked=1, code=code)
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
    pool_query_set = TqStockPool.objects.filter(code=code)
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
        new_stock = TqStockPool(code=code, name=name, profit=profit, isInPool=0, isChecked=1)
        new_stock.save()
    context = {'res_list': TqStockPool.objects.filter(isChecked=1)}
    return render(request, 'quanter/StockMine.html', context)


'''
修改策略设置
'''


def strategy_setting_modify(request):
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
    return render(request, 'quanter/StrategySetting.html', context)


'''
回测部分 
'''


def back_test_multi_code(request):
    # 获取参数
    code_to_test = request.GET.get('code').split(',')
    print('code_to_test: ', code_to_test)
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    total_money = float(request.GET.get('totalMoney'))
    res_df = multi_back_test.multi_backtest(start_date, end_date, code_to_test, total_money)
    multi_back_test.multi_backtest_database_operation(res_df)
    # 需要的数据
    date_list = []
    asset_list = []
    flag_list = []
    order_code_list = []
    order_name_list = []
    order_hold_num_list = []
    price_list = []
    profit_list = []
    left_money_list = []

    date_index = res_df.index
    asset_series = res_df['asset']
    flag_series = res_df['flag']
    order_code_series = res_df['order_code']
    order_name_series = res_df['order_name']
    order_hold_num_series = res_df['order_hold_num']
    price_series = res_df['price_series']
    profit_series = res_df['profit_series']
    left_money_series = res_df['left_money']
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
        left_money_list.append(left_money_series[today])
    data = {
        'date_list': date_list,
        'asset_list': asset_list,
        'flag_list': flag_list,
        'order_code_list': order_code_list,
        'order_name_list': order_name_list,
        'order_hold_num_list': order_hold_num_list,
        'price_list': price_list,
        'profit_list': profit_list,
        'left_money_list': left_money_list
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


def test_modify(request):
    stocks = Stock.objects.all()
    profit_list_2014 = []
    code_list = []
    for stock in stocks:
        res_df = multi_back_test.multi_backtest('2017-01-01', '2017-12-31', [stock.code], 100000.0)
        profit_series = res_df['profit_series']
        profit = profit_series[-1]
        print(profit)
        if profit is None:
            continue
        profit_list_2014.append(profit)
        code_list.append(stock.code)
        res_2014 = pd.DataFrame(data={"code": code_list, "profit2017": profit_list_2014})

        engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test3?charset=utf8')
        table_name = 'quanter_filterstock2017'
        res_2014.to_sql(table_name, engine, if_exists='append')
        profit_list_2014 = []
        code_list = []
    return HttpResponse("Success!")


def test_key_modify(request):
    multi_back_test.multi_backtest("2014-01-01", "2014-12-31", ['000001', '000002'], 1000000.0)
    return HttpResponse("Success!")






















