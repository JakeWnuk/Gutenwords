<h1 align="center">
Gutenwords
</h1>

## What is it?
**Gutenwords** is a Python tool created to scrape Project Gutenburg for unique words for cracking password hashes using the Natural Language Tool Kit (NLTK).

Last updated the results contain 6,527,202 words and 899,257 collocations.

## How does it work?
The script works by taking known URL patterns and enumerating them for unique books and texts from Project Gutenburg. The text is then filtered down by regex and split to be processed by NLTK. The tokens are broken up and tagged in a few different ways:

- Words greater than 37 characters are removed from the results as they are assumed to be not practical for password cracking
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