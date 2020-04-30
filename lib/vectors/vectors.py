import statistics
import numpy as np
from ..extract import db

MIN_APPEARANCE_RATIO = .1
STD_DEV_CUTOFF = 2.5

def get_frequencies(doc):
    doc_total = 0
    for tok in doc:
        doc_total += doc[tok]
    freqs = {}
    for tok in doc:
        freqs[tok] = float(doc[tok]) / float(doc_total)
    return freqs

def get_stddev(docs):
    freqs = {}
    for doc in docs:
        for tok in doc:
            freqs[tok] = []
    stddevs = {}
    for tok in freqs:
        num_docs = 0
        for doc in docs:
            if tok in doc:
                num_docs += 1
                freqs[tok].append(doc[tok])
            else:
                freqs[tok].append(0.0)
        doc_ratio = float(num_docs) / float(len(docs))
        if doc_ratio >= MIN_APPEARANCE_RATIO:
            stddevs[tok] = statistics.stdev(freqs[tok]) / statistics.mean(freqs[tok])
    return stddevs

def get_vectors(doc_ids):
    details = db.get_token_counts_for_documents(doc_ids)
    docs = [details[id] for id in doc_ids]
    freqs = [get_frequencies(doc) for doc in docs]
    stddev = get_stddev(freqs)

    stddev_sorted = []
    for tok in stddev:
        stddev_sorted.append((tok, stddev[tok]))
    stddev_sorted = sorted(stddev_sorted, key=lambda tup: tup[1])
    stddev_sorted = [s for s in stddev_sorted if s[1] > STD_DEV_CUTOFF]

    vectors = [[] for d in docs]
    for stddev in stddev_sorted:
        tok = stddev[0]
        for i in range(len(vectors)):
            val = freqs[i][tok] if tok in freqs[i] else 0.0
            vectors[i].append(val)
    return np.array(vectors)

if __name__ == '__main__':
    cat = '20th-century_musicologists'
    docs = db.get_documents_for_category(cat)
    print(get_vectors([doc['id'] for doc in docs]))
