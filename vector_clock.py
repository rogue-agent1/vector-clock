#!/usr/bin/env python3
"""Vector clocks for distributed event ordering."""
import sys

class VectorClock:
    def __init__(self, node_id, n_nodes):
        self.node_id = node_id
        self.clock = [0] * n_nodes
    def tick(self):
        self.clock[self.node_id] += 1
        return tuple(self.clock)
    def send(self):
        self.tick()
        return tuple(self.clock)
    def receive(self, other_clock):
        for i in range(len(self.clock)):
            self.clock[i] = max(self.clock[i], other_clock[i])
        self.tick()
        return tuple(self.clock)
    def happens_before(self, other):
        return all(a <= b for a, b in zip(self.clock, other)) and any(a < b for a, b in zip(self.clock, other))
    def concurrent(self, other):
        return not self.happens_before(other) and not all(a >= b for a, b in zip(other, self.clock)) or (
            any(a < b for a, b in zip(self.clock, other)) and any(a > b for a, b in zip(self.clock, other)))
    def __repr__(self):
        return f"VC({self.clock})"

def test():
    a = VectorClock(0, 3)
    b = VectorClock(1, 3)
    c = VectorClock(2, 3)
    a.tick()  # a=[1,0,0]
    msg = a.send()  # a=[2,0,0]
    b.receive(msg)  # b=[2,1,0]
    assert b.clock == [2, 1, 0]
    c.tick()  # c=[0,0,1]
    # a happens-before b
    assert a.happens_before(tuple(b.clock))
    # c is concurrent with a
    assert not a.happens_before(tuple(c.clock))
    assert not all(a_ >= b_ for a_, b_ in zip(tuple(c.clock), a.clock))
    print("  vector_clock: ALL TESTS PASSED")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Vector clocks for distributed systems")
