from __future__ import annotations
import heapq, math, random
from typing import List, Sequence
from uuid import UUID
import numpy as np

def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

# ---------- base ----------
class BaseIndex:
    def knn(self, vec: List[float], k: int) -> List[UUID]:
        raise NotImplementedError

# ---------- 1. linear scan ----------
class LinearScan(BaseIndex):
    def __init__(self, vecs: List[List[float]], ids: List[UUID]):
        self.vecs, self.ids = vecs, ids

    def knn(self, vec: List[float], k: int) -> List[UUID]:
        scored = [(cosine(vec, v), i) for v, i in zip(self.vecs, self.ids)]
        return [i for _, i in heapq.nlargest(k, scored)]

# ---------- 2. KD-tree (low-dim) ----------
class KDNode:
    __slots__ = ("pivot", "left", "right", "id", "vec")

    def __init__(self, vecs, ids, depth=0):
        if not vecs:
            self.vec = self.id = self.left = self.right = None
            return
        k = len(vecs[0])
        axis = depth % k
        sorted_pairs = sorted(zip(vecs, ids), key=lambda p: p[0][axis])
        median = len(sorted_pairs) // 2
        self.vec, self.id = sorted_pairs[median]
        left_pairs = sorted_pairs[:median]
        right_pairs = sorted_pairs[median + 1 :]
        self.left = KDNode([v for v, _ in left_pairs], [i for _, i in left_pairs], depth + 1) if left_pairs else None
        self.right = KDNode([v for v, _ in right_pairs], [i for _, i in right_pairs], depth + 1) if right_pairs else None
        self.pivot = axis

    def search(self, target, k, heap):
        if self.vec is None:
            return
        dist = cosine(target, self.vec)
        if len(heap) < k:
            heapq.heappush(heap, (dist, self.id))
        else:
            heapq.heappushpop(heap, (dist, self.id))
        axis = self.pivot
        near, far = (self.left, self.right) if target[axis] < self.vec[axis] else (self.right, self.left)
        if near:
            near.search(target, k, heap)
        # naive pruning (good enough for demo)
        if far:
            far.search(target, k, heap)

class KDTree(BaseIndex):
    def __init__(self, vecs, ids):
        self.root = KDNode(vecs, ids)

    def knn(self, vec, k):
        heap = []
        self.root.search(vec, k, heap)
        return [i for _, i in heapq.nlargest(k, heap)]

# ---------- 3. Random-projection LSH ----------
class RandomProjection(BaseIndex):
    def __init__(self, vecs, ids, planes: int = 12):
        self.planes = [np.random.randn(len(vecs[0])) for _ in range(planes)]
        self.tables = {}
        for v, i in zip(vecs, ids):
            key = self._hash(v)
            self.tables.setdefault(key, []).append((v, i))

    def _hash(self, vec):
        bits = ["1" if np.dot(vec, p) >= 0 else "0" for p in self.planes]
        return "".join(bits)

    def knn(self, vec, k):
        bucket = self.tables.get(self._hash(vec), [])
        return LinearScan([v for v, _ in bucket], [i for _, i in bucket]).knn(vec, k)
