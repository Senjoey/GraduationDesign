from quanter.stock_data import StockDataService
import pandas as pd
import datetime
from sqlalchemy import create_engine
from quanter.views import sell_when_large_departure, buy_when_large_departure
from quanter.models import Stock, Dailydata, BackTest, BackTestTable


def multi_backtest(start, end, code_to_test, total_money):
    stock_list_to_test = []
    stock_list = []
    data_service = StockDataService()
    for code in code_to_test:
        print(len(Stock.objects.filter(code=code)))
        stock_list_to_test.append(Stock.objects.filter(code=code)[0])
    hold_stock = []

    ma_day = 20
    initial_asset = total_money
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()

    close_series_dict = {}
    open_series_dict = {}
    ma20_series_round_dict = {}
    departure_series_dict = {}
    # 数据重新清洗一下 取来一段时间的数据，如果中间数据有缺失，补上
    # 获取大盘在回测区间数据
    hs300_history_prices = data_service.get_stock_data_by_code("399300", start_date, end_date)
    df1 = pd.DataFrame(list(Dailydata.objects.filter(code="399300", date__range=[start_date, end_date]).values("date")))
    for stock in stock_list_to_test:
        history_prices = Dailydata.objects.filter(code=stock.code, date__range=[start_date, end_date])
        if len(history_prices) <= 20:  # 数据太少，淘汰这支股票，如果最后一支股票都没有 返回收益率0
            continue
        df2 = pd.DataFrame(list(history_prices.values("date", "open", "close")))
        df = pd.merge(df1, df2, how="left", on="date")
        df.set_index('date', inplace=True)
        df.sort_index()
        df.fillna(0, inplace=True)
        stock_list.append(stock)

        close_series = pd.Series(df['close'], df.index)
        close_series_dict[stock.code] = close_series

        open_series = pd.Series(df['open'], df.index)
        open_series_dict[stock.code] = open_series

        ma20 = close_series.rolling(ma_day, 1).mean()
        ma20_round_series = ma20.round(3)
        ma20_series_round_dict[stock.code] = ma20_round_series

        departure = ((close_series - ma20_round_series) / ma20_round_series) * 100
        departure_series_dict[stock.code] = pd.Series(departure, df.index)

    # 如果没有股票满足条件，直接返回结果
    if len(stock_list) == 0:
        print("profit: ", 0)
        data = {'order_code': '无', 'order_name': '无', 'profit_series': 0,
            'order_hold_num': 0, 'flag': ' ', 'asset': 0,
            'left_money': 0, 'price_series': 0}
        res_df = pd.DataFrame(data=data, index=hs300_history_prices.index)
        return res_df
        # engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test3?charset=utf8')
        # table_name = 'quanter_backtest'
        # res_df.to_sql(table_name, engine, if_exists='append')

    # hold_stock[]持有股票的列表{'000685': 50000} 一次只持有一只股票
    # stock_to_test[] 待回测股票的列表，获取相应股票的名称
    #
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
    profit_money_series = pd.Series(0.0, date_index)
    per_profit_series = pd.Series(0.0, date_index)
    left_money = initial_asset
    asset = 0
    hold_num = 0.0
    asset_series = pd.Series(0.0, date_index)
    left_money_series = pd.Series(initial_asset, date_index)
    price_series = pd.Series(0.0, date_index)
    latest_buy_close = 0.0
    buy_standard_flag = -1  # 标准1为正乖离大卖出，标准2为负乖离大买入
    sell_flag = -1  # -1为未满足卖出条件，1为满足卖出条件

    for i, x in enumerate(close_series_dict[any_code]):
        if i < ma_day - 1:  # 从第20天开始
            continue
        today = date_index[i]
        yesterday_i = i - 1
        yesterday = date_index[yesterday_i]
        the_day_before_yesterday_i = i - 2
        the_day_before_yesterday = date_index[the_day_before_yesterday_i]
        print("today", today)
        if len(hold_stock) == 0:  # 持有的股票为空：
            for stock in stock_list:
                # 获取相应股票的close_series, open_series, departure_series
                code = stock.code
                # 判断今天是否可以交易，close数据不为0视为可交易，close数据为0视为不可交易
                if close_series_dict[code][today] <= 0.0:  # 不可交易，跳过这一天
                    print("今天不可交易")
                    continue
                else:  # 今天可以交易获取昨天和前天的数据，要跳过数据为0的日期
                    while close_series_dict[code][yesterday] <= 0.0:
                        print("往前推一天获取昨天数据")
                        yesterday_i -= 1
                        yesterday = date_index[yesterday_i]
                        the_day_before_yesterday_i = yesterday_i - 1
                        the_day_before_yesterday = date_index[the_day_before_yesterday_i]
                    while close_series_dict[code][the_day_before_yesterday] <= 0.0:
                        print("往前推一天获取前天数据")
                        the_day_before_yesterday_i -= 1
                        the_day_before_yesterday = date_index[the_day_before_yesterday_i]

                if sell_when_large_departure.is_buy_state(close_series_dict[code][today], open_series_dict[code][today],
                                                          close_series_dict[code][yesterday],
                                                          open_series_dict[code][yesterday],
                                                          ma20_series_round_dict[code][today],
                                                          departure_series_dict[code][today]):
                    flag_series[today] = "标准1买入"
                    buy_standard_flag = 1
                    print("标准1buy!!today: ", today, ' code: ', code)
                elif buy_when_large_departure.is_buy_state(close_series_dict[code][today],
                                                           open_series_dict[code][today],
                                                           close_series_dict[code][yesterday],
                                                           open_series_dict[code][yesterday],
                                                           close_series_dict[code][the_day_before_yesterday],
                                                           open_series_dict[code][the_day_before_yesterday],
                                                           departure_series_dict[code][today]):

                    flag_series[today] = "标准2买入"
                    buy_standard_flag = 2
                    print("标准2buy!!today: ", today, ' code: ', code)
                if buy_standard_flag != -1:  # 满足任一买入标准
                    hold_stock.append({'code': code, 'name': stock.name})
                    order_code_series[today] = code
                    order_name_series[today] = stock.name
                    order_hold_num_series[today] = int(left_money / close_series_dict[code][today])
                    hold_num = order_hold_num_series[today]
                    left_money -= hold_num * close_series_dict[code][today]
                    asset = hold_num * close_series_dict[code][today]
                    price_series[today] = close_series_dict[code][today]
                    latest_buy_close = close_series_dict[code][today]
                    buy_standard_flag = -1  # 重置
                    break

        else:  # 持有的股票不为空：
            for item in hold_stock:
                code = item['code']
                name = item['name']
                if close_series_dict[code][today] <= 0.0:  # 不可交易，跳过这一天
                    print("今天不可交易")
                    continue

                asset = close_series_dict[code][today] * hold_num
                if (buy_standard_flag == 1) & sell_when_large_departure.is_sell_state(
                        departure_series_dict[code][today]):
                    flag_series[today] = "标准1卖出"
                    sell_flag = 1
                elif (buy_standard_flag == 2) & buy_when_large_departure.is_sell_state(
                        departure_series_dict[code][today]):
                    flag_series[today] = "标准2卖出"
                    sell_flag = 1
                elif sell_when_large_departure.is_need_stopping_profit(latest_buy_close,
                                                                       close_series_dict[code][today]):
                    flag_series[today] = "止盈卖出"
                    sell_flag = 1
                elif sell_when_large_departure.is_need_stopping_loss(latest_buy_close, close_series_dict[code][today]):
                    flag_series[today] = "止损卖出"
                    sell_flag = 1
                else:  # 继续持有
                    order_code_series[today] = order_code_series[yesterday]
                    order_name_series[today] = order_name_series[yesterday]
                    order_hold_num_series[today] = hold_num
                if sell_flag != -1:  # 满足卖出条件
                    hold_stock.pop()
                    order_code_series[today] = code
                    order_name_series[today] = name
                    order_hold_num_series[today] = 0.0
                    left_money += asset
                    asset = 0
                    price_series[today] = close_series_dict[code][today]
                    profit_money_series[today] = (close_series_dict[code][today] - latest_buy_close) * \
                                                 order_hold_num_series[yesterday]
                    per_profit_series[today] = profit_money_series[today] / (latest_buy_close * order_hold_num_series[yesterday])
                    hold_num = 0.0
                    sell_flag = -1
        # 买和卖所共有的
        asset_series[today] = asset
        left_money_series[today] = left_money
        profit_series[today] = 100 * (asset + left_money - initial_asset) / initial_asset
    profit = 100 * (asset + left_money - initial_asset) / initial_asset
    print("profit: ", profit)
    data = {'order_code': order_code_series, 'order_name': order_name_series, 'profit_series': profit_series.round(2),
            'order_hold_num': order_hold_num_series, 'flag': flag_series, 'asset': asset_series.round(2),
            'left_money': left_money_series.round(2), 'price_series': price_series, 'profit_money': profit_money_series.round(2),
            'per_profit': per_profit_series.round(2)}
    res_df = pd.DataFrame(data=data, index=date_index)
    return res_df


def multi_backtest_database_operation(res_df):
    engine = create_engine('mysql+mysqlconnector://root:liufengnju@114.212.242.143:3306/quanter?charset=utf8')
    table_name = 'quanter_backtest'
    BackTest.objects.all().delete()
    res_df.to_sql(table_name, engine, if_exists='append')

    table_name = 'quanter_backtesttable'
    BackTestTable.objects.all().delete()
    res_operation_df = res_df[res_df.price_series > 0.0]
    res_operation_df.to_sql(table_name, engine, if_exists='append')



