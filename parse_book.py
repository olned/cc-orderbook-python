import argparse
import csv
import json
import logging.config

from time import time_ns

import yaml

from orderbook import L2OrderBook

parser = argparse.ArgumentParser('Bitfinex Order Book Parser.')
parser.add_argument('input_file', help='Input File Name')
parser.add_argument('-c', '--config')
parser.add_argument('-o', '--output', default='report.csv', help='Name the csv file to report')
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

books = {}
instruments = []
prev_local_ts = None
processing_time = None
interval = 0
report = []


def parse_list(message: list):
    book = books[message[0]]
    if book.handle_message(message):
        if len(book.bids) >= 25 and len(book.asks) >= 25:
            msg = dict(asks=book.asks[:25], bids=book.bids[:25])
            snapshot_message = json.dumps(msg)
            len(snapshot_message)


def parse_dict(message: dict):
    if "event" in message:
        if message["event"] == "subscribed":
            books[message["chanId"]] = L2OrderBook(instrument=message["symbol"])
        else:
            logger.info(repr(dict))
    else:
        logger.warning(f"Unknown message {message}")


with open(args.input_file, newline='') as f:
    csv_reader = csv.reader(f, delimiter=';')
    for row in csv_reader:
        o = json.loads(row[0])
        local_ts = int(row[1])  # ns

        if prev_local_ts:
            interval = local_ts - prev_local_ts
            # interval between this and previous message
            # processing_time for previous message
            report.append([interval, processing_time])

        start_at = time_ns()
        if isinstance(o, list):
            parse_list(o)
        else:
            parse_dict(o)

        processing_time = time_ns() - start_at
        prev_local_ts = local_ts

with open(args.output, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['interval', 'processing_time'])
    for item in report:
        csv_writer.writerow(item)
