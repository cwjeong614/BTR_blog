import backtrader as bt
from collections import OrderedDict
from DataFeed import *

class firstStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy(size=100)
        else:
            if self.rsi > 70:
                self.sell(size=100)


def printTradeAnalysis(analyzer):
    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = round(analyzer.pnl.net.total, 2)
    strike_rate = (total_won / total_closed) * 100

    h1 = ['Total open', 'Total Closed', 'Total Won', 'Total Lost']
    h2 = ['Strike Rate', 'Win Streak', 'Losing Streak', 'PnL Net']
    r1 = [total_open, total_closed, total_won, total_lost]
    r2 = [strike_rate, win_streak, lose_streak, pnl_net]

    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)

    print_list = [h1, r1, h2, r2]
    row_format = "{:<15}" * (header_length + 1)
    print('Trade Analysis Results:')
    for row in print_list:
        print(row_format.format('', *row))

def printSQN(analyzer):
    sqn = round(analyzer.sqn, 2)
    print('SQN: {}'.format(sqn))

cerebro = bt.Cerebro()
cerebro.addstrategy(firstStrategy)

start_date = '20170101'
end_date = '20171231'
cmp_code = 'A005380'

data_feed = DataFeed()
data = data_feed.get_cmp_ohlcv(cmp_code, start_date, end_date)
data = bt.feeds.PandasData(dataname=data)
cerebro.adddata(data)

startcash = 100000000
cerebro.broker.set_cash(startcash)

cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')
cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')

strategies = cerebro.run()
firstStrat = strategies[0]

printTradeAnalysis(firstStrat.analyzers.ta.get_analysis())
printSQN(firstStrat.analyzers.sqn.get_analysis())

portvalue = cerebro.broker.getvalue()

print('Final Portfolio Value: ${}'.format(portvalue))

cerebro.plot(style='candelstick')