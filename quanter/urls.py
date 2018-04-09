from django.urls import path

from quanter.views import three_k, buy_when_large_departure
from quanter import multi_back_test

urlpatterns = [
    path('',  three_k.test_three_k, name='index'),
    path('stock_charts',  three_k.stock_charts, name='stock_charts'),
    path('strategy_introduction',  three_k.strategy_introduction, name='strategy_introduction'),

    path('stock_table',  three_k.stock_table, name='stock_table'),
    path('<str:code>/<int:operation>', three_k.check_stock, name='check_stock'),
    path('stock_mine',  three_k.stock_mine, name='stock_mine'),

    path('back_test_one_code', three_k.back_test_one_code, name="back_test_one_code"),
    path('back_test_multi_code', three_k.back_test_multi_code, name="back_test_multi_code"),

    path('test_all_stock', three_k.test_all_stock_sell_when_large_departure, name='test_all_stock'),
    path('test_all_stock_buy_when_large_departure', buy_when_large_departure.test_all_stock_buy_when_large_departure,
         name='test_all_stock_buy_when_large_departure'),
    path('test_one_stock', three_k.test_one_stock_sell_when_large_departure, name='test_one_stock'),
    path('test_one_stock_buy_when_large_departure', buy_when_large_departure.test_one_stock_buy_when_large_departure,
         name='test_one_stock_buy_when_large_departure'),
    path('merge_three_year_yield', three_k.merge_three_year_yield, name='merge_three_year_yield'),

    path('back_test', three_k.back_test,
         name='back_test')
]