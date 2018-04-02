from django.urls import path

from quanter.views import three_k

urlpatterns = [
    path('',  three_k.index, name='index'),
    path('test_all_stock', three_k.test_all_stock, name='test_all_stock'),
    path('test_one_stock', three_k.test_one_stock, name='test_all_stock'),
]