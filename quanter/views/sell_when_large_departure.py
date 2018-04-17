from django.http import HttpResponse
from quanter.stock_data import StockDataService
from quanter.models import TqBasicStockBool
import pandas as pd
import datetime
from sqlalchemy import create_engine


# 只有回测最后一天的收益率
def test_all_stock_sell_when_large_departure(request):
    # 利用均线趋势向下的背景里的负乖离买反弹，然后在接近向下均线的位置卖出
    print("test_all_stock_sell_when_large_departure")
    data_service = StockDataService()
    all_stocks = TqBasicStockBool.objects.all()

    capital_list = []

    for stock in all_stocks:
        print('处理stock: ', stock.name)
        # year = 2015
        ma_day = 20
        initial_asset = 100000.0
        start_date = datetime.date(2014, 1, 1)
        end_date = datetime.date(2014, 12, 31)
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
                    hold_num = 0
                elif is_need_stopping_profit(latest_buy_close, close_series[today]):
                    hold_num = 0

            # 需要止损也卖出 未实现
            # 需要止盈也卖出 未实现
            # 不持有股票（默认有资金？）
            # 达到买的型态买进
            else:
                if is_buy_state(close_series[today], open_series[today], close_series[yesterday], open_series[yesterday],
                                ma20_series_round[today], departure_series[today]):
                    hold_num = asset / close_series[today]
                    latest_buy_close = close_series[today]
        stock_yield = 100 * (asset - initial_asset) / initial_asset
        capital_item = {'code': stock.code, 'name': stock.name, 'yield': stock_yield}
        print('处理stock: ', capital_item)
        capital_list.append(capital_item)
    capital = pd.DataFrame(capital_list)
    engine = create_engine('mysql+mysqlconnector://root:tanxiaoqiong@127.0.0.1:3306/test4?charset=utf8')
    # engine = create_engine('mysql+mysqlconnector://root:liufengnju@114.212.242.143:3306/quanter?charset=utf8')
    table_name = 'quanter_tq_sell_when_large_departure_strategy_one'
    capital.to_sql(table_name, engine, if_exists='append')
    return HttpResponse("查询数据成功.")


# 判断是否为阴线：close<open为阴线 测试
def is_yin_xian(close_price, open_price):
    return close_price < open_price


# 判断是否为阳线：close>open为阳线 测试
def is_yang_xian(close_price, open_price):
    return close_price > open_price


# 是否达到买的型态: 靠近均线的位置买入
# 判断一下是不是阳上阳，阳上阳买；
def is_buy_state(today_close, today_open, yesterday_close, yesterday_open, today_ma20, departure_value):
    if (today_close > today_ma20) & (departure_value <= 3.6) & (departure_value > 0) & is_yang_xian(today_close, today_open) & \
            is_yang_xian(yesterday_close, yesterday_open) & (today_close > yesterday_close):
        # print("满足买入型态！")
        return True
    return False


# 是否达到卖的型态：正乖离过大的位置卖出
def is_sell_state(departure_value):
    if departure_value >= 5:
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





