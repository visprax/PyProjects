"""Methods to help tokenize strings using python core libraries."""

import io
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

def tokens(query: str):
    """Remove punctuations, convert to lowercase, and tokenize a given query"""
    query = query.translate(str.maketrans({x: None for x in string.punctuation}))
    tokens = [t.string.lower() if t.string.isalpha() else t.string \ 
            for t in tokenize.generate_tokens(io.StringIO(query).readline)]
    # after this step we should also remove any plurality of tokens and
    # capital characters, refer to the comment of pluralize function.
    return tokens

def wordset(docs: list[str]):
    """Get the set of all tokens for a list of documents."""
    tokenized_docs = [tokens(doc) for doc in docs]
    word_set = set([token for tokenized_doc in tokenized_docs for token in tokenized_doc])
    return wordset

def termfreq(doc, token):
    """Get the term-frequency (TF) in a document.

    Term-frequency is defined as the ratio of the number of occurences 
    of a term in a document to the total number of terms in that document.
    """
    tokens = tokens(doc)
    counts = collections.Counter(tokens)
    tf = counts[token] / len(tokens)
    return tf

def inverse_docfreq(docs, token):
    """Get the inverse document-frequency (IDF) in a list of documents.
    
    Inverse document-frequency is defined as the log of the ratio of the 
    number of documents to the number of documents containing the token.
    The words that occur rarely in a corpus have a high IDF score.
    """
    tokenized_docs = [tokens(doc) for doc in docs]




