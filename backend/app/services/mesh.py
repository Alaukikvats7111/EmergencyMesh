from collections import defaultdict
from threading import Lock

class MeshManager:
    def __init__(self):
        self.seen: dict[str, int] = {}
        self.lock = Lock()
        self.edges = defaultdict(set)
        self.gateway_online = True

    def should_forward(self, message_id: str, ttl: int) -> bool:
        with self.lock:
            if ttl <= 0 or message_id in self.seen:
                return False
            self.seen[message_id] = ttl
            return True

    def topology(self):
        return {k: sorted(v) for k, v in self.edges.items()}

mesh = MeshManager()
