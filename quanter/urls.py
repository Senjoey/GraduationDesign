from django.urls import path

from quanter.views import three_k, buy_when_large_departure

urlpatterns = [
    path('',  three_k.test_three_k, name='index'),
    path('stock_charts',  three_k.stock_charts, name='stock_charts'),
    path('strategy_introduction',  three_k.strategy_introduction, name='strategy_introduction'),

    path('stock_table',  three_k.stock_table, name='stock_table'),
    path('<str:code>/', three_k.check_stock, name='check_stock'),

    path('stock_mine',  three_k.stock_mine, name='stock_mine'),
    path('<str:code>/', three_k.delete_my_stock, name='delete_my_stock'),

    path('test_all_stock', three_k.test_all_stock_sell_when_large_departure, name='test_all_stock'),
    path('test_all_stock_buy_when_large_departure', buy_when_large_departure.test_all_stock_buy_when_large_departure,
         name='test_all_stock_buy_when_large_departure'),
    path('test_one_stock', three_k.test_one_stock_sell_when_large_departure, name='test_one_stock'),
    path('test_one_stock_buy_when_large_departure', buy_when_large_departure.test_one_stock_buy_when_large_departure,
         name='test_one_stock_buy_when_large_departure'),
    path('merge_three_year_yield', three_k.merge_three_year_yield, name='merge_three_year_yield'),
]