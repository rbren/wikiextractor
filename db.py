import pymysql.cursors

import warnings
import logging
import os

DELETE_FIRST = False

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

def process_document(doc_id, title, token_counts):
    logging.info("add %s %s", doc_id, title)
    add_document(doc_id, title)
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

def add_document(id, title):
    return execute("INSERT IGNORE INTO documents (id, title) VALUES (%s, %s)", (id, title))

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

if __name__ == "__main__":
    process_document(1, "doc 1", {"c": 3, "a": 1, "b": 2})
    process_document(2, "doc 2", {"c": 2, "a": 10, "d": 4})
