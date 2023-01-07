#!/usr/bin/env python3
#
# A Python interpreter with Python - 500 lines or less version.
# https://www.aosabook.org/en/500L/a-python-interpreter-written-in-python.html

# TODO: replace stack list with a real stack!

# a stack machine implementation
class Interpreter:
    def __init__(self):
        self.stack = []
        self.environment = {}

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

    def STORE_VARIABLE(self, name):
        value = self.stack.pop()
        self.environment[name] = value

    def LOAD_VARIABLE(self, name):
        value = self.environment[name]
        self.stack.append(value)

    def parse_instruction_arg(self, instruction, argument, code_object):
        numbers = ["LOAD_VALUE"]
        variables = ["LOAD_VARIABLE", "STORE_VARIABLE"]

        if instruction in numbers:
            argval = code_object["numbers"][argument]
        elif instruction in variables:
            argval = code_object["variables"][argument]
        else:
            argval = None

        return argval

    def exec_code(self, code_object):
        # instructions are the bytecodes (e.g. LOAD_VALUE of 1),
        # code_object is the dictionary of instructions and arguments to these 
        # instructions and a list of all numbers used in the instructions.
        instructions = code_object["instructions"]

        for instruction, argument in instructions:
            argval = self.parse_instruction_arg(instruction, argument, code_object)
            if instruction == "LOAD_VALUE":
                self.LOAD_VALUE(argval)
            elif instruction == "LOAD_VARIABLE":
                self.LOAD_VARIABLE(argval)
            elif instruction == "STORE_VARIABLE":
                self.STORE_VARIABLE(argval)
            elif instruction == "ADD_TWO_VALUES":
                self.ADD_TWO_VALUES()
            elif instruction == "PRINT_VALUE":
                self.PRINT_VALUE()
            else:
                print(f"{instruction} not supported!")


if __name__ == "__main__":
    # instructions for `4 + 5`
    code_object1 = {
            "instructions": [("LOAD_VALUE", 0),
                             ("LOAD_VALUE", 1),
                             ("ADD_TWO_VALUES", None),
                             ("PRINT_VALUE", None)],
            "numbers": [4, 5]
            }

    # instruction for def f():
    #                     a = 1
    #                     b = 2
    #                     print(a + b)
    code_object2 = {
            "instructions": [("LOAD_VALUE", 0),
                             ("STORE_VARIABLE", 0),
                             ("LOAD_VALUE", 1),
                             ("STORE_VARIABLE", 1),
                             ("LOAD_VARIABLE", 0),
                             ("LOAD_VARIABLE", 1),
                             ("ADD_TWO_VALUES", None),
                             ("PRINT_VALUE", None)],
            "numbers": [1, 2],
            "variables": ['a', 'b']
            }

    interpreter = Interpreter()

    interpreter.exec_code(code_object1)
    interpreter.exec_code(code_object2)

