"""Methods to help tokenize strings using python core libraries."""

import io
import math
import string
import logging
import tokenize
import collections

logger = logging.getLogger("tokens")

# TODO: either make this much smarter (e.g. not pluralize an already plural noun) 
# or use a 3rd-party library (e.g. nltk, pattern.en), or just skip this step altogether!
def pluralize(word: str):
    """Return plural form of given lowercase singular word (English only).

    Based on a activestate recipe: http://code.activestate.com/recipes/577781/
    """
    vowels = set('aeiou')
    abberant_plurals = {
        'appendix':   'appendices',
        'barracks':   'barracks',
        'cactus':     'cacti',
        'child':      'children',
        'criterion':  'criteria',
        'deer':       'deer',
        'echo':       'echoes',
        'elf':        'elves',
        'embargo':    'embargoes',
        'focus':      'foci',
        'fungus':     'fungi',
        'goose':      'geese',
        'hero':       'heroes',
        'hoof':       'hooves',
        'index':      'indices',
        'knife':      'knives',
        'leaf':       'leaves',
        'life':       'lives',
        'man':        'men',
        'mouse':      'mice',
        'nucleus':    'nuclei',
        'person':     'people',
        'phenomenon': 'phenomena',
        'potato':     'potatoes',
        'self':       'selves',
        'syllabus':   'syllabi',
        'tomato':     'tomatoes',
        'torpedo':    'torpedoes',
        'veto':       'vetoes',
        'woman':      'women',
        }

    if not word:
        return ''
    plural = abberant_plurals.get(word)
    if plural:
        return plural
    root = word
    try:
        if word[-1] == 'y' and word[-2] not in vowels:
            root = word[:-1]
            suffix = 'ies'
        elif word[-1] == 's':
            if word[-2] in vowels:
                if word[-3:] == 'ius':
                    root = word[:-2]
                    suffix = 'i'
                else:
                    root = word[:-1]
                    suffix = 'ses'
            else:
                suffix = 'es'
        elif word[-2:] in ('ch', 'sh'):
            suffix = 'es'
        else:
            suffix = 's'
    except IndexError:
        suffix = 's'
    plural = root + suffix
    return plural

def get_tokens(query: str):
    """Remove punctuations, convert to lowercase, and tokenize a given query"""
    query = query.translate(str.maketrans({x: None for x in string.punctuation}))
    tokens = [t.string.lower() if t.string.isalpha() else t.string \
            for t in tokenize.generate_tokens(io.StringIO(query).readline)]
    # after this step we should also remove any plurality of tokens and
    # capital characters, refer to the comment of pluralize function.
    return tokens

def word_set(docs: list[str]):
    """Get the set of all tokens for a list of documents."""
    tokenized_docs = [get_tokens(doc) for doc in docs]
    wordset = set([token for tokenized_doc in tokenized_docs for token in tokenized_doc])
    return wordset

def word_idx(wordset):
    """Get a dictionary of unique words and values as indices from zero."""
    dic = {y: x for x, y in enumerate(wordset)}
    return dic


def term_freq(doc, token):
    """Get the term-frequency (TF) in a document.

    Term-frequency is defined as the ratio of the number of occurences 
    of a term in a document to the total number of terms in that document.
    """
    tokens = get_tokens(doc)
    counts = collections.Counter(tokens)
    tf = counts[token] / len(tokens)
    return tf

def inverse_docfreq(docs, token):
    """Get the inverse document-frequency (IDF) in a list of documents.
    
    Inverse document-frequency is defined as the log of the ratio of the 
    number of documents to the number of documents containing the token.
    The words that occur rarely in a corpus have a high IDF score.
    """
    tokenized_docs = [get_tokens(doc) for doc in docs]
    count = sum(token in tokenized_doc for tokenized_doc in tokenized_docs)
    # to avoid division by zero
    if count == 0: count += 1
    idf = math.log(len(docs) / count)
    return idf

def tfidf(docs):
    wordset = word_set(docs)
    wordidx = word_idx(wordset)
    tfidf = [[0.0 for word in wordset] for doc in docs]
    for idx, doc in enumerate(docs):
        tokens = get_tokens(doc)
        tokens_set = set(tokens)
        for token in tokens_set:
            tf = term_freq(doc, token)
            idf = inverse_docfreq(docs, token)
            tfidf_token_doc = tf * idf
            tfidf[idx][wordidx[token]] = tfidf_token_doc
    return tfidf




# text = ['Topic sentences are similar to mini thesis statements. Like a thesis statement, a topic sentence has a specific main point. Whereas the thesis is the main point of the essay',
 # 'the topic sentence is the main point of the paragraph. Like the thesis statement, a topic sentence has a unifying function. But a thesis statement or topic sentence alone doesn’t guarantee unity.',
 # 'An essay is unified if all the paragraphs relate to the thesis, whereas a paragraph is unified if all the sentences relate to the topic sentence.']

# wordset = word_set(text)
# print(word_idx(wordset))
# print(tfidf(text)[0])

