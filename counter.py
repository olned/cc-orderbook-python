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
        return {'name': self.name, 'min_time': self.min_time, 'max_time': self.max_time,
                'avg_time': self.total_time / self.count}

    def get_dict(self):
        return {f'{self.code}_min_time': self.min_time,
                f'{self.code}_max_time': self.max_time,
                f'{self.code}_avg_time': self.total_time / self.count}

    def print(self):
        print("{name} - avg: {avg_time}, min: {min_time}, max: {max_time}".format(**self.get()))


class Counter:
    def __init__(self):
        self.book_process = Parameter("book process", "book")
        self.ws_latency = Parameter("websocket latency", "ws")
        self.pack_msg = Parameter("pack msg", "pack")
        self.unpack_msg = Parameter("unpack msg", "unpack")

    def add(self, server_time, start_at, end_at):
        self.book_process.count_it(end_at - start_at)
        self.ws_latency.count_it(start_at - server_time)

    def report(self):
        if self.book_process.count:
            self.book_process.print()
            self.ws_latency.print()
            self.pack_msg.print()
            self.unpack_msg.print()
            print(f"total count {self.book_process.count}")

    def get_dict(self):
        return {
            'total_changes': self.book_process.count,
            **self.ws_latency.get_dict(),
            **self.book_process.get_dict(),
            **self.pack_msg.get_dict(),
            **self.unpack_msg.get_dict(),
        }
