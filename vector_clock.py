#!/usr/bin/env python3
"""vector_clock - Vector clocks for distributed event ordering."""
import sys

class VectorClock:
    def __init__(self, node_id, nodes):
        self.node_id = node_id
        self.clock = {n: 0 for n in nodes}
    def tick(self):
        self.clock[self.node_id] += 1
        return dict(self.clock)
    def send(self):
        self.tick()
        return dict(self.clock)
    def receive(self, other_clock):
        for node, time in other_clock.items():
            self.clock[node] = max(self.clock.get(node, 0), time)
        self.tick()
    def happened_before(self, other):
        return all(self.clock.get(n, 0) <= other.get(n, 0) for n in set(self.clock) | set(other)) and self.clock != other
    def concurrent(self, other):
        return not self.happened_before(other) and not VectorClock._hb(other, self.clock)
    @staticmethod
    def _hb(a, b):
        return all(a.get(n, 0) <= b.get(n, 0) for n in set(a) | set(b)) and a != b

def test():
    nodes = ["A", "B", "C"]
    a = VectorClock("A", nodes)
    b = VectorClock("B", nodes)
    c = VectorClock("C", nodes)
    msg1 = a.send()
    assert msg1 == {"A": 1, "B": 0, "C": 0}
    b.receive(msg1)
    assert b.clock["A"] == 1 and b.clock["B"] == 1
    msg2 = b.send()
    c.receive(msg2)
    assert c.clock["B"] == 2
    # A's clock happened before B's after receive
    assert a.happened_before(b.clock)
    # concurrent events
    a.tick()
    c.tick()
    assert a.concurrent(c.clock)
    print("OK: vector_clock")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: vector_clock.py test")
