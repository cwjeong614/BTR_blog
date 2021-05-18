import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds

# Data Feeds
# >> 기본 작업은 Strategies에서 진행. Data Feeds도 자동으로 패스

class MyStrategy(bt.Strategy):
    lines = ('sma')
    params = dict(period=20)

    def __init__(self):
        sma = btind.SMA(self.datas[0], period=self.params.period)

    def prenext(self):
        print('prenext:: current period:', len(self))

    def nextstart(self):
        print('nextstart:: current period:', len(self))

    def next(self):
        print('next:: current period:', len(self))