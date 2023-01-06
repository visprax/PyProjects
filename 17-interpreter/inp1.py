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
    def LOAD_VALUE(self, value):
        self.stack.append(value)

    def PRINT_VALUE(self):
        value = self.stack.pop()
        print(value)

    def ADD_TWO_VALUES(self):
        value1 = self.stack.pop()
        value2 = self.stack.pop()
        total  = value1 + value2
        self.stack.append(total)

    def exec_code(self, code_object):
        # instructions are the bytecodes (e.g. LOAD_VALUE of 1),
        # code_object is the dictionary of instructions and arguments to these 
        # instructions and a list of all numbers used in the instructions.
        instructions = code_object["instructions"]
        numbers = code_object["numbers"]

        for instruction, argument in instructions:
            if instruction == "LOAD_VALUE":
                number = numbers[argument]
                self.LOAD_VALUE(number)
            elif instruction == "ADD_TWO_VALUES":
                self.ADD_TWO_VALUES()
            elif instruction == "PRINT_VALUE":
                self.PRINT_VALUE()
            else:
                print(f"{instruction} not supported!")


        




if __name__ == "__main__":
    # instructions for `4 + 5`
    code_object = {
            "instructions": [("LOAD_VALUE", 0),
                             ("LOAD_VALUE", 1),
                             ("ADD_TWO_VALUES", None),
                             ("PRINT_VALUE", None)],
            "numbers": [4, 5]
            }

    interpreter = Interpreter()
    interpreter.exec_code(code_object)

