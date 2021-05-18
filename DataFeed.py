import sqlite3
import pandas as pd

class DataFeed():
    def __init__(self):
        self.con = sqlite3.connect('E:/DB/cmp_ohlcv.db')
        self.cursor = self.con.cursor()

    def get_cmp_ohlcv(self, cmp_code, start_date, end_date):
        query = """
        SELECT Day, Open, High, Low, Close, Volume 
        FROM T_STK_DAILY_DATA 
        WHERE Code='{0}' 
        AND Day BETWEEN '{1}' AND '{2}' 
        ORDER BY Day ASC
        """

        data = pd.read_sql_query(query.format(cmp_code, start_date, end_date), self.con,
                                 index_col='Day', parse_dates=['Day'])
        # print('------------------------------------------------------')
        # print(cmp_code)
        # print(data)
        return data

    def grouping_by_mkt_cap(self, lower_mkt_cap, upper_mkt_cap, date, limit):
        query = """
        SELECT Code
        FROM T_CMP_MASTER
        WHERE Cmp_type=1
        --AND Volume NOT IN ('0')
        AND Mkt_cap BETWEEN '{0}' AND '{1}'
        AND Day='{2}'
        ORDER BY Mkt_cap DESC
        LIMIT '{3}'
        """

        unit = 100000000
        data = pd.read_sql_query(query.format(lower_mkt_cap * unit,
                                              upper_mkt_cap * unit,
                                              date, limit), self.con)

        return data


    def get_benchmark(self, start_date, end_date):
        query = """
        SELECT * FROM T_KOSPI_DATA
        WHERE Day BETWEEN '{0}' AND '{1}'
        ORDER BY Day ASC
        """

        data = pd.read_sql_query(query.format(start_date, end_date), self.con,
                                 index_col='Day', parse_dates=['Day'])

        return data

if __name__ == '__main__':
    cmp_code = 'A005930'
    start_date = '20200101'
    end_date = '20201231'

    data_feed = DataFeed()
    # data_feed.get_cmp_ohlcv(cmp_code=cmp_code, start_date=start_date, end_date=end_date)
    data = data_feed.get_benchmark(start_date, end_date)
    print(data)

    # lower_mkt_cap = 1000
    # upper_mkt_cap = 5000
    # day = '20210105'
    #
    # data = data_feed.grouping_by_mkt_cap(lower_mkt_cap, upper_mkt_cap, day, 200)
    # print(data['Code'])
