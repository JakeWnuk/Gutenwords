<h1 align="center">
Gutenwords
</h1>

## What is it?
**Gutenwords** is a Python tool created to scrape Project Gutenburg for unique words for cracking password hashes using the Natural Language Tool Kit (NLTK).

Last updated the results contain 6,527,202 words, 899,257 collocations, and 15 languages.

```
$ python3 gutenwords.py

LOADED 47301 SOURCES
5395536 COLLOS | 26108804 WORDS

 [1] <Response [200]> | https://www.gutenberg.org/cache/epub/1/pg1.txt
Title:  The   Bill of Rights | Language: ENGLISH
Words in source: 3152 | NEW WORDS: 0
Records in collocations table: 899256 | Records in word table: 6527201
 [2] <Response [200]> | https://www.gutenberg.org/cache/epub/2/pg2.txt
Title:  The   Bill of Rights | Language: ENGLISH
Words in source: 531 | NEW WORDS: 0
Records in collocations table: 899256 | Records in word table: 6527201
 [3] <Response [200]> | https://www.gutenberg.org/cache/epub/3/pg3.txt
Title:  Kennedy Inaugural Address | Language: ENGLISH
Words in source: 485 | NEW WORDS: 0
Records in collocations table: 899256 | Records in word table: 6527201
 [4] <Response [200]> | https://www.gutenberg.org/cache/epub/4/pg4.txt
Title:  | Language: ENGLISH
Words in source: 472 | NEW WORDS: 0
Records in collocations table: 899274 | Records in word table: 6527201
 [5] <Response [200]> | https://www.gutenberg.org/cache/epub/5/pg5.txt
Title:  THE UNITED STATES  CONSTITUTION | Language: ENGLISH
Words in source: 979 | NEW WORDS: 0
Records in collocations table: 899274 | Records in word table: 6527201
 [6] <Response [200]> | https://www.gutenberg.org/cache/epub/6/pg6.txt
Title:  | Language: ENGLISH
Words in source: 407 | NEW WORDS: 0
Records in collocations table: 899288 | Records in word table: 6527201
 [7] <Response [200]> | https://www.gutenberg.org/cache/epub/7/pg7.txt
Title:  The Mayflower Compact | Language: ENGLISH
Words in source: 509 | NEW WORDS: 0
Records in collocations table: 899288 | Records in word table: 6527201

```

## How does it work?
The script works by taking known URL patterns and enumerating them for unique books and texts from Project Gutenburg. The text is then filtered down by regex and split to be processed by NLTK. The tokens are broken up and tagged in a few different ways:

- Words greater than 36 characters are removed from the results as they are assumed to be not practical for password cracking
- Before tokenizing the text, all non-ASCII chars, punctuation, numbers, and one character words are removed
- Input text is automatically tagged for language
- Stop words are removed based on the input language
- The original word and the word's lemma are recorded (dictionary form of a word)
- The text's collocations are recorded (expressions of multiple words which commonly co-occur)
- The word's part of speech in the text is recorded
- Words and collocations are stored, and duplicate entries are not recorded

The script will create two output CSV's after 50 URLs. Words and collocations are stored in two separate tables with associated metadata. The script will reingest the output databases on further runs so progress can be saved. The script was intended to be expanded for other applications in the future. 

## What is the output?
The output is stored in the results folder. It consists of a few presorted results and the raw results from the script. The words table will be all of the unique words from Project Gutenberg, and the collocations table will be all word pair associations concatenated. The results were then mutated in a few unique ways for the application of password cracking (not provided), but it will give a good baseline for a corpus of words.

### Collocations Table Key
|INDEX|TOKEN 1|TOKEN 2|CONCAT|LANG|TITLE|URL
|---|---|---|---|---|---|---|
|Index #|Collocation1|Collocation2|Concat of both (nospaces)|Detected language|Title of Source|Source URL

### Words Table Key
|WORD|UNQ FREQ|PART OF SPEECH|LANG|LENGTH|
|---|---|---|---|---|
|Word recorded|Unique number of appearances*|Guessed Part of Speech**|Detected language|Length of word

##### *After removing duplicates from the text so multiple usages in one text count as one
##### **Somewhat inaccurate as it is guessed based on surrounding text and is only recorded once

## How can I use this for hash cracking?
This is very useful when cracking hashes as you get a large language corpus in a single location for filtering and creating wordlists. It is very effective at targeting passphrases as well because of the part of speech tagging. For example, one could take a list of all the most popular English nouns and adjectives and quickly make a combinator wordlist or take all the french words and create passphrases in a V-ADJ-N form, then utilize the collocation database to create common phrase combinations. The corpus could also be mutated with 1337sp34k or other rules that can give a jumping point for specific applications or combined with keywords taken from target metadata to create new wordlists.