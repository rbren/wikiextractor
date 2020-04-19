import psycopg2
import os

dbname = os.environ["PG_DATABASE"]
host = os.environ["PG_HOST"]
user = os.environ["PG_USER"]
pw = os.environ["PG_PASSWORD"]
conn_str = "dbname=%s host=%s user=%s password=%s" % (dbname, host, user, pw)
conn = psycopg2.connect(conn_str)

MAX_INSERT = 1000

def execute(cmd, args):
    cur = conn.cursor()
    cur.execute(cmd, args)
    result = cur.fetchall()
    cur.close()
    conn.commit()
    return result

def close():
    conn.close()

def process_document(id, title, token_counts):
    tokens = list(token_counts.keys())
    token_ids = add_tokens(tokens)
    token_ids = [i[0] for i in token_ids]
    add_document(id, title)
    counts = []
    for idx in range(len(tokens)):
        counts.append((id, token_ids[idx], token_counts[tokens[idx]]))
    add_token_counts(counts)

def add_document(id, title):
    return execute("INSERT INTO documents (id, title) VALUES (%s, %s) ON CONFLICT DO NOTHING returning id", (id, title))

def add_tokens(tokens):
    if len(tokens) > MAX_INSERT:
        ids = add_tokens(tokens[:MAX_INSERT])
        ids += add_tokens(tokens[MAX_INSERT:])
        return ids
    q = "INSERT INTO tokens (token) VALUES " + ", ".join(["(%s)"] * len(tokens))
    q += " ON CONFLICT (token) DO UPDATE SET dummy=true RETURNING id"
    return execute(q, [str(t) for t in tokens])

def add_token_counts(counts):
    if len(counts) > MAX_INSERT:
        ids = add_token_counts(counts[:MAX_INSERT])
        ids += add_token_counts(counts[MAX_INSERT:])
        return ids
    q = "INSERT INTO token_counts (document, token, num) VALUES "
    q += ", ".join(["(%s, %s, %s)"] * len(counts))
    q += " ON CONFLICT (token, document) DO UPDATE SET num=EXCLUDED.num RETURNING id"
    values = [item for sublist in counts for item in sublist]
    return execute(q, values)

if __name__ == "__main__":
    res = add_tokens(["foo", "bar", "foo"])
    print(res)
