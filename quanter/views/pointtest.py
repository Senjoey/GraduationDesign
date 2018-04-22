from django.http import HttpResponse
from quanter.three_k_strategy import ThreeKStrategy
from quanter.data_prepare import DataPrepare


def test_two_point(request):
    data_prepare = DataPrepare()
    # data_prepare.ma_data_prepare('2014-01-01', '2018-04-20')
    data_prepare.test()
    return HttpResponse("获取数据成功！")


def test_one_point(request):
    three_k = ThreeKStrategy("2014-01-01", "2014-12-31")
    three_k.get_date_series()
    return HttpResponse("获取数据成功！")

