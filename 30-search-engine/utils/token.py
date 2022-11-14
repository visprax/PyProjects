"""Methods to help tokenize strings using python core libraries."""

import io
import string
import tokenize

docstr = "This is a test of many tests!"

docstr = docstr.translate(str.maketrans({x: None for x in string.punctuation}))

for teken in tokenize.generate_tokens(io.StringIO(docstr).readline):
    print(token.string)
