'''변동성 돌파 전략 (Volatility Break-Out Strategy)'''
import argparse

import pandas as pd
import backtrader as bt
from DataFeed import *
from datetime import datetime
import statistics as stats

class VBO(bt.Strategy):
    params = ()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        pass

    def notify_order(self, order):
        pass

    def notify_trade(self, trade):
        pass

    def next(self):
        pass

def parse_args(pargs=None):

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='변동성 돌파 전략'
    )

    parser.add_argument()

def runstrat():
    pass

if __name__ == '__main__':
    runstrat()


