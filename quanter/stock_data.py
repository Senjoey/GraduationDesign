from quanter.models import Dailydata, Ma, Stock
import pandas as pd


class StockDataService(object):

    def get_stock_data(self, code, start_date, end_date):
        data_query_set = Dailydata.objects.filter(date__range=(start_date, end_date), code__in=[code])
        df = pd.DataFrame(list(data_query_set.values('date', 'close')))
        if len(df) == 0:
            return df
        df.set_index('date', inplace=True)
        df.sort_index()
        return df

    def get_ma_related_data(self):
        data_query_set = Ma.objects.all()
        df = pd.DataFrame(list(data_query_set.values('date', 'ma20', 'ma5', 'ma20_departure_value', 'close')))
        df.set_index('date', inplace=True)
        df.sort_index()
        return df

    def get_all_stock(self):
        # return Mystock.objects.all()
        return Stock.objects.all()

    def get_stock_by_code(self, code):
        return Stock.objects.filter(code=code)
