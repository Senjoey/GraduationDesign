from quanter.models import Dailydata, Stock
import pandas as pd


class StockDataService(object):

    def get_stock_data(self, code, start_date, end_date):
        data_query_set = Dailydata.objects.filter(date__range=(start_date, end_date), code__in=[code])
        df = pd.DataFrame(list(data_query_set.values('id', 'date', 'close')))
        if len(df) == 0:
            return df
        df.set_index('date', inplace=True)
        df.sort_index()
        return df

    def get_stock_data_by_code(self, code, star_date, end_date):
        data_query_set = Dailydata.objects.filter(date__range=(star_date, end_date), code__in=[code])
        df = pd.DataFrame(list(data_query_set.values('date', 'close', 'open')))
        if len(df) == 0:
            return df
        df.set_index('date', inplace=True)
        df.sort_index()
        return df


    def get_all_stock(self):
        # return Mystock.objects.all()
        return Stock.objects.all()

    def get_stock_by_code(self, code):
        return Stock.objects.filter(code=code)



