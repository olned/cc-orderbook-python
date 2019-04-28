from sortedcontainers import SortedKeyList


VERY_SMALL_NUMBER = 1e-13


class HalfSnap:

    def __init__(self, bids: bool):
        if bids:
            self.data = SortedKeyList(key=lambda val: -val[0])
        else:
            self.data = SortedKeyList(key=lambda val: val[0])
        self.is_bids = bids
        self.time = None

    def fill(self, source):
        self.data.clear()
        for item in source:
            self.add(item)

    def add(self, item):
        price = item[0]
        size = item[1]
        self.data.add([price, size])

    def update(self, price: float, size: float):
        key = -price if self.is_bids else price
        i = self.data.bisect_key_left(key)

        if 0 <= i < len(self.data):
            value = self.data[i]
        else:
            if size <= VERY_SMALL_NUMBER:
                return False

            self.data.add([price, size])
            return True

        if size <= VERY_SMALL_NUMBER:
            if value[0] == price:
                self.data.discard(value)
                return True
            else:
                return False

        if value[0] == price:
            self.data[i][1] = size
        else:
            self.data.add([price, size])
        return True

    def delete(self, price: float):
        return self.updatef(price, 0.0)

