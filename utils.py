import QuantLib as ql


def build_bond(start_date: ql.Date, maturity_years: int, discount_handle: ql.RelinkableYieldTermStructureHandle):
    settlement_days = 2
    notional = 1000
    coupon_rate = [0.03]

    maturity_date = start_date + ql.Period(maturity_years, ql.Years)
    schedule = ql.Schedule(
        start_date, 
        maturity_date,
        ql.Period(ql.Semiannual), 
        ql.TARGET(),
        ql.ModifiedFollowing, 
        ql.ModifiedFollowing, 
        ql.DateGeneration.Backward, 
        False
    )
    bond = ql.FixedRateBond(
        settlement_days, 
        notional, 
        schedule, 
        coupon_rate, 
        ql.Thirty360(ql.Thirty360.BondBasis)
    )
    bond.setPricingEngine(ql.DiscountingBondEngine(discount_handle))
    return bond