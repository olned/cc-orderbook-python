import asyncio
import logging
import sys

from ssc2ce import Bitfinex

from instruments import SYMBOLS
from orderbook import L2OrderBook

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.WARNING)
logger = logging.getLogger("ons-derobit-ws-python-sample")

conn = Bitfinex()

books = []
instruments = []
if len(sys.argv) > 1:
    if sys.argv[1].isdigit():
        instruments += ['t' + t.upper() for t in SYMBOLS[:int(sys.argv[1])]]
    else:
        instruments += sys.argv[1:]
else:
    instruments.append("tBTCUSD")


class Counter:
    count = 0
    local_latency = 0.0
    ws_latency = 0.0

    def add(self, server_time, start_at, end_at):
        self.count += 1
        self.local_latency += (end_at - start_at)
        self.ws_latency += (start_at - server_time)

    def report(self):
        if self.count:
            print(
                f"avg local latency:{self.local_latency / self.count}\n"
                f"avg websocket latency:{self.ws_latency / self.count}\n"
                f"total count {self.count}")


counter = Counter()


async def subscribe():
    for instrument in instruments:
        order_book = L2OrderBook(instrument)
        books.append(order_book)
        await order_book.subscribe_book(conn, counter.add)


conn.on_connect_ws = subscribe

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
except Exception as e:
    print(e)
    print(conn.last_message)

print("Number of instruments:", len(instruments))
counter.report()
