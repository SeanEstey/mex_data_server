import logging
from .utils import abbrevnum
from math import floor, log10
log = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
def trade_stats(trades, prev_trd_id):
    """ Analyze recent trades, summarize + notify of Chad trades """
    n_bought=sum([x['size'] for x in trades if x['side']=='Buy'])
    n_sold=sum([x['size'] for x in trades if x['side']=='Sell'])
    largest=sorted(trades, key=lambda k: k['size'])[-1]

    if largest['trdMatchID'] != prev_trd_id:
        side='BUY' if n_bought > n_sold else 'SELL'
        perc=n_bought/(n_bought+n_sold) if side=='BUY' else n_sold/(n_bought+n_sold)
        log.info("{0} contracts Bought, {1} Sold ({2:0.2f}% {3} ratio)".format(
            abbrevnum(n_bought), abbrevnum(n_sold), perc*100, side))

        # Check for Chad trades
        chads=[x for x in trades if x['size'] > 1000000]
        for chad in chads:
            verb='bought' if chad['side']=='Buy' else 'sold'
            log.info("***CHAD TRADE: {0:,} contracts market {1}.***".format(chad['size'],verb))

        return largest['trdMatchID']

#-------------------------------------------------------------------------------
def instrum_stats(instruments):
    """ Print Open Interest, Funding Rate """
    log.info('{0}:${1:,} Funding:{2}% OI:${3}'.format(
        instruments[0]['underlying'],
        int(instruments[0]['lastPrice']),
        instruments[0]['fundingRate']*100,
        abbrevnum(sum([x['openInterest'] for x in instruments]))
    ))
