#!/usr/bin/env python3
"""vector_clock - Vector clocks for causal ordering."""
import sys

class VectorClock:
    def __init__(self, node_id=None):
        self.clock = {}
        self.node_id = node_id
    
    def increment(self, node_id=None):
        nid = node_id or self.node_id
        self.clock[nid] = self.clock.get(nid, 0) + 1
        return self
    
    def get(self, node_id):
        return self.clock.get(node_id, 0)
    
    def merge(self, other):
        result = VectorClock(self.node_id)
        all_keys = set(self.clock) | set(other.clock)
        for k in all_keys:
            result.clock[k] = max(self.clock.get(k, 0), other.clock.get(k, 0))
        return result
    
    def __le__(self, other):
        """Happens-before or equal."""
        for k, v in self.clock.items():
            if v > other.clock.get(k, 0):
                return False
        return True
    
    def __lt__(self, other):
        """Strictly happens-before."""
        return self <= other and self != other
    
    def __eq__(self, other):
        all_keys = set(self.clock) | set(other.clock)
        return all(self.clock.get(k, 0) == other.clock.get(k, 0) for k in all_keys)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def concurrent(self, other):
        return not (self <= other) and not (other <= self)
    
    def dominates(self, other):
        return other < self
    
    def __repr__(self):
        return f"VC({dict(sorted(self.clock.items()))})"
    
    def copy(self):
        vc = VectorClock(self.node_id)
        vc.clock = dict(self.clock)
        return vc

class CausalHistory:
    def __init__(self):
        self.events = []
    
    def add(self, node_id, clock, data):
        self.events.append({"node": node_id, "clock": clock.copy(), "data": data})
    
    def causal_order(self):
        """Return events in causal order."""
        ordered = []
        remaining = list(self.events)
        while remaining:
            # Find events whose dependencies are all in ordered
            ready = []
            for e in remaining:
                if all(e["clock"].clock.get(o["node"], 0) <= o["clock"].get(e["node"]) 
                       for o in ordered if o["node"] != e["node"]):
                    ready.append(e)
            if not ready:
                ready = [remaining[0]]  # Break ties
            # Pick one with smallest clock
            chosen = min(ready, key=lambda e: sum(e["clock"].clock.values()))
            ordered.append(chosen)
            remaining.remove(chosen)
        return ordered

def test():
    a = VectorClock("a")
    b = VectorClock("b")
    
    a.increment()  # a:{a:1}
    assert a.get("a") == 1
    
    b.increment()  # b:{b:1}
    
    # Concurrent
    assert a.concurrent(b)
    assert not a < b
    assert not b < a
    
    # Merge
    c = a.merge(b)
    assert c.get("a") == 1
    assert c.get("b") == 1
    
    # Happens-before
    a2 = a.copy()
    a2.increment()  # a:{a:2}
    assert a < a2
    assert not a2 < a
    assert a2.dominates(a)
    
    # Send/receive pattern
    sender = VectorClock("s")
    receiver = VectorClock("r")
    sender.increment()  # s sends
    received = receiver.merge(sender)
    received.increment()  # r processes
    assert sender < received
    
    # Equality
    x = VectorClock("x")
    y = VectorClock("x")
    assert x == y
    x.increment()
    assert x != y
    
    print("All tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: vector_clock.py test")
