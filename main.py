from app.bitmex_websocket import BitMEXWebsocket
import logging
from time import sleep
from util.apikeys import api_key,api_secret


# Basic use of websocket.
def run():
    logger = setup_logger()
    ws = BitMEXWebsocket(
        endpoint="wss://www.bitmex.com/realtime",
        symbol="XBTUSD",
        api_key=api_key,
        api_secret=api_secret
    )

    # Run forever
    while(ws.ws.sock.connected):
        #ticker=ws.get_ticker()
        instrument=ws.get_instrument()

        logger.info("Open Interest: "+str(instrument['openInterest']))

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


if __name__ == "__main__":
    run()
