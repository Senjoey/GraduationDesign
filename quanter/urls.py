from django.urls import path

from quanter.views import three_k, buy_when_large_departure, sell_when_large_departure
from quanter import stock_pool

urlpatterns = [
    # 其他页面
    path('',  three_k.three_k_index, name='index'),
    path('stock_charts',  three_k.stock_charts, name='stock_charts'),
    path('strategy_introduction',  three_k.strategy_introduction, name='strategy_introduction'),

    path('stock_table',  three_k.stock_table, name='stock_table'),
    path('<str:code>/<int:operation>', three_k.check_stock, name='check_stock'),
    path('stock_mine',  three_k.stock_mine, name='stock_mine'),

    # 选择策略
    path('choose_strategy_one', three_k.choose_strategy_one, name="choose_strategy_one"),
    path('choose_strategy_two', three_k.choose_strategy_two, name="choose_strategy_two"),

    # 回测
    path('back_test_multi_code_sell_when_large_departure', three_k.back_test_multi_code_sell_when_large_departure, name="back_test_multi_code_sell_when_large_departure"),
    path('back_test_multi_code_buy_when_large_departure', three_k.back_test_multi_code_buy_when_large_departure, name="back_test_multi_code_buy_when_large_departure"),

    # 选股
    path('choose_stock', stock_pool.choose_stock, name='choose_stock'),
    path('test_all_stock_buy_when_large_departure', buy_when_large_departure.test_all_stock_buy_when_large_departure, name='test_all_stock_buy_when_large_departure'),
    path('test_all_stock_sell_when_large_departure', sell_when_large_departure.test_all_stock_sell_when_large_departure, name='test_all_stock_sell_when_large_departure'),

]


