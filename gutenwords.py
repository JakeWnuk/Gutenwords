#!/bin/python3
# Dev by Jake Wnuk

import os
import re
import time

import nltk
import pandas as pd
import requests as rq
from langdetect import detect
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


def dep_check():
    """
    checks for nltk deps
    @return: none
    """
    try:
        test = word_tokenize('can you parse me')
    except LookupError:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        nltk.download('averaged_perceptron_tagger')


def detect_lang(string):
    """
    detects language then returns nltk term
    @param string: string of text to analyze
    @return: string
    """
    nltk_stopwords = {
        'en': 'english',
        'hu': 'hungarian',
        'sv': 'swedish',
        'kk': 'kazakh',
        'no': 'norwegian',
        'fi': 'finnish',
        'ar': 'arabic',
        'id': 'indonesian',
        'pt': 'portuguese',
        'tr': 'turkish',
        'az': 'azerbaijani',
        'sl': 'slovene',
        'es': 'spanish',
        'da': 'danish',
        'ne': 'nepali',
        'ro': 'romanian',
        'el': 'greek',
        'nl': 'dutch',
        'tg': 'tajik',
        'de': 'german',
        'ru': 'russian',
        'fr': 'french',
        'it': 'italian'
    }
    try:
        d_lang = detect(string)
        return nltk_stopwords[str(d_lang)]
    except:
        return nltk_stopwords['en']


def clean_text(input_text):
    """
    takes input text and cleans known patterns for tokenization
    @param input_text: string of input text
    @return: string
    """

    # text to delim by and index of result to take
    delim_chars = [
        [('*** START OF', 1), ('*** END OF', 0)],
        [('***START OF', 1), ('***END OF', 0)],
        [('***The Project Gutenberg Etext of', 1)],
        [('to header material.', 1)]
    ]
    re_patterns = [
        '[^\x00-\x7F]+',  # remove all non ASCII chars
        '[^\w\s]',  # remove punctuations
        '[0-9]',  # remove all numbers
        '(?:^| )\w(?:$| )'  # removes all 1 char words
    ]
    str_subs = [
        ' THE PROJECT GUTENBERG EBOOK ',
        ' THIS PROJECT GUTENBURG EBOOK ',
        ' THIS PROJECT GUTENBERG EBOOK ',
        '_'
    ]

    split_text = str(input_text)
    try:
        for delim in delim_chars:
            try:
                for i in delim:
                    broken_text = split_text.split(str(i[0]), 1)
                    split_text = broken_text[i[1]]
                break
            except IndexError:
                pass

        for rep in re_patterns:
            # replace with space to prevent weird concats
            split_text = re.sub(rep, ' ', split_text)

        for sub in str_subs:
            split_text = split_text.replace(str(sub), '')

        title = split_text.partition('\n')[0].rstrip()
        return split_text, title
    except Exception as ex:
        print(f'{colors.INFOPURP} [*] PARSE ERROR | {str(ex)} {colors.NOC}')


def get_text(url, index):
    """
    fetches text from resource
    @param url: string url
    @param index: int
    @return: string HTTP body
    """
    req_url = str(url).replace('INDEX', str(index))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) '
                      'Chrome/32.0.1667.0 Safari/537.36',
        'X-Forwarded-For': '127.0.0.1'
    }
    try:
        resp = rq.get(req_url, headers=headers)
        data = resp.text
        status = resp.status_code
        if status == rq.codes.ok:
            print(f'{colors.OKGREEN} [{str(index)}] {str(resp)}{colors.NOC} | {str(req_url)}')
            return clean_text(data)
        elif status != rq.codes.not_found:
            print(f'{colors.BADRED} [{str(index)}] {str(resp)}{colors.NOC} | {str(req_url)}')
            if status == 403:
                pass
            else:
                print(f'{colors.BADRED} [~] SLEEPING 600 SECONDS {colors.NOC}')
                time.sleep(600)
                try:
                    return clean_text(data)
                except Exception as ex:
                    print(f'{colors.INFOPURP} [*] PARSE ERROR | {str(ex)} {colors.NOC}')
    except rq.exceptions.ConnectionError:
        print(f'{colors.BADRED} [~] SLEEPING 600 SECONDS {colors.NOC}')
        time.sleep(300)


def tokenize_text(text):
    """
    takes string input and splits it into tokens using nltk
    @param text: string
    @return: list of strings
    """
    tokens = word_tokenize(text)
    tokens = [x.lower() for x in tokens]

    lang = detect_lang(text)
    stop_words = set(stopwords.words(lang))

    filtered_tokens = [word for word in tokens if word not in stop_words]
    lemma_tokens = [lemmatizer.lemmatize(word) for word in tokens if word not
                    in stop_words]

    # get collocations
    colo_tokens = nltk.Text(lemma_tokens).collocation_list()

    all_tokens = [*filtered_tokens, *lemma_tokens]
    # dedupe without caring about order
    all_tokens = list(set(all_tokens))
    return all_tokens, filtered_tokens, colo_tokens


def tag_tokens(tokens):
    """
    tags new words with expensive functions
    @param tokens: pd.DataFrame
    @return: pd.DataFrame
    """
    tokens_list = nltk.pos_tag(tokens.index.tolist())
    df = pd.DataFrame(tokens_list, columns=['WORD', 'PART OF SPEECH'])
    df['PART OF SPEECH'] = df['PART OF SPEECH'].replace(pos_trans)
    df['LANG'] = lang
    df['LENGTH'] = df['WORD'].astype(str).map(len)
    c_df = df[df['LENGTH'] >= 37].index
    df.drop(c_df, inplace=True)

    df.set_index('WORD', inplace=True)
    return df


def create_source_df(tokens, web_source, index, title, lang):
    """
    Creates a pd.df of all words in a source
    @param tokens: pd.df of all word tokens
    @param web_source: string
    @param index: int
    @param title: string
    @param lang: string
    @return: pd.df
    """
    df = pd.DataFrame(tokens[0], columns=['WORD'])
    df['TITLE'] = str(title)
    df['LANG'] = str(lang)
    df.set_index(['WORD'], inplace=True)
    df['URL'] = str(web_source).replace('INDEX', str(index))

    return df


def create_colo_df(tokens, web_source, index, title, lang):
    """
    creates pd.df of collocations from a source
    @param tokens: py.df of all words
    @param web_source: string
    @param index: int
    @param title: string
    @param lang: string
    @return: py.df
    """
    df = pd.DataFrame(tokens, columns=['TOKEN 1', 'TOKEN 2'])
    c_df = df[(df['TOKEN 1'] == 'gutenberg') | (df['TOKEN 2'] == 'gutenberg')].index
    df.drop(c_df, inplace=True)
    df['CONCAT'] = df['TOKEN 1'] + df['TOKEN 2']
    df['LANG'] = str(lang)
    df['TITLE'] = str(title[0:70]).replace('\r', '')
    df['URL'] = str(web_source).replace('INDEX', str(index))
    return df


if __name__ == '__main__':

    dep_check()


    class colors:
        OKGREEN = "\033[32m"
        BADRED = '\033[31m'
        INFOPURP = '\033[0;35m'
        NOC = '\033[0m'


    pos_trans = {
        'CC': 'conjunction',
        'CD': 'cardinal digit',
        'DT': 'determiner',
        'EX': 'existential there',
        'FW': 'foreign',
        'IN': 'conjunction',
        'JJ': 'adjective',
        'JJR': 'adjective',
        'JJS': 'adjective',
        'LS': 'list',
        'MD': 'modal',
        'NN': 'noun',
        'NNS': 'noun',
        'NNP': 'noun',
        'NNPS': 'noun',
        'PDT': 'predeterminer',
        'POS': 'possessive',
        'PRP': 'pronoun',
        'PRP$': 'pronoun',
        'RB': 'adverb',
        'RBR': 'adverb',
        'RBS': 'adverb',
        'RP': 'particle',
        'TO': 'to',
        'UH': 'interjection',
        'VB': 'verb',
        'VBD': 'verb',
        'VBG': 'verb',
        'VBN': 'verb',
        'VBP': 'verb',
        'VBZ': 'verb',
        'WDT': 'wh-determiner',
        'WP': 'wh-pronoun',
        'WP$': 'wh-pronoun',
        'WRB': 'wh-abverb'
    }

    lemmatizer = WordNetLemmatizer()

    # these appear identical after a certain point
    web_source = [
        'https://www.gutenberg.org/cache/epub/INDEX/pgINDEX.txt',
        'https://www.gutenberg.org/files/INDEX/INDEX-0.txt'
    ]

    # look in cwd for file to load
    ctd = os.path.isfile("./collocations_table.csv")
    wtd = os.path.isfile("./word_table.csv")
    if os.path.exists(wtd and ctd):
        colo_table = pd.read_csv('collocations_table.csv', index_col=0)
        token_table = pd.read_csv('word_table.csv', index_col=0)
        print(f'\n{colors.OKGREEN}LOADED {str(colo_table["URL"].unique().size)} SOURCES{colors.NOC}')
        print(f'{colors.INFOPURP}{str(colo_table.size)} COLLOS | {str(token_table.size)} WORDS{colors.NOC}\n')
    else:
        colo_table = pd.DataFrame()
        token_table = pd.DataFrame(columns=['WORD', 'UNQ FREQ'])
        token_table.set_index(['WORD'], inplace=True)

    counter = 0
    for w_source in web_source:
        for index in range(1, 70001):
            source_text = get_text(w_source, index)

            if source_text is None:
                pass
            else:
                lang = detect_lang(source_text[0])
                tokens = tokenize_text(source_text[0])

                c_tokens = create_colo_df(tokens[2], w_source, index, source_text[1], lang)
                colo_table = pd.concat([c_tokens, colo_table])
                colo_table.reset_index(inplace=True, drop=True)

                s_tokens = create_source_df(tokens, w_source, index, source_text[1], lang)

                j_tokens = token_table.merge(s_tokens, how='outer', left_on='WORD', right_on='WORD', indicator=True)
                n_tokens = j_tokens.loc[lambda x: x['_merge'] == 'right_only'].drop(
                    columns=['URL', '_merge'])
                i_tokens = j_tokens.loc[lambda x: x['_merge'] == 'both'].drop(columns=['URL', '_merge'])

                token_table.loc[token_table.index.isin(i_tokens.index.tolist()), 'UNQ FREQ'] += 1

                n_tokens = tag_tokens(n_tokens)
                token_table = pd.concat([token_table, n_tokens])
                token_table['UNQ FREQ'] = token_table['UNQ FREQ'].fillna(1)
                colo_table.drop_duplicates(subset=['TOKEN 1', 'TOKEN 2', 'CONCAT', 'LANG', 'TITLE'], inplace=True)
                counter += 1

                print(
                    f'Title: {colors.OKGREEN}{source_text[1]}{colors.NOC} | Language: {colors.OKGREEN}{str(lang).upper()}{colors.NOC}')
                print(
                    f'Words in source: {colors.INFOPURP}{len(s_tokens.index)}{colors.NOC} | NEW WORDS: {colors.OKGREEN}{len(n_tokens.index)}{colors.NOC}')
                print(
                    f'Records in collocations table: {colors.INFOPURP}{len(colo_table.index)}{colors.NOC} | Records in '
                    f'word table: {colors.OKGREEN}{len(token_table.index)}{colors.NOC}')

            if counter >= 50:
                counter = 0
                print(f'\n{colors.OKGREEN} PRINTING TABLES {colors.NOC}\n')
                colo_table.to_csv('collocations_table.csv')
                token_table.sort_values(by=['UNQ FREQ'], ascending=False).to_csv('word_table.csv')

        print(f'\n{colors.OKGREEN} PRINTING TABLES {colors.NOC}\n')
        colo_table.to_csv('collocations_table.csv')
        token_table.sort_values(by=['UNQ FREQ'], ascending=False).to_csv('word_table.csv')
