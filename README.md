# WikiVectors
This is a fork of [WikiExtractor](https://github.com/attardi/wikiextractor).

This project processes a [Wikipedia Dump](https://dumps.wikimedia.org/) to
create a distributed-bag-of-words model for each English-language article.
Effectively, it counts the number of times a particular word occurs in
each article.

The extractor crawls through each article, passing it through a custom
[spaCy tokenizer](https://spacy.io/api/tokenizer),
and sends the resulting word counts to a MySQL database.

## Setup

### Database
You'll need to set up a MySQL database, and set the following env variables:

```
MS_PASSWORD
MS_USER
MS_HOST
MS_DATABASE
```

### Category Links
Wikipedia provides a MySQL backup of all links to category pages.
We can ingest these and clean up some of the ones we don't need.

Note that the database is huge, and will take hours to ingest.
```
curl -L "https://dumps.wikimedia.org/enwiki/20200401/enwiki-20200401-categorylinks.s
ql.gz" > catlinks.sql
mysql -h $MS_HOST -u $MS_USER -D $MS_DATABASE --password=$MS_PASSWORD < catlinks.sql
# this will take hours
rm -rf catlinks.sql
```

To cut down on the size of the database, you can delete some of the less
helpful categories:
```
DELETE FROM categorylinks WHERE
  cl_to LIKE '%isambiguation%' OR
  cl_to LIKE 'Pages_%' OR
  cl_to LIKE '%_pages' OR
  cl_to LIKE '%rticles%' OR
  cl_to LIKE '%ikidata%' OR
  cl_to LIKE '%ikimedia%' OR
  cl_to LIKE '%ikipedia%' or
  cl_to LIKE 'Files_%' OR
  cl_to LIKE '%_files' or
  cl_to LIKE '%edirects%' OR
  cl_to LIKE '%free_media' OR
  cl_to LIKE '%_templates' OR
  cl_to LIKE 'CS1%' OR
  cl_to LIKE '%_no_TOC';
```

### Word Count Data
You can use the following commands to run the script locally.
But note that it will probably take months to complete!
```
curl -L "http://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.b
z2" > wiki.dump.bz2
python3 main.py
```

To process faster, you can use a Kubernetes cluster to run
many parallel extraction tasks.

By default, we'll create 20 parallel jobs to run in our Kubernetes cluster.
This will finish in 4-5 days.

To start the jobs, run:
```
./deploy/expand.sh
kubectl apply -f ./deploy/jobs
```

We suggest using a log aggregator [like stern](https://github.com/wercker/stern)
to watch the output.
