from django.urls import path

from quanter.views import three_k, buy_when_large_departure, sell_when_large_departure, pointtest
from quanter import stock_pool

urlpatterns = [
    # 其他页面
    path('',  three_k.three_k_index, name='index'),
    path('stock_charts',  three_k.stock_charts, name='stock_charts'),
    path('back_test_table',  three_k.back_test_table, name='back_test_table'),
    path('strategy_setting', three_k.strategy_setting, name='strategy_setting'),
    path('strategy_introduction', three_k.strategy_introduction, name='strategy_introduction'),

    path('stock_table',  three_k.stock_table, name='stock_table'),
    path('<str:code>/<int:operation>', three_k.check_stock, name='check_stock'),
    path('stock_mine',  three_k.stock_mine, name='stock_mine'),

    # 修改股票池筛选时间
    path('change_filter_year', three_k.change_filter_year, name='change_filter_year'),
    path('change_filter_date', three_k.change_filter_date, name='change_filter_date'),

    # 添加自选股
    path('check_database', three_k.check_database, name='check_database'),
    path('add_my_stock', three_k.add_my_stock, name='add_my_stock'),

    # 策略设置
    path('strategy_setting_modify', three_k.strategy_setting_modify, name="strategy_setting_modify"),

    # 回测
    path('back_test_multi_code', three_k.back_test_multi_code, name="back_test_multi_code"),

    # 选股
    path('choose_stock', stock_pool.choose_stock, name='choose_stock'),
    path('test_all_stock_sell_when_large_departure', sell_when_large_departure.test_all_stock_sell_when_large_departure, name='test_all_stock_sell_when_large_departure'),
    path('test_all_stock_buy_when_large_departure', buy_when_large_departure.test_all_stock_buy_when_large_departure, name='test_all_stock_buy_when_large_departure'),

    # 测试Point One
    path('test_one_point', pointtest.test_one_point, name="test_one_point"),
    path('test_two_point', pointtest.test_two_point, name="test_two_point"),
    path('test_modify', three_k.test_modify, name="test_modify"),
    path('test_key_modify', three_k.test_key_modify, name="test_key_modify"),
    path('merge_three_year_yield', three_k.merge_three_year_yield, name="merge_three_year_yield"),
]


