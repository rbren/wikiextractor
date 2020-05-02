import pymysql.cursors

import warnings
import logging
import os
import zlib
import base64

DELETE_FIRST = True

dbname = os.environ["MS_DATABASE"]
host = os.environ["MS_HOST"]
user = os.environ["MS_USER"]
pw = os.environ["MS_PASSWORD"]

connection = pymysql.connect(user=user, password=pw,
                              host=host,
                              db=dbname)

MAX_INSERT = 1000

def execute(cmd, args, multi=False):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with connection.cursor() as cursor:
            cursor.execute(cmd, args)
    connection.commit()

def retrieve(cmd, args, multi=False):
    with connection.cursor() as cursor:
        cursor.execute(cmd, args)
        return cursor.fetchall() if multi else cursor.fetchone()

def close():
    connection.close()

def process_document(doc_id, title, text, token_counts=None):
    logging.info("add %s %s", doc_id, title)
    add_document(doc_id, title, text)
    if token_counts is None:
        return

    tokens = list(token_counts.keys())
    tokens.sort()
    logging.info("tok %s %s %d", doc_id, title, len(tokens))
    token_ids = get_tokens(tokens)
    to_add = [t for t in tokens if t not in token_ids]
    if len(to_add) > 0:
        logging.info("add tok %s %s %d", doc_id, title, len(to_add))
        add_tokens(to_add)
        logging.info("get ids %s %s %d", doc_id, title, len(to_add))
        added = get_tokens(to_add)
        token_ids = {**token_ids, **added}
    counts = []
    counts = [(doc_id, token_ids[token], token_counts[token]) for token in token_ids]
    counts.sort()
    logging.info("add cts %s %s %d", doc_id, title, len(counts))
    add_token_counts(counts)

def add_document(id, title, text):
    text = zlib.compress(bytes(text, 'utf-8'))
    text = base64.b64encode(text)
    return execute("INSERT INTO documents (id, title, text) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE text=VALUES(text)", (id, title, text))

def add_tokens(tokens):
    if len(tokens) > MAX_INSERT:
        add_tokens(tokens[:MAX_INSERT])
        add_tokens(tokens[MAX_INSERT:])
        return
    tokens = [str(t) for t in tokens]
    q = "INSERT IGNORE INTO tokens (token) VALUES " + ", ".join(["(%s)"] * len(tokens))
    execute(q, tokens, True)

def get_tokens(tokens):
    q = "SELECT token, id FROM tokens WHERE token IN ("
    q += ", ".join(["%s"] * len(tokens)) + ")"
    all = retrieve(q, tokens, True)
    map = {}
    for data in all:
        map[data[0]] = data[1]
    return map

def add_token_counts(counts):
    if len(counts) > MAX_INSERT:
        add_token_counts(counts[:MAX_INSERT])
        add_token_counts(counts[MAX_INSERT:])
        return
    if DELETE_FIRST:
        delete_token_counts(counts)
    q = "INSERT INTO token_counts (document, token, num) VALUES "
    q += ", ".join(["(%s, %s, %s)"] * len(counts))
    q += " ON DUPLICATE KEY UPDATE num=VALUES(num)"
    values = [item for sublist in counts for item in sublist]
    execute(q, values, True)

def delete_token_counts(counts):
    if len(counts) > MAX_INSERT:
        delete_token_counts(counts[:MAX_INSERT])
        delete_token_counts(counts[MAX_INSERT:])
        return
    q = "DELETE FROM token_counts WHERE (document, token) IN "
    q += "(" + ", ".join(["(%s, %s)"] * len(counts)) + ")"
    values = [item for sublist in counts for item in sublist[0:2]]
    execute(q, values, True)

def get_documents_for_category(cat_id):
    q = """
    SELECT cl_from, title
    FROM categorylinks
    INNER JOIN documents
        ON documents.id=cl_from
    WHERE cl_to=%s
    """
    results = retrieve(q, [cat_id], True)
    return [{'id': r[0], 'title': r[1]} for r in results]

def get_token_counts_for_document(id):
    print("get toks", id)
    q = """
    SELECT tokens.token, num from token_counts
        INNER JOIN tokens
        ON tokens.id=token_counts.token
    WHERE
        document=%s
    ORDER BY num
    """
    results = retrieve(q, [id], True)
    ret = {}
    for res in results:
        ret[res[0]] = res[1]
    return ret

def get_token_counts_for_documents(ids):
    q = """
    SELECT document, tokens.token, num from token_counts
        INNER JOIN tokens
        ON tokens.id=token_counts.token
    WHERE
        document IN (
    """ + ", ".join(["%s" for id in ids]) + ")"
    q += " ORDER BY num"

    results = retrieve(q, ids, True)
    ret = {}
    for id in ids:
        ret[id] = {}
    for res in results:
        id = res[0]
        token = res[1]
        count = res[2]
        ret[id][token] = count
    return ret

def get_categories():
    q = """
    SELECT cl_to, count(*) as num FROM categorylinks
    WHERE
      cl_to NOT LIKE '%%_births' AND
      cl_to NOT LIKE '%%_deaths'
    GROUP BY cl_to
    HAVING num >= 100
    ORDER BY num DESC
    """
    results = retrieve(q, [], True)
    return [{'name': r[0].decode('utf-8'), 'count': r[1]} for r in results]

def get_random_articles(num):
    q = """
    SELECT id from documents
    LIMIT %s
    """
    results = retrieve(q, [num], True)
    return [a[0] for a in results]

if __name__ == "__main__":
    process_document(1, "doc 1", {"c": 3, "a": 1, "b": 2})
    process_document(2, "doc 2", {"c": 2, "a": 10, "d": 4})
