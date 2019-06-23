from app.bitmex_websocket import BitMEXWebsocket
import logging
from time import sleep
from conf.mexapikey import api_key,api_secret
from conf.gservkeys import gservacct
from conf.conf import *
from app.timer import Timer

symbols=['XBTUSD','XBTM19','XBTU19','XBTZ19']

def run():
    logger = setup_logger()

    ws=[]
    for symbol in symbols:
        ws.append(BitMEXWebsocket(
            endpoint="wss://www.bitmex.com/realtime",
            symbol=symbol, #"XBTUSD",
            api_key=api_key,
            api_secret=api_secret
        ))

    t=Timer(name="SS_Timer",expire="every 5 clock minutes utc")

    # Run forever
    while(ws[0].ws.sock.connected):
        # Update Gsheet at fixed timer intervals
        if t.remain()==0:
            t.reset()
            instruments=[]
            for _ws in ws:
                instruments.append(_ws.get_instrument())
            append_oi(instruments)
        sleep(10)

def setup_logger():
    # Prints logger info to terminal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def append_oi(instruments):
    from datetime import datetime
    from app.gsheets import SS

    total_oi=0
    for instrument in instruments:
        total_oi+=instrument['openInterest']

    ss = SS(gservacct['oauth'], ss_id)
    wks = ss.wks(wks_name)
    row=[
        str(datetime.now()),            # Date
        "XBT",                          # Asset
        "Bitmex",                       # Exchange
        instruments[0]['lastPrice'],    # Price
        "",                             # Perp Swap OI
        "",                             # Futures OI
        int(total_oi/100000)            # Total OI
    ]
    print("Appending Open Interest: "+str(total_oi))
    wks.appendRows([row])


if __name__ == "__main__":
    run()
