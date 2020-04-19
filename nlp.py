from spacy.tokenizer import Tokenizer
from spacy.lang.en import English

nlp = English()
sentencizer = nlp.create_pipe("sentencizer")
nlp.add_pipe(sentencizer)
tokenizer = nlp.Defaults.create_tokenizer(nlp)

def get_token_counts(text):
    token_counts = {}
    tokens = tokenizer(text)
    for tok in tokens:
        tok = str(tok).lower()
        if tok not in token_counts:
            token_counts[tok] = 0
        token_counts[tok] += 1
    return token_counts

if __name__ == "__main__":
    print(get_token_counts("Hello 'there' my 'friend'. hello..."))
