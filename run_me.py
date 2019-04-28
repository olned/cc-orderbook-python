import argparse
import asyncio
import csv
import json
import logging.config
import os
import sys
from time import time
from traceback import format_tb

import yaml
from ssc2ce import Bitfinex

from counter import Counter
from instruments import SYMBOLS
from orderbook import L2OrderBook

parser = argparse.ArgumentParser('Bitfinex Order Book Example.')
parser.add_argument('-s', '--stop', dest='stop_in', type=int, default=0,
                    help='Stop the script after a specified time in seconds. Default 0 - do not stop')
parser.add_argument('-c', '--config')
parser.add_argument('-n', '--num_instruments', type=int, default=None,
                    help='Get first N instruments from the instruments.py file. Default None - do not use')
parser.add_argument('-i', '--instrument', nargs='*', dest='instrument', default=['tBTCUSD'])
parser.add_argument('-o', '--output', help='Name the csv file to add report')
args = parser.parse_args()

if args.config:
    with open(args.config) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

        log_config = config.get('log')
else:
    log_config = None

if log_config:
    logging.config.dictConfig(log_config)
else:
    logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.WARNING)

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

app_start_at = time()
try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    logger.info("Application closed by KeyboardInterrupt.")
except Exception as e:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    logger.error("While handling message {} Unknown Exception {} {}".
                 format(conn.last_message,
                        e.__class__.__name__,
                        repr(format_tb(exc_traceback))))

if args.output:
    result = {
        'instr_num': len(instruments),
        'total_time': (time() - app_start_at),
        **counter.get_dict()
    }
    if not os.path.exists(args.output):
        dirname = os.path.dirname(args.output)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(args.output, 'w') as f:
            w = csv.DictWriter(f, result.keys())
            w.writeheader()
            w.writerow(result)
    else:
        with open(args.output, 'a') as f:
            w = csv.DictWriter(f, result.keys())
            w.writerow(result)
else:
    print(f"Number of instruments: {len(instruments)}\nestimated {round((time() - app_start_at), 2)} sec\n"
          f"{'=' * 7} Time Measurements in ms {'=' * 7}")
    counter.report()
