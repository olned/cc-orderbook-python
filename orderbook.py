from time import time

from half_book import HalfSnap


class L2OrderBook:
    handle_time = None
    on_changed = None

    def __init__(self, instrument: str):
        self.instrument = instrument
        self._bids = HalfSnap(True)
        self._asks = HalfSnap(False)

    def is_empty(self):
        return len(self.bids) == 0

    @property
    def bids(self):
        return self._bids.data

    @property
    def asks(self):
        return self._asks.data

    def get_side(self, side: str):
        if side == 'bids' or side == 'buy':
            return self._bids
        elif side == 'asks' or side == 'sell':
            return self._asks
        else:
            return None

    def set_snapshot(self, message):
        self.asks.clear()
        self.bids.clear()
        for item in message[1]:
            price = item[2]
            if price < 0:
                self.asks.add([item[0], -price])
            else:
                self.bids.add([item[0], price])

    def set_l2update(self, message):
        price = message[1][0]
        size = message[1][2]
        count = message[1][1]
        if size < 0:
            if count == 0:
                self._asks.update(price, 0.)
            else:
                self._asks.update(price, -size)
        else:
            if count == 0:
                self._bids.update(price, 0.)
            else:
                self._bids.update(price, size)

    async def handle_subscription(self, message):
        if isinstance(message[1][0], list):
            self.set_snapshot(message)
        elif isinstance(message[1][0], str):
            pass
        else:
            start_at = time() * 1000
            server_time = message[-1]

            self.set_l2update(message)

            self.handle_time(server_time, start_at, time() * 1000)
            if self.on_changed:
                await self.on_changed(self)

    async def subscribe_book(self, conn, handle_time, on_changed=None):
        self.handle_time = handle_time
        self.on_changed = on_changed
        await conn.subscribe({
            "channel": "book",
            "symbol": self.instrument
        }, handler=self.handle_subscription)
