"""Methods to help tokenize strings using python core libraries."""

import io
import string
import tokenize

# TODO: either make this much smarter (e.g. not pluralize an already plural noun) 
# or use a 3rd-party library (e.g. nltk, pattern.en), or just skip this step altogether!
def pluralize(singular):
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

    if not singular:
        return ''
    plural = abberant_plurals.get(singular)
    if plural:
        return plural
    root = singular
    try:
        if singular[-1] == 'y' and singular[-2] not in vowels:
            root = singular[:-1]
            suffix = 'ies'
        elif singular[-1] == 's':
            if singular[-2] in vowels:
                if singular[-3:] == 'ius':
                    root = singular[:-2]
                    suffix = 'i'
                else:
                    root = singular[:-1]
                    suffix = 'ses'
            else:
                suffix = 'es'
        elif singular[-2:] in ('ch', 'sh'):
            suffix = 'es'
        else:
            suffix = 's'
    except IndexError:
        suffix = 's'
    plural = root + suffix
    return plural

def tokenize(query):
    query = query.translate(str.maketrans({x: None for x in string.punctuation}))
    tokens = [t.string for t in tokenize.generate_tokens(io.StringIO(query).readline)]
    # after this step we should also remove any plurality of tokens and
    # capital characters, refer to the comment of pluralize function.
    return tokens
