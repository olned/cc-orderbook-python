import argparse
import asyncio
import json
import logging
from time import time

from ssc2ce import Bitfinex

from counter import Counter
from instruments import SYMBOLS
from orderbook import L2OrderBook

parser = argparse.ArgumentParser('Bitfinex Order Book Example.')
parser.add_argument('-s', '--stop', dest='stop_in', type=int, default=0,
                    help='Stop the script after a specified time in seconds. Default 0 - do not stop')
parser.add_argument('-l', '--log_level', type=str, default='WARNING')
parser.add_argument('-n', '--num_instruments', type=int, default=None,
                    help='Get first N instruments from the instruments.py file. Default None - do not use')
parser.add_argument('-i', '--instrument', nargs='*', dest='instrument', default=['tBTCUSD'])
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=args.log_level)
logger = logging.getLogger("ons-derobit-ws-python-sample")

conn = Bitfinex()

books = []
instruments = []

if args.num_instruments:
    instruments += ['t' + t.upper() for t in SYMBOLS[:args.num_instruments]]
else:
    instruments += args.instrument

counter = Counter()
loop = asyncio.get_event_loop()


async def on_change(book: L2OrderBook):
    start_at = time() * 1000
    msg = dict(asks=book.asks[:25], bids=book.bids[:25])
    message = json.dumps(msg)
    counter.pack_msg.count_it(time() * 1000 - start_at)

    start_at = time() * 1000
    data = json.loads(message)
    len(data)
    counter.unpack_msg.count_it(time() * 1000 - start_at)


async def subscribe():
    for instrument in instruments:
        order_book = L2OrderBook(instrument)
        books.append(order_book)
        await order_book.subscribe_book(conn, counter.add, on_change)


def stop():
    asyncio.ensure_future(conn.stop())


if args.stop_in:
    loop.call_later(args.stop_in, stop)

conn.on_connect_ws = subscribe

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
except Exception as e:
    print(e)
    print(conn.last_message)

print("Number of instruments:", len(instruments))
counter.report()
