from django.http import HttpResponse
from quanter.stock_data import StockDataService
from quanter.models import TqBasicStockBool
import pandas as pd
import datetime
from sqlalchemy import create_engine


# 只有回测最后一天的收益率
def test_all_stock_buy_when_large_departure(request):
    # 利用均线趋势向下的背景里的负乖离买反弹，然后在接近向下均线的位置卖出
    data_service = StockDataService()
    all_stocks = TqBasicStockBool.objects.all()
    # all_stocks = pd.DataFrame(list(data_query_set.values('code', 'name')))

    capital_list = []

    for stock in all_stocks:
        print('处理stock: ', stock.name)
        # year = 2015
        ma_day = 20
        initial_asset = 100000.0
        start_date = datetime.date(2014, 1, 1)
        end_date = datetime.date(2016, 12, 31)
        history_prices = data_service.get_stock_data_by_code(stock.code, start_date, end_date)
        # 获取股票的收盘价、收盘价，产生序列close_series、open_series
        close_series = pd.Series(history_prices['close'], history_prices.index)
        open_series = pd.Series(history_prices['open'], history_prices.index)
        # 计算ma20,产生一个Series: ma20_series
        ma20_series = history_prices['close'].rolling(ma_day, 1).mean()
        ma20_series_round = ma20_series.round(3)
        # 计算乖离值,产生一个Series: departure_series
        departure_series = ((close_series - ma20_series_round) / ma20_series_round) * 100

        hold_num = 0
        asset = initial_asset
        date_index = close_series.index
        latest_buy_close = 0.0
        for i, x in enumerate(close_series):
            if i < ma_day-1:  # 从第20天开始
                continue
            today = date_index[i]
            yesterday_i = i - 1
            yesterday = date_index[yesterday_i]
            the_day_before_yesterday_i = i - 2
            the_day_before_yesterday = date_index[the_day_before_yesterday_i]
            # 是否持有股票
            # 持有股票
            # 达到卖的型态卖出
            if hold_num != 0:
                asset = close_series[today] * hold_num
                if is_sell_state(departure_series[today]):
                    hold_num = 0
                elif is_need_stopping_loss(latest_buy_close, close_series[today]):
                    asset = close_series[today] * hold_num
                    hold_num = 0
                elif is_need_stopping_profit(latest_buy_close, close_series[today]):
                    hold_num = 0
            # 需要止损也卖出 未实现
            # 需要止盈也卖出 未实现
            # 不持有股票（默认有资金？）
            # 达到买的型态买进
            else:
                if is_buy_state(close_series[today], open_series[today], close_series[yesterday],
                                open_series[yesterday],
                                close_series[the_day_before_yesterday], open_series[the_day_before_yesterday],
                                departure_series[today]):
                    hold_num = asset / close_series[today]
                    latest_buy_close = close_series[today]
        stock_yield = 100 * (asset - initial_asset) / initial_asset
        capital_item = {'code': stock.code, 'name': stock.name, 'yield': stock_yield}
        print('处理stock: ', capital_item)
        capital_list.append(capital_item)
    capital = pd.DataFrame(capital_list)
    # engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test4?charset=utf8')
    engine = create_engine('mysql+mysqlconnector://root:liufengnju@114.212.242.143:3306/quanter?charset=utf8')
    table_name = 'quanter_tq_buy_when_large_departure_strategy_two'
    capital.to_sql(table_name, engine, if_exists='append')
    return HttpResponse("查询数据成功.")


# 有每一天的收益率
def test_one_stock_buy_when_large_departure(request):
    # 利用均线趋势向下的背景里的负乖离买反弹，然后在接近向下均线的位置卖出
    data_service = StockDataService()
    all_stocks = data_service.get_stock_by_code('000685')  # 获取股票

    for stock in all_stocks:
        print('处理stock: ', stock.name)
        year = 2016
        ma_day = 20
        initial_asset = 100000.0
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
        history_prices = data_service.get_stock_data_by_code(stock.code, start_date, end_date)
        # 获取股票的收盘价、收盘价，产生序列close_series、open_series
        close_series = pd.Series(history_prices['close'], history_prices.index)
        open_series = pd.Series(history_prices['open'], history_prices.index)
        # 计算ma20,产生一个Series: ma20_series
        ma20_series = history_prices['close'].rolling(ma_day, 1).mean()
        ma20_series_round = ma20_series.round(3)
        # 计算乖离值,产生一个Series: departure_series
        departure_series = ((close_series - ma20_series_round) / ma20_series_round) * 100
        profit_series = pd.Series(0.0, close_series.index)

        hold_num = 0
        hold_series = pd.Series(0.0, index=close_series.index)
        asset = initial_asset
        asset_series = pd.Series(initial_asset, index=close_series.index)
        flag_series = pd.Series(0, index=close_series.index)
        date_index = close_series.index
        latest_buy_close = 0.0
        for i, x in enumerate(close_series):
            if i < ma_day-1:  # 从第20天开始
                continue
            today = date_index[i]
            yesterday_i = i - 1
            yesterday = date_index[yesterday_i]
            the_day_before_yesterday_i = i - 2
            the_day_before_yesterday = date_index[the_day_before_yesterday_i]
            # 是否持有股票
            # 持有股票
            # 达到卖的型态卖出
            if hold_num != 0:
                asset = close_series[today] * hold_num
                if is_sell_state(departure_series[today]):
                    hold_num = 0
                    flag_series[today] = -1

                # elif is_need_stopping_loss(latest_buy_close * hold_num, close_series[today] * hold_num):
                #     asset = close_series[today] * hold_num
                #     hold_num = 0
                #     flag_series[today] = -2

            # 需要止损也卖出 未实现
            # 需要止盈也卖出 未实现
            # 不持有股票（默认有资金？）
            # 达到买的型态买进
            else:
                if is_buy_state(close_series[today], open_series[today], close_series[yesterday], open_series[yesterday],
                                close_series[the_day_before_yesterday], open_series[the_day_before_yesterday],
                                departure_series[today]):
                    hold_num = asset / close_series[today]
                    latest_buy_close = close_series[today]
                    flag_series[today] = 1
                    print('buy!! today: ', today, ' close: ', close_series[today], ' hold: ', asset / close_series[today], ' asset: ', asset)
            hold_series[today] = hold_num
            asset_series[today] = asset
            profit_series[today] = 100 * (asset_series[today] - initial_asset) / initial_asset
        data = {'close': close_series, 'departure': departure_series, 'flag': flag_series, 'hold_num': hold_series,
                'asset': asset_series, 'profit': profit_series}
        res_df = pd.DataFrame(data=data, index=close_series.index)
        engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test3?charset=utf8')
        table_name = 'quanter_zsgybuy'+str(year)
        res_df.to_sql(table_name, engine, if_exists='append')
        # print('asset_series: ', asset_series)
        # print('profit: ', profit_series)
        # my_departure = departure_series[19:]
        # departure_median = my_departure.median()
        # print('departure_median: ', departure_median)
        return HttpResponse("查询数据成功.")


# 判断是否为阴线：close<open为阴线 测试
def is_yin_xian(close_price, open_price):
    return close_price < open_price


# 判断是否为阳线：close>open为阳线 测试
def is_yang_xian(close_price, open_price):
    return close_price > open_price


# 是否达到卖的型态：靠近均线的位置卖出 测试
def is_sell_state(departure_value):
    if departure_value >= 0:
        return True
    return False


# 是否达到买的型态: 负乖离过大的位置买进 测试
# 判断一下是不是阴下阴，阴下阴不买；判断一下是不是阴下阴+止跌失败，不买【还没有跌够】
def is_buy_state(today_close, today_open, yesterday_close, yesterday_open, the_day_before_yesterday_close, the_day_before_yesterday_open, departure_value):
    large_negative_departure = -5
    # 今天阴，昨天阴，构成"阴下阴"
    if is_yin_xian(today_close, today_open) & is_yin_xian(yesterday_close, yesterday_open) & (today_close < yesterday_close):
        return False
    # 昨天阴，前天阴，昨天和前天构成阴下阴 & 今天和昨天没有构成止跌（止跌是今天的收盘价 > 昨天的收盘价）
    if is_yin_xian(the_day_before_yesterday_close, the_day_before_yesterday_open) & \
            is_yin_xian(yesterday_close, yesterday_open) & (yesterday_close < the_day_before_yesterday_close) & \
            (today_close < yesterday_close):
        return False
    if departure_value <= large_negative_departure:
        return True
    return False


# 是否需要止损
def is_need_stopping_loss(latest_close, today_close):
    # 止损：相对买入时候跌破2%
    if (today_close - latest_close)/latest_close <= -0.05:
        print("需要止损！")
        return True
    return False


# 是否需要止盈
def is_need_stopping_profit(latest_close, today_close):
    if (today_close - latest_close)/latest_close >= 0.2:
        print("需要止盈！")
        return True
    return False



