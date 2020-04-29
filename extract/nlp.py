import logging
import re
import time

from spacy.tokenizer import Tokenizer
from spacy.lang.en import English

from timeout import timeout

MAX_TOKENIZE_TIME = 5

nlp = English()
sentencizer = nlp.create_pipe("sentencizer")
nlp.add_pipe(sentencizer)
tokenizer = nlp.Defaults.create_tokenizer(nlp)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def normalize(s):
    txt = str(s).encode("ascii", errors="ignore").decode().lower().strip()
    txt = re.sub(r'[^a-z]', '', txt)
    return txt

def get_token_counts(text):
    start = time.time()
    with timeout(MAX_TOKENIZE_TIME):
        token_counts = {}
        logging.info("tokenize %d", len(text))
        tokens = tokenizer(text)
        logging.info("tokenized %d", len(text))
        for tok in tokens:
            tok = normalize(tok)
            if tok == '':
                continue
            if tok not in token_counts:
                token_counts[tok] = 0
            token_counts[tok] += 1
    end = time.time()
    logging.info("tok took %.2fs", end - start)
    return token_counts

if __name__ == "__main__":
    print(get_token_counts("Hello 'there' my- foo-bar 7th 8-bit 'friend'. 7.83 9 hello... (where am i) (as"))
