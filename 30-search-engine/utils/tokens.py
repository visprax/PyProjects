"""Methods to help tokenize strings using python core libraries."""

import io
import math
import string
import logging
import tokenize
import collections

logger = logging.getLogger("tokens")

def get_tokens(query: str):
    """Remove punctuations, convert to lowercase, and tokenize a given query"""
    query = query.translate(str.maketrans({x: None for x in string.punctuation}))
    tokens = [t.string.lower() if t.string.isalpha() else t.string \
            for t in tokenize.generate_tokens(io.StringIO(query).readline)]
    # after this step we should also remove any plurality of tokens.
    return tokens

def word_set(docs: list[str]):
    """Get all the unqiue tokens for a list of documents and set an index from zero."""
    tokenized_docs = [get_tokens(doc) for doc in docs]
    # we use this method as opposed to set() to get unique tokens so that the list is ordered.
    wordset = dict.fromkeys([token for tokenized_doc in tokenized_docs for token in tokenized_doc])
    wordset = {y: x for x, y in enumerate(wordset)}
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

def tf_idf(docs):
    wordset = word_set(docs)
    tfidf = [[0.0 for word in wordset] for doc in docs]
    for idx, doc in enumerate(docs):
        tokens = get_tokens(doc)
        tokens_set = set(tokens)
        for token in tokens_set:
            tf = term_freq(doc, token)
            idf = inverse_docfreq(docs, token)
            tfidf_token_doc = tf * idf
            tfidf[idx][wordset[token]] = tfidf_token_doc
    return tfidf




text = ['Topic sentences are similar to mini thesis statements. Like a thesis statement, a topic sentence has a specific main point. Whereas the thesis is the main point of the essay',
 'the topic sentence is the main point of the paragraph. Like the thesis statement, a topic sentence has a unifying function. But a thesis statement or topic sentence alone doesn’t guarantee unity.',
 'An essay is unified if all the paragraphs relate to the thesis, whereas a paragraph is unified if all the sentences relate to the topic sentence.']

wordset = word_set(text)
print(word_idx(wordset))
print(tf_idf(text)[0])

