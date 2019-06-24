import logging
import json
from time import sleep
from datetime import datetime

from app import *
from app.gsheets import SS
from app.analyze import *
from app.bitmex_websocket import BitMEXWebsocket
from app.timer import Timer
from app.utils import abbrevnum
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
            logger.critical("Doh! "+str(e))

    ss_tmr=Timer(name="ss_tmr", expire="every 60 clock minutes utc", quiet=True)
    prnt_tmr=Timer(name="prnt_tmr", expire="every 1 clock minutes utc", quiet=True)

    # Main loop
    prev_trd_id=""
    while(ws[0].ws.sock.connected):
        instruments=[]
        for _ws in ws:
            if _ws.exited:
                logger.critical("lost socket connection to "+_ws.symbol)
            else:
                instruments.append(_ws.get_instrument())

        prev_trd_id=trade_stats(ws[0].recent_trades(),prev_trd_id)

        # Print instrument data to console
        if prnt_tmr.remain()==0:
            prnt_tmr.reset()
            instrum_stats(instruments)

        # Append data to gsheet
        if ss_tmr.remain()==0:
            ss_tmr.reset()
            write_gsheet(instruments)
        sleep(10)

    logger.critical("lost socket connection. exiting...")

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
