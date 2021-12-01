from functools import reduce
import sys
import re

class Int:
    def __init__(self, value):
        self.value = int(value)

    def get_value(self):
        return self.value

class Bool:
    def __init__(self, value):
        if type(value) == bool:
            self.value = 'true' if value else 'false'
        else:
            self.value = value

    def is_true(self):
        return self.value == 'true'

    def get_value(self):
        return self.value

class Stack: # TODO: alloc mechanism
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
        if self.get_size().get_value() >= 1:
            self.push(self.array[self.stack_pointer-1])

    def swap(self):
        if self.get_size().get_value() >= 2:
            temp = self.array[self.stack_pointer-1]
            self.array[self.stack_pointer-1] = self.array[self.stack_pointer-2]
            self.array[self.stack_pointer-2] = temp

    def over(self):
        if self.get_size().get_value() >= 2:
            self.push(self.array[self.stack_pointer-2])

    def rotate(self):
        if self.get_size().get_value() >= 3:
            temp = self.array[self.stack_pointer-1]
            self.array[self.stack_pointer-1] = self.array[self.stack_pointer-3]
            self.array[self.stack_pointer-3] = temp

    def clear(self):
        self.array = [0 for _ in range(self.size)]
        self.stack_pointer = 0

    def debug(self):
        stack = []
        for var in self.array:
            if type(var) == Int or type(var) == Bool:
                stack.append(var.get_value())
            else:
                stack.append(0)
        print(stack, self.stack_pointer)

    def make_operation(self, operation):
        ints = filter(lambda x: isinstance(x, Int), self.array)
        operands = list(map(lambda x: x.get_value(), list(ints)))
        return Int(reduce({
            '+':  lambda x, y: x + y,
            '-':  lambda x, y: x - y,
            '*':  lambda x, y: x * y,
            '/':  lambda x, y: x / y,
            '|':  lambda x, y: x | y,
            '&':  lambda x, y: x & y,
            '^':  lambda x, y: x ^ y,
            '<<': lambda x, y: x << y,
            '>>': lambda x, y: x >> y,
        }[operation], operands))

    def make_compare(self, operation):
        a = self.pop().get_value()
        b = self.pop().get_value() 
        return Bool(reduce({
            '=':  lambda x, y: x == y,
            '<':  lambda x, y: x < y,
            '>':  lambda x, y: x > y,
            '!=': lambda x, y: x != y,
            '<=': lambda x, y: x <= y,
            '>=': lambda x, y: x >= y,
        }[operation], [b, a]))

    def get_size(self):
        return Int(len(list(filter(lambda x: x != 0, self.array))))

BITWISE_OPERATOR = 'BITWISE_OPERATOR'
COMPARE_OPERATOR = 'COMPARE_OPERATOR'
MATH_OPERATOR = 'MATH_OPERATOR'
SPECIAL_ID = 'SPECIAL_ID'
RESERVED = 'RESERVED'
BOOL = 'BOOL'
INT = 'INT'
ID = 'ID'

TOKEN_EXPRS = [
    (r'[ \n\t]+', None),
    (r'//[^\n]*', None),

    (r'-*[0-9]+', INT),

    (r'!=', COMPARE_OPERATOR),
    (r'<=', COMPARE_OPERATOR),
    (r'>=', COMPARE_OPERATOR),
    (r'=', COMPARE_OPERATOR),
    (r'<', COMPARE_OPERATOR),
    (r'>', COMPARE_OPERATOR),

    (r'\+', MATH_OPERATOR),
    (r'-', MATH_OPERATOR),
    (r'\*', MATH_OPERATOR),
    (r'/', MATH_OPERATOR),

    (r'\|', BITWISE_OPERATOR),
    (r'&', BITWISE_OPERATOR),
    (r'\^', BITWISE_OPERATOR),
    (r'<<', BITWISE_OPERATOR),
    (r'>>', BITWISE_OPERATOR),

    (r'stdout', RESERVED),
    (r'size', RESERVED),
    (r'dup', RESERVED),
    (r'drop', RESERVED),
    (r'swap', RESERVED),
    (r'over', RESERVED),
    (r'rot', RESERVED),

    (r'proc', RESERVED),
    (r'while', RESERVED),
    (r'if', RESERVED),
    (r'begin', RESERVED),
    (r'end', RESERVED),

    (r'true', BOOL),
    (r'false', BOOL),

    (r'[A-Za-z][A-Za-z0-9_]*', ID),
    (r'[\!\?][A-Za-z][A-Za-z0-9_]*', SPECIAL_ID),
]

def lex(source, token_exprs):
    index = 0
    tokens = []
    while index < len(source):
        match = None
        for token_expr in token_exprs:
            pattern, tag = token_expr
            regex = re.compile(pattern)
            match = regex.match(source, index)
            if match:
                text = match.group(0)
                if tag:
                    token = (text, tag)
                    tokens.append(token)
                break
        assert match
        index = match.end(0)
    return tokens

def build_statement(lexed_source, start_index):
    starts = 1
    lexed_statement = []
    while start_index != len(lexed_source) and starts != 0:
        item, tag = lexed_source[start_index]
        if tag == RESERVED:
            if item in 'begin':
                starts += 1
            elif item == 'end':
                starts -= 1
                if starts == 0:
                    break
        lexed_statement.append((item, tag))
        start_index += 1
    assert lexed_statement != []
    return lexed_statement, start_index

STACK = Stack()
VARIABLES = {}
PROCEDURES = {}

def parse_code(source):
    last_id = ''
    index = 0

    while index != len(source):
        item, tag = source[index]

        if tag == INT:
            STACK.push(Int(item))
        elif tag == BOOL:
            STACK.push(Bool(item))
        elif tag == MATH_OPERATOR or tag == BITWISE_OPERATOR:
            result = STACK.make_operation(item)
            STACK.clear()
            STACK.push(result)
        elif tag == COMPARE_OPERATOR:
            result = STACK.make_compare(item)
            STACK.push(result)
        elif tag == SPECIAL_ID:
            special_symbol = item[0]
            variable_name = item[1:]
            if special_symbol == '!':
                VARIABLES[variable_name] = STACK.pop()
            elif special_symbol == '?':
                del VARIABLES[variable_name]
        elif tag == RESERVED:
            if item == 'stdout' and not STACK.get_size().get_value() == 0:
                number = STACK.pop()
                print(number.get_value())
            elif item == 'size':
                STACK.push(STACK.get_size())
            elif item == 'dup':
                STACK.duplicate()
            elif item == 'swap':
                STACK.swap()
            elif item == 'drop':
                STACK.pop()
            elif item == 'over':
                STACK.over()
            elif item == 'rot':
                STACK.rotate()
            elif item == 'if':
                value = STACK.pop()
                statement, index = build_statement(source, index + 2) # +2 cuz skipping <item begin>
                if value.is_true():
                    parse_code(statement)
            elif item == 'while':
                value = STACK.pop()
                statement, index = build_statement(source, index + 2)
                while value.is_true():
                    parse_code(statement)
                    value = STACK.pop()
            elif item == 'proc':
                assert last_id
                statement, index = build_statement(source, index + 2)
                PROCEDURES[last_id] = statement
        elif tag == ID:
            if item in VARIABLES:
                STACK.push(VARIABLES[item])
            elif item in PROCEDURES:
                parse_code(PROCEDURES[item])
            last_id = item

        index += 1

if __name__ == '__main__':
    assert len(sys.argv) == 2 
    with open(sys.argv[1], 'r') as file:
        source = lex(file.read(), TOKEN_EXPRS)
        parse_code(source)
