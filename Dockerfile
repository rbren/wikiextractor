FROM python:3.8.2-buster

COPY wiki.dump.bz2 wiki.dump.bz2
RUN python -m pip install spacy PyMySQL
ENV PYTHONUNBUFFERED=1

COPY *.py ./

CMD "python ngrams.py"
