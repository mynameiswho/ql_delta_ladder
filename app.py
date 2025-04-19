import time
import random
import threading
import tkinter as tk
import QuantLib as ql

from display import DV01Ladder
from bus import EventBus
from position import FixedRateBondPortfolio, FixedRateBondPosition
from utils import build_bond


def simulate_trading(portfolio: FixedRateBondPortfolio, yts: ql.RelinkableYieldTermStructureHandle):
    while True:
        time.sleep(3)
        action = random.choice(['add_bond', 'remove'])
        if action == 'add_bond':
            mat = random.randint(1, 20)
            bond = build_bond(today, mat, yts)
            notional = random.randint(1000, 10000)
            position = FixedRateBondPosition(bond, notional, yts)
            portfolio.add_position(position)
            portfolio.calculate_portfolio_dv01(list(range(1, 21)))
            print(f'Notional position {notional} in bond with maturity {mat} was added')
        elif action == 'remove':
            print('Random position was removed')
            portfolio.remove_random_position()
            portfolio.calculate_portfolio_dv01(list(range(1,21)))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Delta risk display")
    root.geometry("300x500")

    event_bus = EventBus()

    today = ql.Date.todaysDate()
    day_count = ql.Actual360()
    curve = ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(0.02)), day_count)
    curve.enableExtrapolation()

    yts = ql.RelinkableYieldTermStructureHandle(curve)
    portfolio = FixedRateBondPortfolio(event_bus)
    
    dv01_frame = DV01Ladder(root, event_bus, buckets=list(range(1, 21)))
    dv01_frame.pack(padx=10, pady=10)

    threading.Thread(target=simulate_trading, args=(portfolio, yts, ), daemon=True).start()

    root.mainloop()
