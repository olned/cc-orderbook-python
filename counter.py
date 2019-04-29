class Parameter:
    min_time = 0.0
    max_time = 0.0
    total_time = 0.0
    count = 0

    def __init__(self, name, code):
        self.name = name
        self.code = code

    def count_it(self, new_time):
        self.count += 1
        if not self.min_time or new_time < self.min_time:
            self.min_time = new_time

        if not self.max_time or new_time > self.max_time:
            self.max_time = new_time

        self.total_time += new_time

    def get(self):
        return {'name': self.name,
                'min_time': self.min_time,
                'max_time': self.max_time,
                "total_time": self.total_time,
                'count': self.count,
                'avg_time': self.total_time / self.count}

    def get_dict(self):
        return {f'{self.code}_min_time': self.min_time,
                f'{self.code}_max_time': self.max_time,
                f'{self.code}_count': self.count,
                f'{self.code}_total_time': self.total_time,
                f'{self.code}_avg_time': self.total_time / self.count}

    def print(self):
        print("{name:20} - avg: {avg_time:.6f}, min: {min_time:.6f}, max: {max_time:.6f}, "
              "total: {total_time:.6f}, count: {count}".format(**self.get()))


class Counter:
    def __init__(self):
        self.ws_latency = Parameter("websocket latency", "ws")
        self.unpack_and_route = Parameter("unpack and route incoming messages", "unpack_and_route")
        self.book_process = Parameter("book process", "book")
        self.pack_msg = Parameter("simulation pack", "pack_snap")
        self.unpack_msg = Parameter("simulation unpack", "unpack_snap")

    def add(self, server_time, receipt_time, start_at, end_at):
        self.ws_latency.count_it(receipt_time - server_time)
        self.unpack_and_route.count_it(start_at - receipt_time)
        self.book_process.count_it(end_at - start_at)

    def report(self):
        if self.ws_latency.count:
            self.ws_latency.print()
            self.unpack_and_route.print()
            self.book_process.print()
            self.pack_msg.print()
            self.unpack_msg.print()
            print(f"number of changes {self.ws_latency.count}")

    def get_dict(self):
        return {
            **self.ws_latency.get_dict(),
            **self.unpack_and_route.get_dict(),
            **self.book_process.get_dict(),
            **self.pack_msg.get_dict(),
            **self.unpack_msg.get_dict(),
        }
