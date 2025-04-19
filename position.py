from typing import List, Dict
import random

import QuantLib as ql

from bus import EventBus, DV01Events


class FixedRateBondPosition:
    def __init__(self, instrument: ql.FixedRateBond, notional: float, yts: ql.RelinkableYieldTermStructureHandle, label: str = ""):
        self.instrument = instrument
        self.notional = notional
        self.discount_handle = yts
        self.original_curve = self.discount_handle.currentLink()
        self.label = label or str(id(instrument))

    def npv(self) -> float:
        return self.instrument.NPV() * self.notional

    def dv01(self, nodes: List[int]) -> dict:
        base_npv = self.npv()
        spreads = [ql.SimpleQuote(0.0) for _ in nodes]
        new_curve = self._get_spread_curve(nodes, spreads)
        self.discount_handle.linkTo(new_curve)
        dv01s = {}
        for i in range(len(nodes)):
            spreads[i].setValue(1e-4)
            bumped_npv = self.npv()
            dv01s[i + 1] = base_npv - bumped_npv
            spreads[i].setValue(0)
        self.discount_handle.linkTo(self.original_curve)
        return dv01s
    
    def _get_spread_curve(self, nodes: List[int], spreads: List[ql.SimpleQuote]) -> ql.SpreadedLinearZeroInterpolatedTermStructure:
        dates = [ql.Date.todaysDate() + ql.Period(b, ql.Years) for b in nodes]
        new_curve = ql.SpreadedLinearZeroInterpolatedTermStructure(
            ql.YieldTermStructureHandle(self.original_curve),
            [ql.QuoteHandle(s) for s in spreads],
            dates
        )
        new_curve.enableExtrapolation()
        return new_curve


class FixedRateBondPortfolio:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.positions: List[FixedRateBondPosition] = []

    def add_position(self, position: FixedRateBondPosition):
        self.positions.append(position)
    
    def remove_random_position(self):
        if self.positions:
            self.positions.pop(random.randint(0, len(self.positions) - 1))

    def npv(self) -> float:
        return sum(pos.npv() for pos in self.positions)

    def calculate_portfolio_dv01(self, nodes=range(1, 11)) -> Dict[int, float]:
        agg_dv01 = {n: 0.0 for n in nodes}
        for pos in self.positions:
            pos_dv01 = pos.dv01(nodes)
            for n in nodes:
                agg_dv01[n] += pos_dv01.get(n, 0.0)
        self.event_bus.publish(DV01Events.DV01_UPDATED, agg_dv01)
