#!/usr/bin/env python3
"""Vector clocks for distributed event ordering."""
import sys, json

class VectorClock:
    def __init__(self, node_id=None, clocks=None):
        self.clocks = dict(clocks) if clocks else {}
        if node_id: self.clocks.setdefault(node_id, 0)
    def increment(self, node_id):
        self.clocks[node_id] = self.clocks.get(node_id, 0) + 1
        return self
    def merge(self, other):
        result = VectorClock(clocks=self.clocks)
        for k, v in other.clocks.items():
            result.clocks[k] = max(result.clocks.get(k, 0), v)
        return result
    def __le__(self, other):
        return all(self.clocks.get(k, 0) <= other.clocks.get(k, 0) for k in self.clocks)
    def __lt__(self, other): return self <= other and self.clocks != other.clocks
    def __eq__(self, other): return self.clocks == other.clocks
    def concurrent(self, other): return not (self <= other) and not (other <= self)
    def __repr__(self): return f"VC({self.clocks})"

def main():
    if len(sys.argv) < 2: print("Usage: vector_clock.py <demo|test>"); return
    if sys.argv[1] == "test":
        a = VectorClock("A").increment("A")
        b = VectorClock("B").increment("B")
        assert a.concurrent(b)
        c = a.merge(b).increment("A")
        assert a < c; assert b < c
        assert not c < a
        d = VectorClock("A").increment("A").increment("A")
        assert a < d
        e = VectorClock(clocks={"A": 1}); f = VectorClock(clocks={"A": 1})
        assert e == f; assert not e.concurrent(f)
        print("All tests passed!")
    else:
        a = VectorClock("A").increment("A"); print(f"A sends: {a}")
        b = VectorClock("B").increment("B"); print(f"B sends: {b}")
        print(f"Concurrent? {a.concurrent(b)}")
        c = a.merge(b).increment("A"); print(f"Merged at A: {c}")

if __name__ == "__main__": main()
