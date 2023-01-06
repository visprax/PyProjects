#!/usr/bin/env python3
#
# A Python interpreter with Python - 500 lines or less version.
# https://www.aosabook.org/en/500L/a-python-interpreter-written-in-python.html

# TODO: replace stack list with a real stack!

# a stack machine implementation
class Interpreter:
    def __init__(self):
        self.stack = []
    
    # opcodes
    def LOAD_VALUE(self, number):
        self.stack.append(number)

    def PRINT_ANSWER(self):
        answer = self.stack.pop()
        print(answer)

    def ADD_TWO_VALUES(self):
        num1 = self.stack.pop()
        num2 = self.stack.pop()
        total = num1 + num2
        self.stack.append(total)

