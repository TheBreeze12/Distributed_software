import threading
import time


class SnowflakeGenerator:
    """简单雪花算法实现，生成全局唯一、有序的业务订单号。"""

    def __init__(self, worker_id: int = 1, datacenter_id: int = 1):
        self.worker_id_bits = 5
        self.datacenter_id_bits = 5
        self.sequence_bits = 12

        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_id_bits)

        if worker_id > self.max_worker_id or worker_id < 0:
            raise ValueError("worker_id out of range")
        if datacenter_id > self.max_datacenter_id or datacenter_id < 0:
            raise ValueError("datacenter_id out of range")

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id

        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = (
            self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits
        )
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)

        self.twepoch = 1704067200000  # 2024-01-01 00:00:00 UTC
        self.last_timestamp = -1
        self.sequence = 0
        self._lock = threading.Lock()

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _next_millis(self, last_timestamp: int) -> int:
        ts = self._timestamp()
        while ts <= last_timestamp:
            ts = self._timestamp()
        return ts

    def next_id(self) -> int:
        with self._lock:
            timestamp = self._timestamp()

            if timestamp < self.last_timestamp:
                raise RuntimeError("Clock moved backwards")

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.sequence_mask
                if self.sequence == 0:
                    timestamp = self._next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            return (
                ((timestamp - self.twepoch) << self.timestamp_left_shift)
                | (self.datacenter_id << self.datacenter_id_shift)
                | (self.worker_id << self.worker_id_shift)
                | self.sequence
            )


_generator = SnowflakeGenerator()


def generate_order_id() -> str:
    return str(_generator.next_id())
