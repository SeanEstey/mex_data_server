import logging
import json
from time import sleep
from datetime import datetime

from app import *
from app.gsheets import SS
from app.bitmex_websocket import BitMEXWebsocket
from app.timer import Timer
from conf.mexapikey import api_key,api_secret
from conf.gservkeys import gservacct
from conf.conf import *

#-------------------------------------------------------------------------------
# TODO: find way to discover list of XBT fut symbols instead of hardcoding
# TODO: find way to subcribe to multiple instruments using same websocket
def run():
    logger = setup_logger()
    ws=[]

    for symbol in symbols:
        try:
            ws.append(BitMEXWebsocket(
                endpoint="wss://www.bitmex.com/realtime",
                symbol=symbol,
                api_key=api_key,
                api_secret=api_secret
            ))
        except Exception as e:
            logger.critical(str(e))

    ss_tmr=Timer(name="ss_tmr", expire="every 60 clock minutes utc", quiet=True)
    prnt_tmr=Timer(name="prnt_tmr", expire="every 1 clock minutes utc", quiet=True)

    # Main loop
    while(ws[0].ws.sock.connected):
        instruments=[]
        for _ws in ws:
            if _ws.exited:
                logger.critical("lost socket connection to "+_ws.symbol)
            else:
                instruments.append(_ws.get_instrument())

        print_chad(ws[0].recent_trades())

        # Print instrument data to console
        if prnt_tmr.remain()==0:
            prnt_tmr.reset()
            logger.info('Symbol:{0} Price:${1:,} Funding:{2}% OpenInterest:${3:,}'.format(
                instruments[0]['underlying'],
                int(instruments[0]['lastPrice']),
                instruments[0]['fundingRate']*100,
                sum([x['openInterest'] for x in instruments])
            ))

        # Append data to gsheet
        if ss_tmr.remain()==0:
            ss_tmr.reset()
            write_gsheet(instruments)
        sleep(10)

    logger.critical("lost socket connection. exiting...")

#-------------------------------------------------------------------------------
def print_chad(trades):
    chads=[x for x in trades if x['size'] > 1000000]
    for chad in chads:
        verb='bought' if chad['side']=='Buy' else 'sold'
        print("Chad Trade: {0:,} contracts market {1}.".format(chad['size'],verb))
    if len(chads)==0:
        biggest=sorted(trades, key=lambda k: k['size'])[-1]
        print("{0:,} non-chad trades, {1:,} contracts largest {2}.".format(len(trades),biggest['size'],biggest['side']))

#-------------------------------------------------------------------------------
def write_gsheet(instruments):
    ss = SS(gservacct['oauth'], ss_id)
    wks = ss.wks(wks_name)
    row=[
        str(datetime.utcnow()),                                                 # Date
        instruments[0]["underlying"],                                           # Asset
        instruments[0]['reference'],                                            # Exchange
        instruments[0]['lastPrice'],                                            # PerpSwap Price
        sum([x['fundingRate'] for x in instruments if x['fundingRate']]),       # PerpSwap Funding Rate
        sum([x['openInterest'] for x in instruments if x['fundingRate']]),      # PerpSwap OI
        sum([x['openInterest'] for x in instruments if not x['fundingRate']]),  # Futures OI sum
        int(sum([x['openInterest'] for x in instruments])/100000)               # Total OI
    ]
    wks.appendRows([row])


if __name__ == "__main__":
    run()
