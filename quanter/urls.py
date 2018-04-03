from django.urls import path

from quanter.views import three_k

urlpatterns = [
    path('',  three_k.index, name='index'),
    path('test_all_stock', three_k.test_all_stock_sell_when_large_departure, name='test_all_stock'),
    path('test_all_stock_buy_when_large_departure', three_k.test_all_stock_buy_when_large_departure,
         name='test_all_stock_buy_when_large_departure'),
    path('test_one_stock', three_k.test_one_stock_sell_when_large_departure, name='test_one_stock'),
    path('test_one_stock_buy_when_large_departure', three_k.test_one_stock_buy_when_large_departure,
         name='test_one_stock_buy_when_large_departure'),
    path('merge_three_year_yield', three_k.merge_three_year_yield, name='merge_three_year_yield'),
]