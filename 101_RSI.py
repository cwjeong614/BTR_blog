import pandas as pd
import backtrader as bt
from DataFeed import *
from datetime import datetime
import statistics as stats

class RSI_Strategy(bt.Strategy):
    params = (
        ('valid', 10),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    # 개별 종목
    # def __init__(self):
    #     self.dataclose = self.datas[0].close
    #
    #     # 변수 선언
    #     self.order = None
    #     self.buyprice = None
    #     self.buycomm = None
    #
    #     self.tradepnl_sum = 0.0
    #
    #     # 지표 추가
    #     self.rsi = bt.indicators.RSI_SMA(self.datas[0])

    def __init__(self):
        self.inds = dict()

        # print(type(self.datas))
        # print(self.datas[:-1])
        for i, d in enumerate(self.datas[:-1]):
            self.inds[d] = dict()
            self.inds[d]['close'] = d.close
            self.inds[d]['high'] = d.high
            self.inds[d]['low'] = d.low

            self.inds[d]['rsi'] = bt.indicators.RSI_Safe(d.close, period=14)
            # self.indx[d]['bbands'] = bt.indicators.BollingerBands(d.close, period=20)

            self.inds[d]['bar_executed'] = 0
            # self.cmp_list = dict()

        self.o = dict()     # orders per data
        self.holding = []   # holding periods per data
        self.tradepnl_sum = 0

    def notify_order(self, order):
        dt, dn = self.datetime.date(), order.data._name

        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            order.executed.price = int(order.executed.price)
            order.executed.value = int(order.executed.value)
            order.executed.comm = int(order.executed.comm)
            if order.isbuy():
                if dn in self.o:
                    pass
                else:
                    self.o[dn] = {}

                self.log('종목: %s | 매수 체결: %s | 매입원가: %s | 수수료: %s' %
                         (order.data._name,
                          format(order.executed.price, ',d'),
                          format(order.executed.value, ',d'),
                          format(order.executed.comm, ',d')))

                self.o[dn]['buy_price'] = order.executed.price
            elif order.issell():
                self.log('종목: %s | 매도 체결: %s | 매입원가: %s | 수수료: %s' %
                         (order.data._name,
                          format(order.executed.price, ',d'),
                          format(order.executed.value, ',d'),
                          format(order.executed.comm, ',d')))

            # self.bar_executed = len(self)


            self.o[dn]['bar_executed'] = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('%s 주문 취소/마진/거절' % dn)


    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        # 거래 손익 로그
        self.log('총손익: %.2f | 순손익: %.2f' %
                 (trade.pnl, trade.pnlcomm))
        self.tradepnl_sum += trade.pnlcomm
        self.log('누적실현손익: %.2f' % self.tradepnl_sum)

    def next(self):
        # self.log('날짜')
        for i, d in enumerate(self.datas[:-1]):
            # self.log(self.inds[d]['rsi'][0])
            # self.log(self.inds[d]['close'][0])
            dt, dn = self.datetime.date(), d._name
            pos = self.getposition(d).size
            # self.log('{} 종가: {}'.format(dn, self.inds[d]['close'][0]))

            # RSI < 20 이하이면 매수
            if not pos:
                if self.inds[d]['rsi'] < 15:
                    self.o[d] = self.order_target_percent(data=d, target=0.01)

            elif pos:
                if self.inds[d]['rsi'] > 70:
                    self.o[d] = self.close(data=d)
                    self.holding.append(len(self) - self.o[dn]['bar_executed'])
                    self.log(stats.mean(self.holding))
                    self.log('%s 매도전략 1: RSI Upper 돌파' % dn)

                # elif len(self) > self.o[dn]['bar_executed'] + self.p.valid:
                #     self.o[d] = self.close(data=d)
                #     self.log('%s 매도전략 2: 보유기간 초과' % dn)

                # elif len(self) > self.o[dn]['bar_executed'] and self.inds[d]['high'][0] > self.o[dn]['buy_price'] * 1.3:
                #     self.log('%s | 고가: %s | 목표가: %s' % (dn, self.inds[d]['high'][0], self.o[dn]['buy_price'] * 1.3))
                #     self.o[d] = self.close(data=d, price=self.inds[d]['high'][0])
                #     self.log('%s 매도전략 3: 수익률 30%% 초과' % dn)



def printDrawDown(analyzer):
    drawdown = round(analyzer.drawdown, 2)
    moneydown = round(analyzer.moneydown, 2)
    duration = analyzer.len
    maxdrawdown = round(analyzer.max.drawdown, 2)
    maxmoneydown = round(analyzer.max.moneydown, 2)
    maxduration = analyzer.max.len
    print('Drawdown %    : {}, Drawdown     : {}, Duration    : {}'.format(drawdown, moneydown, duration))
    print('Max Drawdown %: {}, Max Drawdown : {}, Max Duration: {}'.format(maxdrawdown, maxmoneydown, maxduration))


def printTraderAnalysis(analyzer):
    '''
    Function to print the Technical Analysis results in a nice format.
    '''
    # Get the results we are interested in
    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = format(int(round(analyzer.pnl.net.total, 2)), ',d')

    strike_rate = round(((total_won / total_closed) * 100), 2)
    # Designate the rows
    h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
    h2 = ['Strike Rate', 'Win Streak', 'Losing Streak', 'PnL Net']
    r1 = [total_open, total_closed, total_won, total_lost]
    r2 = [strike_rate, win_streak, lose_streak, pnl_net]
    # Check which set of headers is the longest.
    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)
    # Print the rows
    print_list = [h1, r1, h2, r2]
    row_format = "{:<15}" * (header_length + 1)
    print("Trade Analysis Results:")
    for row in print_list:
        print(row_format.format('', *row))

def printSarpeRatio(analyzer):
    pass

def printSQN(analyzer):
    sqn = round(analyzer.sqn, 2)
    if sqn > 7.0:
        text = '전략 점수 Too high >> 오류 없나 확인 필요'
    elif sqn > 5.1:
        text = '전략 점수 Super Good..!!'
    elif sqn > 3.0:
        text = '전략 점수 Excellent!!'
    elif sqn > 2.5:
        text = '전략 점수 Good!'
    elif sqn > 2.0:
        text = '전략 점수 Average'
    elif sqn > 1.6:
        text = '전략 점수 Below Avg'
    else:
        text = '전략 점수 너무 낮음 >> 쓰레기..'
    print('SQN: {} >> '.format(sqn) + text)

if __name__ == '__main__':
    cerebro = bt.Cerebro(stdstats=False)        # stdstats=False >> Plotting X
    data_feed = DataFeed()

    # 전략 추가
    cerebro.addstrategy(RSI_Strategy)

    # 데이터 로드 ========================================================================================
    # 변수 입력
    start_date = '20150102'      # 휴일부터 시작하면 안됨
    end_date = '20201231'
    cmp_code = 'A005930'
    gijun_date = '20201230'
    lower_cap = 1000
    upper_cap = 5000000
    universe_cmp = 10

    ## 1. 개별 종목
    # data = data_feed.get_cmp_ohlcv(cmp_code, start_date, end_date)
    # data = bt.feeds.PandasData(dataname=data)
    # cerebro.adddata(data)

    ## 2. 복수 종목
    data = data_feed.grouping_by_mkt_cap(lower_cap, upper_cap, gijun_date, universe_cmp)
    cmp_list = data['Code']

    for i, code in enumerate(cmp_list):
        if i == 0:
            data = data_feed.get_cmp_ohlcv(code, start_date, end_date)
            data = bt.feeds.PandasData(dataname=data, name=code, plot=False)
            cerebro.adddata(data)
        else:
            data_n = data_feed.get_cmp_ohlcv(code, start_date, end_date)

            if len(data_n) == 0:
                print('데이터 없음 ', code)
                pass
            elif data_n['Volume'][0] == 0:      # 거래량 0인 종목 제외 (거래정지 종목)
                print('거래량 0인 종목 ', code)
                pass
            elif data_n.index[0].strftime('%m/%d/%Y') > datetime.strptime(start_date,'%Y%m%d').strftime('%m/%d/%Y'):    # 상장일이 기준일보다 늦는 종목 제외
                print('상장일이 기준일보다 늦는 경우 ', code)
                print(data_n.index[0].strftime('%m/%d/%Y'))
                print(datetime.strptime(start_date,'%Y%m%d').strftime('%m/%d/%Y'))
                pass
            else:
                data_n = bt.feeds.PandasData(dataname=data_n, name=code, plot=False)
                data_n.plotinfo.plotmaster = data
                cerebro.adddata(data_n)

    ## 3. Benchmark 데이터
    bm_data = data_feed.get_benchmark(start_date, end_date)
    bm_data = bt.feeds.PandasData(dataname=bm_data, name='Benchmark')
    cerebro.adddata(bm_data, name='BM_Kospi')
    # ===================================================================================================


    # 초기 세팅 ===========================================================================================
    cerebro.broker.set_cash(100000000)
    cerebro.broker.setcommission(0.003)
    # cerebro.addsizer(bt.sizers.PercentSizerInt, percents=10)

    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    cerebro.addobserver(bt.observers.Broker)        # 포트폴리오만 Plotting
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.Benchmark, data=bm_data)
    # cerebro.addobserver(bt.observers.TimeReturn)

    # 결과 csv 파일로 출력
    # cerebro.addwriter(bt.WriterFile, csv=True, out='MultiRSI_2.csv')
    # ====================================================================================================

    start_pf_value = format(cerebro.broker.getvalue(), ',d')


    # 백테스트 실행
    strat = cerebro.run()
    firstStrat = strat[0]

    printTraderAnalysis(firstStrat.analyzers.ta.get_analysis())
    printSQN(firstStrat.analyzers.sqn.get_analysis())
    printDrawDown(firstStrat.analyzers.drawdown.get_analysis())

    end_pf_value = format(int(cerebro.broker.getvalue()), ',d')

    print('기초 포트폴리오: %s' % start_pf_value)
    print('기말 포트폴리오: %s' % end_pf_value)

    cerebro.plot()