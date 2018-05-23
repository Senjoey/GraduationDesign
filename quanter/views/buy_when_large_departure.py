from quanter.models import TqStrategySetting


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
    large_negative_departure = get_negative_departure()
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


def get_negative_departure():
    setting = TqStrategySetting.objects.all()[0]
    return setting.negative_departure


def get_stop_profit():
    setting = TqStrategySetting.objects.all()[0]
    return setting.stop_profit


def get_stop_loss():
    setting = TqStrategySetting.objects.all()[0]
    return setting.stop_loss



