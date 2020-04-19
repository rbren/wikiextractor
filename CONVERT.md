## Categories
```
curl -L "https://dumps.wikimedia.org/enwiki/20200401/enwiki-20200401-categorylinks.sql.gz" > catlinks.sq

sed "s/),(/)\n(/g" catlinks.sql > catlinks.tsv
rm catlinks.sql

cut -f 1,2 -d ',' catlinks.tsv | sed 's/^(//' > catlinks2.tsv
mv catlinks2.tsv catlinks.tsv

s/INSERT INTO .* VALUES (//g" catlinks.tsv > catlinks2.tsv
mv catlinks2.tsv catlinks.tsv

sed -r "s/^(.*)$/INSERT INTO categories (document, category) VALUES (\1);/g" catlinks.tsv > catlinks-cond
ensed.sql
rm catlinks2.sql

sed -r "s/,'/,E'/" catlinks-condensed.sql > catlinks-fixed.sql
rm catlinks-condensed.sql
```
NOTE: some trailing `'` get left off, causing ~1% of queries to fail
