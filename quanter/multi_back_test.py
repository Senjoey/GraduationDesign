from django.http import HttpResponse
from quanter.stock_data import StockDataService
import pandas as pd
import datetime
from sqlalchemy import create_engine
from quanter.views import sell_when_large_departure, buy_when_large_departure


# 测试股票池 选出三年下来收益较高的
def multi_test_buy_when_large_departure(start, end, code_to_test):
    print("buy_when_large_departure")
    stock_list_to_test = []
    data_service = StockDataService()
    for code in code_to_test:
        stock_list_to_test.append(data_service.get_stock_by_code(code)[0])
    hold_stock = []

    ma_day = 20
    initial_asset = 100000.0
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()

    history_prices_dict = {}
    close_series_dict = {}
    open_series_dict = {}
    ma20_series_round_dict = {}
    departure_series_dict = {}

    for stock in stock_list_to_test:
        history_prices = data_service.get_stock_data_by_code(stock.code, start_date, end_date)
        history_prices_dict[stock.code] = history_prices

        close_series = pd.Series(history_prices['close'], history_prices.index)
        close_series_dict[stock.code] = close_series
        print("type(close_series): ", type(close_series))

        open_series = pd.Series(history_prices['open'], history_prices.index)
        open_series_dict[stock.code] = open_series

        ma20_series = history_prices['close'].rolling(ma_day, 1).mean()
        ma20_series_round = ma20_series.round(3)
        ma20_series_round_dict[stock.code] = ma20_series_round

        departure_series = ((close_series - ma20_series_round) / ma20_series_round) * 100
        departure_series_dict[stock.code] = departure_series

    # hold_stock[]持有股票的列表{'000685': 50000} 一次只持有一只股票
    # stock_to_test[] 待回测股票的列表，获取相应股票的名称

    # 在每一天中循环：
    #    持有的股票为空：
    #       对待回测股票列表逐个判断，是否达到买入型态，是，则买入达到买入型态的股票
    #    持有的股票不为空：
    #       对持有的股票进行判断，是否达到卖出型态，是，则卖出达到卖出型态的股票
    # for i, x in enumerate()

    # any_code = code_to_test[0]
    # date_index = close_series_dict[any_code].index

    # 选择天数最少的股票作为日期索引
    any_code = code_to_test[0]
    # min_date_index = close_series_dict[any_code].index
    # for code in code_to_test:
    #     if len(close_series_dict[code].index) < len(min_date_index):
    #         min_date_index = close_series_dict[code].index
    date_index = close_series_dict[any_code].index
    print("len(date_index): ", len(date_index))
    print(date_index)

    order_code_series = pd.Series(" ", date_index)
    order_name_series = pd.Series(" ", date_index)
    order_hold_num_series = pd.Series(0.0, date_index)
    flag_series = pd.Series(" ", date_index)
    profit_series = pd.Series(0.0, date_index)
    asset = initial_asset
    hold_num = 0.0
    asset_series = pd.Series(initial_asset, date_index)
    price_series = pd.Series(0.0, date_index)

    for i, x in enumerate(close_series_dict[any_code]):
        if i < ma_day - 1:  # 从第20天开始
            continue
        today = date_index[i]
        yesterday_i = i - 1
        yesterday = date_index[yesterday_i]
        the_day_before_yesterday_i = i - 2
        the_day_before_yesterday = date_index[the_day_before_yesterday_i]

        if not hold_stock:  # 持有的股票为空：
            for stock in stock_list_to_test:
                # 获取相应股票的close_series, open_series, departure_series
                code = stock.code
                if buy_when_large_departure.is_buy_state(close_series_dict[code][today], open_series_dict[code][today],
                                close_series_dict[code][yesterday], open_series_dict[code][yesterday],
                                close_series_dict[code][the_day_before_yesterday], open_series_dict[code][the_day_before_yesterday],
                                departure_series_dict[code][today]):
                    hold_stock.append(code)
                    order_code_series[today] = code
                    order_name_series[today] = stock.name
                    order_hold_num_series[today] = asset / close_series_dict[code][today]
                    hold_num = order_hold_num_series[today]
                    flag_series[today] = "买入"
                    price_series[today] = close_series_dict[code][today]
                    print("buy!!today: ", today, ' code: ', code)
                    break
        else:  # 持有的股票不为空：
            for code in hold_stock:
                asset = close_series_dict[code][today] * hold_num
                if buy_when_large_departure.is_sell_state(departure_series_dict[code][today]):
                    hold_stock.remove(code)
                    flag_series[today] = "卖出"
                    order_code_series[today] = " "
                    order_name_series[today] = " "
                    order_hold_num_series[today] = 0.0
                    hold_num = 0.0
                    price_series[today] = close_series_dict[code][today]
                else:
                    order_code_series[today] = order_code_series[yesterday]
                    order_name_series[today] = order_name_series[yesterday]
                    order_hold_num_series[today] = hold_num
                    price_series[today] = close_series_dict[code][today]
        asset_series[today] = asset
        profit_series[today] = 100 * (asset - initial_asset) / initial_asset
    profit = 100 * (asset - initial_asset) / initial_asset
    print("profit: ", profit)
    data = {'order_code': order_code_series, 'order_name': order_name_series, 'profit_series': profit_series,
            'order_hold_num': order_hold_num_series, 'flag': flag_series, 'asset': asset_series, 'price_series': price_series}
    res_df = pd.DataFrame(data=data, index=date_index)
    engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test4?charset=utf8')
    table_name = 'quanter_multibuy' + start
    res_df.to_sql(table_name, engine, if_exists='append')
    # return res_df
    return HttpResponse('获取数据成功！')


# 待测试 测试之后选出三年下来收益最高的
def multi_test_sell_when_large_departure(start, end, code_to_test, total_money):
    stock_list_to_test = []
    data_service = StockDataService()
    for code in code_to_test:
        stock_list_to_test.append(data_service.get_stock_by_code(code)[0])
    hold_stock = []

    ma_day = 20
    initial_asset = total_money
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()

    history_prices_dict = {}
    close_series_dict = {}
    open_series_dict = {}
    ma20_series_round_dict = {}
    departure_series_dict = {}

    for stock in stock_list_to_test:
        history_prices = data_service.get_stock_data_by_code(stock.code, start_date, end_date)
        history_prices_dict[stock.code] = history_prices

        close_series = pd.Series(history_prices['close'], history_prices.index)
        close_series_dict[stock.code] = close_series
        # print("type(close_series): ", type(close_series))

        open_series = pd.Series(history_prices['open'], history_prices.index)
        open_series_dict[stock.code] = open_series

        ma20_series = history_prices['close'].rolling(ma_day, 1).mean()
        ma20_series_round = ma20_series.round(3)
        ma20_series_round_dict[stock.code] = ma20_series_round

        departure_series = ((close_series - ma20_series_round) / ma20_series_round) * 100
        departure_series_dict[stock.code] = departure_series

    # hold_stock[]持有股票的列表{'000685': 50000} 一次只持有一只股票
    # stock_to_test[] 待回测股票的列表，获取相应股票的名称

    # 在每一天中循环：
    #    持有的股票为空：
    #       对待回测股票列表逐个判断，是否达到买入型态，是，则买入达到买入型态的股票
    #    持有的股票不为空：
    #       对持有的股票进行判断，是否达到卖出型态，是，则卖出达到卖出型态的股票

    any_code = code_to_test[0]
    date_index = close_series_dict[any_code].index

    order_code_series = pd.Series(" ", date_index)
    order_name_series = pd.Series(" ", date_index)
    order_hold_num_series = pd.Series(0.0, date_index)
    flag_series = pd.Series(" ", date_index)
    profit_series = pd.Series(0.0, date_index)
    asset = initial_asset
    hold_num = 0.0
    asset_series = pd.Series(initial_asset, date_index)
    price_series = pd.Series(0.0, date_index)
    latest_buy_close = 0.0

    for i, x in enumerate(close_series_dict[any_code]):
        if i < ma_day - 1:  # 从第20天开始
            continue
        today = date_index[i]
        yesterday_i = i - 1
        yesterday = date_index[yesterday_i]
        the_day_before_yesterday_i = i - 2
        the_day_before_yesterday = date_index[the_day_before_yesterday_i]

        if not hold_stock:  # 持有的股票为空：
            for stock in stock_list_to_test:
                # 获取相应股票的close_series, open_series, departure_series
                code = stock.code
                if sell_when_large_departure.is_buy_state(close_series_dict[code][today], open_series_dict[code][today],
                                                          close_series_dict[code][yesterday], open_series_dict[code][yesterday],
                                                          ma20_series_round_dict[code][today],departure_series_dict[code][today]):
                    hold_stock.append(code)
                    order_code_series[today] = code
                    order_name_series[today] = stock.name
                    order_hold_num_series[today] = asset / close_series_dict[code][today]
                    hold_num = order_hold_num_series[today]
                    flag_series[today] = "买入"
                    price_series[today] = close_series_dict[code][today]
                    latest_buy_close = close_series_dict[code][today]
                    print("buy!!today: ", today, ' code: ', code)
                    break
        else:  # 持有的股票不为空：
            for code in hold_stock:
                asset = close_series_dict[code][today] * hold_num
                if sell_when_large_departure.is_sell_state(departure_series_dict[code][today]) | \
                        sell_when_large_departure.is_need_stopping_profit(latest_buy_close, close_series_dict[code][today]) | \
                        sell_when_large_departure.is_need_stopping_loss(latest_buy_close, close_series_dict[code][today]):
                    hold_stock.remove(code)
                    flag_series[today] = "卖出"
                    order_code_series[today] = " "
                    order_name_series[today] = " "
                    order_hold_num_series[today] = 0.0
                    hold_num = 0.0
                    price_series[today] = close_series_dict[code][today]
                else:
                    order_code_series[today] = order_code_series[yesterday]
                    order_name_series[today] = order_name_series[yesterday]
                    order_hold_num_series[today] = hold_num
                    price_series[today] = close_series_dict[code][today]
        asset_series[today] = asset
        profit_series[today] = 100 * (asset - initial_asset) / initial_asset
    profit = 100 * (asset - initial_asset) / initial_asset
    print("profit: ", profit)
    data = {'order_code': order_code_series, 'order_name': order_name_series, 'profit_series': profit_series,
            'order_hold_num': order_hold_num_series, 'flag': flag_series, 'asset': asset_series, 'price_series': price_series}
    res_df = pd.DataFrame(data=data, index=date_index)
    engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test4?charset=utf8')
    table_name = 'quanter_multisell' + start
    res_df.to_sql(table_name, engine, if_exists='append')
    return res_df





