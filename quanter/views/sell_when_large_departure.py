from quanter.models import TqStrategySetting


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
    if departure_value >= get_positive_departure():
        return True
    return False


# 是否需要止损
def is_need_stopping_loss(latest_close, today_close):
    # 止损：相对买入时候跌破2%
    if (today_close - latest_close)/latest_close <= -get_stop_loss():
        print("需要止损！")
        return True
    return False


# 是否需要止盈
def is_need_stopping_profit(latest_close, today_close):
    if (today_close - latest_close)/latest_close >= get_stop_profit():
        print("需要止盈！")
        return True
    return False


def get_positive_departure():
    setting = TqStrategySetting.objects.all()[0]
    return setting.positive_departure


def get_stop_profit():
    setting = TqStrategySetting.objects.all()[0]
    return setting.stop_profit


def get_stop_loss():
    setting = TqStrategySetting.objects.all()[0]
    return setting.stop_loss





