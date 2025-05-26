from app.infrastructure.indexing import LinearScan
import numpy as np, uuid, random

def test_knn_exact():
    vecs = [np.random.randn(4).tolist() for _ in range(10)]
    ids = [uuid.uuid4() for _ in vecs]
    index = LinearScan(vecs, ids)
    q = vecs[3]
    assert ids[3] in index.knn(q, k=3)
