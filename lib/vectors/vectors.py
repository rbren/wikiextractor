import math
import statistics
import numpy as np
from ..extract import db

MIN_APPEARANCE_RATIO = .1
STD_DEV_CUTOFF = 0.0

NUM_DOCS_FOR_IDF = 1000
IDFs = {}

def get_idfs(docs):
    num_docs_for_tok = {}
    for doc in docs:
        for tok in doc:
            if tok not in num_docs_for_tok:
                num_docs_for_tok[tok] = 0
            num_docs_for_tok[tok] += 1
    idfs = {}
    for tok in num_docs_for_tok:
        idfs[tok] = math.log(float(len(docs)) / float(num_docs_for_tok[tok]))
    return idfs

def initialize():
    global IDFs
    doc_ids = db.get_random_articles(NUM_DOCS_FOR_IDF)
    details = db.get_token_counts_for_documents(doc_ids)
    docs = [details[id] for id in doc_ids]
    IDFs = get_idfs(docs)

initialize()

def get_idf(token):
    if token in IDFs:
        return IDFs[token]
    return math.log(float(NUM_DOCS_FOR_IDF) / 1.0)

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
    sub_idfs = get_idfs(docs)
    tfs = [get_frequencies(doc) for doc in docs]
    all_tokens = []
    for doc in docs:
        for token in doc:
            if token in all_tokens: continue
            if get_idf(token) < math.log(2): continue # occurs in > 1/2 docs
            if sub_idfs[token] > math.log(10): continue # occurs in < 1/10 docs in this cat
            all_tokens.append(token)

    all_tokens = sorted(all_tokens, key=lambda tok: sub_idfs[tok])

    vectors = [[] for d in docs]
    for tok in all_tokens:
        for j in range(len(vectors)):
            tf = tfs[j][tok] if tok in tfs[j] else 0.0
            idf = get_idf(tok)
            vectors[j].append(tf * idf)

    return np.array(vectors), [sub_idfs[t] for t in all_tokens], all_tokens

if __name__ == '__main__':
    cat = '20th-century_musicologists'
    docs = db.get_documents_for_category(cat)
    vecs, idfs, toks = get_vectors([doc['id'] for doc in docs])
    print('got', len(toks))
    for i in range(len(toks)):
        print(toks[i], idfs[i])
