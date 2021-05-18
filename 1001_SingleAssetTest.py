import backtrader as bt
from DataFeed import *
from datetime import datetime
import statistics as stats

class RSI_SingleAsset(bt.Strategy):
    params = (
        ('rsiperiod', 14),
        ('target_weight', 0.8),
        ('target_ret_per', 5),
        ('loss_cut_per', 3),
        ('exitbars', 5),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.rsi = bt.indicators.RSI_Safe(self.datas[0],
                                          period = self.p.rsiperiod)

        self.rsi.csv = True

        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.tradepnl_sum = 0.0

        self.condition_1 = 0
        self.condition_2 = 0
        self.condition_3 = 0
        self.condition_4 = 0

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('매수 체결: %.2f | 매입원가: %.2f | 수수료: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                self.bar_executed = len(self)
                self.buyprice = order.executed.price

            elif order.issell():
                self.log('매도 체결: %.2f | 매입원가: %.2f | 수수료: %.2f | 주문수량: %s' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm,
                          order.executed.size))

        if order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('주문 취소/마진/거절')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('실현손익: %.2f | 순손익: %.2f' % (trade.pnl, trade.pnlcomm))
        self.tradepnl_sum += trade.pnlcomm
        self.log('누적순손익: %.2f' % self.tradepnl_sum)

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.rsi < 30:
                self.order = self.order_target_percent(target=self.p.target_weight)

        else:
            target_price = self.buyprice * (1.0 + self.p.target_ret_per / 100.0)
            losscut_price = self.buyprice * (1.0 - self.p.loss_cut_per / 100.0)
            # self.sell(exectype=bt.Order.Limit)

            if len(self) > self.bar_executed + self.p.exitbars:
                self.log('매도조건2: 5일 경과')
                self.order = self.close()
                self.condition_2 +=  1

                print(self.condition_2)

            elif self.datahigh[0] > target_price:
                self.log('매도조건3: %s%% 이상 상승 | 고가: %s | 5%% 가격: %s' %
                         (self.p.target_ret_per, self.datahigh[0], target_price))
                self.order = self.close(exectype=bt.Order.Limit, price=target_price)
                self.condition_3 += 1

                print(self.condition_3)

            elif self.datalow[0] < losscut_price:
                self.log('매도조건4: 손절')
                self.order = self.close()
                self.condition_4 += 1

                print(self.condition_4)

            elif self.rsi > 70:
                self.log('매도조건1: RSI > 70')
                self.order = self.close()
                self.condition_1 += 1

                print(self.condition_1)

if __name__ == '__main__':
    data_feed = DataFeed()

    cerebro = bt.Cerebro()

    cerebro.addstrategy(RSI_SingleAsset)

    start_date = '20100104'
    end_date = '20201231'
    cmp_code = 'A005930'

    data = data_feed.get_cmp_ohlcv(cmp_code, start_date, end_date)
    data = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data)

    # cerebro.addwriter(bt.WriterFile, csv=True, out='test3.csv')

    cerebro.broker.set_cash(1000000)
    cerebro.broker.setcommission(0.003)

    start_pf_value = format(cerebro.broker.getvalue(), ',d')
    cerebro.run()
    end_pf_value = format(int(cerebro.broker.getvalue()), ',d')

    print('기초 포트폴리오: %s' % start_pf_value)
    print('기말 포트폴리오: %s' % end_pf_value)

    cerebro.plot()

