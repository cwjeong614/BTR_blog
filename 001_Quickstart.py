import datetime
import sqlite3
import pandas as pd

import backtrader as bt

# 전략 클래스 생성
class TestStrategy(bt.Strategy):
    params = (
        ('exitbars', 10),
        ('maperiod', 15),
    )

    # 로그 찍는 함수
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    # 초기 실행 함수
    def __init__(self):
        self.dataclose = self.datas[0].close

        # 변수 선언
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.tradepnl_sum = 0.0

        # 지표 추가
        self.sma = bt.indicators.MovingAverageSimple(self.datas[0],
                                                     period = self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        # if order.status in [order.Completed]:
        #     if order.isbuy():
        #         self.log('매수 체결: %.2f | 매입원가: %.2f | 수수료: %.2f' %
        #                  (order.executed.price,
        #                   order.executed.value,
        #                   order.executed.comm))
        #     elif order.issell():
        #         self.log('매도 체결: %.2f | 매입원가: %.2f | 수수료: %.2f' %
        #                  (order.executed.price,
        #                   order.executed.value,
        #                   order.executed.comm))

            self.bar_executed = len(self)
            # self.log('len(self) %s' % len(self))

        # elif order.status in [order.Canceled, order.Margin, order.Rejected]:
        #     self.log('주문 취소/마진/거절')

        # 주문 함수 = None 으로 덮어쓰기
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        # 거래  손익 로그
        # self.log('실현손익: %.2f | 실현손익(수수료포함): %.2f' % (trade.pnl, trade.pnlcomm))
        # self.tradepnl_sum += trade.pnlcomm
        # self.log('누적실현손익(수수료포함): %.2f' % self.tradepnl_sum)

    def next(self):
        # 종가 로그 찍기
        # self.log('종가: %.0f' % self.dataclose[0])
        # self.log('self.dataclose[-1] : %.0f' % self.dataclose[-1])

        # 주문 나가있는 게 있으면, 두번째 주문 내면 안되니깐 추가
        if self.order:
            return

        # 현재 포지션이 없을 때만 매수
        if not self.position:

            # # 3일 연속 하락 조건 추가
            # if self.dataclose[0] < self.dataclose[-1]:
            #     if self.dataclose[-1] < self.dataclose[-2]:
            #         self.log('매수 시그널: %.2f' % self.dataclose[0])
            #
            #         # 주문 변수에 매수 주문
            #         self.order = self.buy()

            # # 이평선 전략
            if self.dataclose[0] > self.sma[0]:
                # self.log('매수 시그널: %.2f' % self.dataclose[0])

                self.order = self.buy()

        # 포지션 있으면 매도
        else:
            # # 매수일로부터 5일 뒤 매도
            # if len(self) >= (self.bar_executed + self.params.exitbars):
            #     self.log('매도 시그널: %.2f' % self.dataclose[0])
            #
            #     # 주문 변수에 매도 주문
            #     self.order = self.sell()

            # 이평선 전략
            if self.dataclose[0] < self.sma[0]:
                # self.log('매도 시그널: %.2f' % self.dataclose[0])

                self.order = self.sell()

    def stop(self):
        self.log('(%2d 이평선) 기말 포트폴리오 %.2f' %
                 (self.params.maperiod, self.broker.getvalue()))


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # 전략 추가
    cerebro.addstrategy(TestStrategy)

    # 전략 최적화
    # cerebro.optstrategy(
    #     TestStrategy,
    #     maperiod=range(10,31)
    # )

    # Data Feed ===================================================================================================
    con = sqlite3.connect('E:/DB/cmp_ohlcv.db')
    query = "SELECT Day, Open, High, Low, Close, Volume FROM T_STK_DAILY_DATA WHERE Code='A005930' ORDER BY DAY ASC"
    data = pd.read_sql(query, con, index_col='Day', parse_dates=['Day'])

    # print(data.head(100))

    data = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data)
    # =============================================================================================================

    # 초기 현금 세팅
    cerebro.broker.setcash(1000000.0)

    # 주식수량 세팅
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # 수수료 세팅
    cerebro.broker.setcommission(commission=0.0015)

    print('기초 포트폴리오: %.2f' % cerebro.broker.getvalue())

    cerebro.run(maxcpus=1)

    print('기말 포트폴리오: %.2f' % cerebro.broker.getvalue())


    cerebro.plot()