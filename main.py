from functools import reduce
import sys

class Word:
    def __init__(self, value):
        self.value = value

    def is_int(self):
        result = True
        if not isinstance(self.value, int):
            result = self.value.replace('-', '').isnumeric()
        return result

    def is_bool(self):
        return self.value in ['true', 'false']

    def is_math_operator(self):
        return self.value in ['+', '-', '*', '/']

    def is_bitwise_operator(self):
        return self.value in ['|', '&', '^', '<<', '>>']

    def is_compare_operator(self):
        return self.value in ['!=', '<=', '>=', '=', '<', '>']

    def is_keyword(self):
        return self.value in ['stdout', 'size', 'dup', 'drop', 'swap', 'over', 'rot', 'if', 'while', 'proc', 'in', 'end']

    def compile(self, char):
        if self.value.startswith(char):
            return Word(self.value[1:])

    def get_value(self):
        value = self.value
        if self.is_int():
            value = int(value)
        return value

class Stack:
    def __init__(self, size=16):
        self.size = size
        self.array = [0 for _ in range(self.size)]
        self.stack_pointer = 0

    def push(self, value):
        self.array[self.stack_pointer] = value
        if self.stack_pointer != self.size - 1:
            self.stack_pointer += 1

    def pop(self):
        if self.stack_pointer != 0:
            self.stack_pointer -= 1
        value = self.array[self.stack_pointer]
        self.array[self.stack_pointer] = 0
        return value

    def duplicate(self):
        if self.get_size() >= 1:
            self.push(self.array[self.stack_pointer-1])

    def swap(self):
        if self.get_size() >= 2:
            temp = self.array[self.stack_pointer-1]
            self.array[self.stack_pointer-1] = self.array[self.stack_pointer-2]
            self.array[self.stack_pointer-2] = temp

    def over(self):
        if self.get_size() >= 2:
            self.push(self.array[self.stack_pointer-2])

    def rotate(self):
        if self.get_size() >= 3:
            temp = self.array[self.stack_pointer-1]
            self.array[self.stack_pointer-1] = self.array[self.stack_pointer-3]
            self.array[self.stack_pointer-3] = temp

    def clear(self):
        self.array = [0 for _ in range(self.size)]
        self.stack_pointer = 0

    def make_operation(self, operation):
        operands = list(filter(lambda x: isinstance(x, int) and x != 0, self.array))
        return reduce({
            '+':  lambda x, y: x + y,
            '-':  lambda x, y: x - y,
            '*':  lambda x, y: x * y,
            '/':  lambda x, y: x / y,
            '|':  lambda x, y: x | y,
            '&':  lambda x, y: x & y,
            '^':  lambda x, y: x ^ y,
            '<<': lambda x, y: x << y,
            '>>': lambda x, y: x >> y,
        }[operation], operands)

    def make_compare(self, operation):
        operands = [self.array[self.stack_pointer-1], self.array[self.stack_pointer-2]]
        return 'true' if reduce({
            '!=': lambda x, y: x != y,
            '<=': lambda x, y: x <= y,
            '>=': lambda x, y: x >= y,
            '=':  lambda x, y: x == y,
            '<':  lambda x, y: x < y,
            '>':  lambda x, y: x > y,
        }[operation], operands) else 'false'

    def get_size(self):
        return len(list(filter(lambda x: x != 0, self.array)))

    def is_empty(self):
        return self.get_size() == 0

    def debug(self):
        print(self.array, self.stack_pointer)

def build_statement(source, index):
    need_close = []
    statement = []
    while index != len(source):
        word = Word(source[index])
        if word.is_keyword():
            if word.get_value() == 'in':
                need_close.append(True)
            elif word.get_value() == 'end':
                if len(need_close) > 0:
                    need_close.pop()
                if len(need_close) == 0:
                    break
        statement.append(word.get_value())
        index += 1
    return statement[1:], index

STACK = Stack()
VARIABLES = {}
PROCEDURES = {}

def parse_code(source):
    variables = {}
    index = 0

    while index != len(source):
        previous_word = Word(source[index-1 if index != 0 else 0])
        word = Word(source[index])

        if word.is_int() or word.is_bool():
            STACK.push(word.get_value())
        elif word.is_math_operator() or word.is_bitwise_operator():
            result = STACK.make_operation(word.get_value())
            STACK.clear()
            STACK.push(result)
        elif word.is_compare_operator():
            result = STACK.make_compare(word.get_value())
            STACK.push(result)
        elif word.is_keyword():
            if word.get_value() == 'stdout':
                if not STACK.is_empty():
                    print(STACK.pop())
            elif word.get_value() == 'size':
                STACK.push(STACK.get_size())
            elif word.get_value() == 'dup':
                STACK.duplicate()
            elif word.get_value() == 'swap':
                STACK.swap()
            elif word.get_value() == 'drop':
                STACK.pop()
            elif word.get_value() == 'over':
                STACK.over()
            elif word.get_value() == 'rot':
                STACK.rotate()
            elif word.get_value() == 'proc':
                procedure, index = build_statement(source, index + 1) # skip 'in' keyword
                PROCEDURES[previous_word.get_value()] = procedure
            elif word.get_value() == 'if':
                statement, index = build_statement(source, index + 1)
                if STACK.pop() == 'true':
                    parse_code(statement)
            elif word.get_value() == 'while':
                statement, index = build_statement(source, index + 1)
                while STACK.pop() == 'true':
                    parse_code(statement)
        elif word.get_value().startswith('*'): # procedure call
            procedure = word.compile('*').get_value()
            if procedure in PROCEDURES:
                parse_code(PROCEDURES[procedure])
        elif word.get_value().startswith('@'): # variable store
            variable = word.compile('@').get_value()
            VARIABLES[variable] = STACK.pop()
        elif word.get_value() in VARIABLES:
            STACK.push(VARIABLES[word.get_value()])
       
        index += 1

if __name__ == '__main__':
    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as file:
            source = file.read().split()
        parse_code(source)
    else:
        source = input('-> ')
        parse_code(source)
