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

You can then create the tables:
```
mysql -h $MS_HOST -u $MS_USER -D $MS_DATABASE --password=$MS_PASSWORD < migrations/001_init.sql
mysql -h $MS_HOST -u $MS_USER -D $MS_DATABASE --password=$MS_PASSWORD < migrations/002_text.sql
```

### Wikipedia Dumps
Wikipedia provides a MySQL backup of all links to category pages.
We can ingest these and clean up some of the ones we don't need.

Note that you should replace `20200401` with the latest date listed at dumps.wikimedia.org/enwiki

```
export TARGET_DATE=20200401
```

#### Pages
```
curl -L "https://dumps.wikimedia.org/enwiki/$TARGET_DATE/enwiki-$TARGET_DATE-page.sql.gz" > pages.sql.gz
gunzip pages.sql.gz
mysql -h $MS_HOST -u $MS_USER -D $MS_DATABASE --password=$MS_PASSWORD < pages.sql
rm -rf pages.sql
```

#### Category Links
Note that this table is huge, and will take hours to ingest.
```
curl -L "https://dumps.wikimedia.org/enwiki/$TARGET_DATE/enwiki-$TARGET_DATE-categorylinks.sql.gz" > catlinks.sql.gz
gunzip catlinks.sql.gz
mysql -h $MS_HOST -u $MS_USER -D $MS_DATABASE --password=$MS_PASSWORD < catlinks.sql
# this will take hours
rm -rf catlinks.sql
```

To cut down on the size of the database, you can delete some of the less
helpful categories:
```
DELETE FROM categorylinks WHERE
  cl_to='All_pages_needing_cleanup' OR
  cl_to='Old_requests_for_peer_review' OR
  cl_to='Exclude_in_print' OR
  cl_to='Cite_iucn_maint' OR
  cl_to='Dynamic_lists' OR
  cl_to='Track_variant_DoB' OR
  cl_to='Commons_category_link_is_locally_defined' OR
  cl_to='Navboxes_using_background_colours' OR
  cl_to='GFDL_files_with_disclaimers' OR
  cl_to='Former_good_article_nominees' OR
  cl_to='CanElecResTopTest_with_bare_year' OR
  cl_to='Transwikied_to_Wiktionary' OR
  cl_to LIKE 'Year_of_%' OR
  cl_to LIKE 'Place_of_%' OR
  cl_to LIKE 'Template:%' OR
  cl_to LIKE 'Singlechart_%' OR
  cl_to LIKE 'Use_British_English_%' OR
  cl_to LIKE 'Use_Australian_English_%' OR
  cl_to LIKE 'Incomplete_lists_%' OR
  cl_to LIKE 'Fair_use_%' OR
  cl_to LIKE 'Certification_Table_Entry_%' OR
  cl_to LIKE 'Webarchive_%' OR
  cl_to LIKE 'Infobox_%' OR
  cl_to LIKE '%varB_%' OR
  cl_to LIKE '%_TOC' OR
  cl_to LIKE 'Shared_IP_addresses_%' OR
  cl_to LIKE '%isambiguation%' OR
  cl_to LIKE '%on-free%' OR
  cl_to LIKE 'User_%' OR
  cl_to LIKE 'Pages_%' OR
  cl_to LIKE 'Talk_pages_%' OR
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
  cl_to LIKE '%_template_errors' OR
  cl_to LIKE 'CS1%' OR
  cl_to LIKE 'Use_dmy_%' OR
  cl_to LIKE 'Use_mdy_%' OR
  cl_to LIKE '%_no_TOC';
```

### Word Count Data
You can use the following commands to run the script locally.
But note that it will probably take months to complete!
```
curl -L "http://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.b
z2" > wiki.dump.bz2
python3 extract/main.py
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
