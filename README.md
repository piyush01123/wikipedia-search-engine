# Wikipedia Search Engine
Search Engine for Wikipedia dump (~75 GB).
*Search time <5s tested on Ubuntu 18 with 8 GB RAM and Intel i5 processor*

## How to run?
### Requirements
**Download wikipedia dump and extract.**

If the link is not working, it is because Wikipedia decided to delete it from their server.
<br>
Get latest wikipedia dump from [here](https://dumps.wikimedia.org/enwiki/).
<br>
Also create a new directory `data` to be used for posting lists.
```
wget https://dumps.wikimedia.org/enwiki/20210720/enwiki-20210720-pages-articles-multistream.xml.bz2
bzip2 -d enwiki-20210720-pages-articles-multistream.xml.bz2
mkdir -p data
```
### Indexing
**Run indexer**
```
python indexer.py https://dumps.wikimedia.org/enwiki/20210720/enwiki-20210720-pages-articles-multistream.xml
```
This will create files like `data/index0.txt`, `data/index1.txt` and so on.
Each of these are posting lists. They contain text in the form
```
[word] d[doc ID] t[freq_t] b[freq_b] i[freq_i] c[freq_c] l[freq_l] r[freq_r]
```
where each symbol represents:
```
word: English word that this posting list represents
freq_t: Frequency of word in Title section
freq_b: Frequency of word in Body section
freq_i: Frequency of word in Infobox section
freq_c: Frequency of word in Category section
freq_l: Frequency of word in External Links section
freq_r: Frequency of word in Reference section
```
The crucial thing to note is that each of these files have words in alphabetically sorted order. This fact will be useful to us during merging.

A file named `data/title.txt` will also get created. It will have data in the form
```
[doc ID] [Document Title]
```
### Merging
**Run merger**
```
python merger.py
```
This will merge the posting lists into a compact form which is faster for search. Effectively we want all data for one word at one place. So that is exactly what we we generate using this merger.

This will generate files named `data/t0.txt`, `data/t1.txt` and so on. These are the compact listings of title field. Similarly for body field we will have files like `data/b0.txt`, `data/b1.txt` and so on. Similarly we will have for other fields as well.
Each line in these files represents all occurrences of a specific word in the corresponding field.

For example for the title field files, each line will have the format:
```
[word] [doc ID A] [freq_t_A] [doc ID B] [freq_t_B] [doc ID C] [freq_t_C]
```
where each symbol represents:
```
word: English word that this posting list represents
freq_t_A: Frequency of word in title of doc ID A
freq_t_B: Frequency of word in title of doc ID B
freq_t_C: Frequency of word in title of doc ID C
```
Similarly, we will have files for other field as well.

Most importantly, each word is mentioned only once in these merged files (hence works like an index). So, given a word, we can simply look at the appropriate line to get the entire posting list for that word. This is what makes the search so fast. Also the words are sorted alphabetically, hence binary search can be used. Moreover, we created `vocab.txt` for sorted vocabulary and offset files to quickly get to the correct line number.


### Searching
```
python search.py
```
Search can be for plain query as well as field queries.
Examples of plain query:
```
Billie Jean michael jackson
Allan Rune Pettersson
4 July 1776
```

Examples of field query:
```
t:World Cup i:2018 c:Football
b:Marc Spector i:Marvel Comics c:1980 comics debuts
b:Speed of Light c:Concepts in Physics
```

#### How search results are ranked
Once we have obtained the index as mentioned above, getting the document IDs for a query is easy. However, we still need to rank the results.
For this we use [TF-IDF](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) (TF is replaced by just frequency and IDF is used as per standard definition).

For all the words combined together, TF-IDF scores are calculated and the scores are multiplied with a factor based on the field that word came from.
Weighing scheme for each field:
```
Title: 0.3
Body: 0.25
Infobox: 0.20
Category: 0.1
Reference: 0.05
External Links: 0.05
```
Finally we have scores in the form `Doc ID: score`. This dictionary is sorted based on value and top 5 Doc IDs are returned along with their titles.


### Quit Search Engine
```
exit()
```
