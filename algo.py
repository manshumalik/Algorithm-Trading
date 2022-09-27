from zipline.api import order, symbol, order_target_percent
from library.technicals.indicators import bollinger_band, sma, macd



def initialize(context):
    # universe selection
    context.securities = [symbol("COST"), symbol("BRK.B"), symbol("DHR"), symbol("WFC"), symbol("UNP"), symbol("TMO"), symbol("CSCO"), symbol("AVGO"), symbol("PFE"), symbol("KO"), symbol("MRK"), symbol("ABBV"), symbol("PEP"), symbol("CVX"), symbol("NKE"), symbol("ACN"), symbol("LLY"), symbol("TXN"), symbol("QCOM"), symbol("MDT"), symbol("PG"), symbol("UNH"), symbol("HD"), symbol("MA"), symbol("BAC"), symbol("INTC"), symbol("NFLX"), symbol("CMCSA"), symbol("VZ"), symbol("ADBE"), symbol("CRM"), symbol("ABT"), symbol("XOM"), symbol("T"), symbol("WMT"), symbol("AAPL"), symbol("MSFT"), symbol("AMZN"), symbol("FB"), symbol("GOOGL"), symbol("GOOG"), symbol("JPM"), symbol("JNJ"), symbol("NVDA"), symbol("V"), symbol("PYPL"), symbol("DIS")]

    context.params = {'indicator_lookback':400,
                      'indicator_freq':'1m',
                      'buy_signal_threshold':5,
                      'sell_signal_threshold':-0.05,
                      'SMA_period_short':10,
                      'SMA_period_long':35,
                      'BBands_period':300,
                      'trade_freq':600,
                      'leverage':1}

    context.bar_count = 0

    context.signals = dict((security,0) for security in context.securities)
    context.target_position = dict((security,0) for security in context.securities)

def run_strategy(context, data):
    generate_signals(context, data)
    generate_target_position(context, data)
    rebalance(context, data)

def handle_data(context, data):
    context.bar_count = context.bar_count + 1
    if context.bar_count < context.params['trade_freq']:
        return

    context.bar_count = 0
    run_strategy(context, data)


def rebalance(context,data):
    for security in context.securities:
        order_target_percent(security, context.target_position[security])

def generate_target_position(context, data):
    num_secs = len(context.securities)
    weight = round(1.0/num_secs,2)*context.params['leverage']

    for security in context.securities:
        if context.signals[security] > context.params['buy_signal_threshold']:
            context.target_position[security] = weight
        elif context.signals[security] < context.params['sell_signal_threshold']:
            context.target_position[security] = -weight
        else:
            context.target_position[security] = 0

def generate_signals(context, data):
    price_data = data.history(context.securities, 'close', 
        context.params['indicator_lookback'], context.params['indicator_freq'])

    for security in context.securities:
        px = price_data.loc[:,security].values
        context.signals[security] = signal_function(px, context.params)

def signal_function(px, params):
    upper, mid, lower = bollinger_band(px,params['BBands_period'])
    ind2 = sma(px, params['SMA_period_long'])
    ind3 = sma(px, params['SMA_period_short'])
    last_px = px[-1]
    dist_to_upper = 100*(upper - last_px)/(upper - lower)

    if dist_to_upper > 95:
        return -1
    elif dist_to_upper < 5:
        return 1
    elif dist_to_upper > 40 and dist_to_upper < 60 and ind2-ind3 < 0:
        return -1
    elif dist_to_upper > 40 and dist_to_upper < 60 and ind2-ind3 > 0:
        return 1
    else:
        return 0
