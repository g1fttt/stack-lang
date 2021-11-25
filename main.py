from functools import reduce
import sys

class Item:
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
        return self.value in ['print', 'size', 'dup', 'drop', 'swap', 'over', 'rot', 'store', 'if', 'while', 'proc', 'endproc', 'call', 'endif', 'back', 'glob']

    def is_str(self):
        result = False
        for i in range(97, 123): # a-z
            if chr(i) in self.value:
                result = True
        for i in range(65, 91): # A-Z
            if chr(i) in self.value:
                result = True
        return result

    def get_value(self):
        value = self.value
        if self.is_int():
            value = int(value)
        return value

class Iter:
    def __init__(self, array, index=0):
        self.array = array
        self.index = index

    def next(self, increment=True):
        result = None
        if increment:
            self.index += 1
            result = Iter(self.array, self.index)
        else:
            index = self.index + 1
            result = Iter(self.array, index)
        return result

    def collect(self):
        return Item(self.array[self.index]) if self.index < len(self.array) else None

    def get_index(self):
        return self.index

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

def build_string(array, index):
    items = Iter(array, index)
    item = items.next().collect()
    string = list()
    while item != None and not item.is_keyword() and not item.is_int() and not item.is_bool():
        string.append(item.get_value())
        item = items.next().collect()
    return (string, items.get_index() - 1)

def build_statement_block(array, index, end_name):
    items = Iter(array, index)
    item = items.next().collect()
    statement_block = list()
    while item != None and item.get_value() != end_name:
        statement_block.append(item.get_value())
        item = items.next().collect()
    return (statement_block, items.get_index() - 1)

STACK = Stack()
VARIABLES = {}
PROCEDURES = {}

def parse_code(source):
    items = Iter(source, -1)
    item = items.next().collect()
    use_global_variables = True
    return_index = 0
    variables = {}

    while item != None:
        next_item = Iter(source, items.get_index()).next(increment=False).collect()

        if next_item is None:
            next_item = Item('')
         
        if item.is_int() or item.is_bool():
            STACK.push(item.get_value())
        elif item.is_str() and not item.is_keyword():
            string, index = build_string(source, items.get_index() - 1)
            STACK.push(' '.join(string)[1:-1])
            items = Iter(source, index)
        elif item.is_math_operator() or item.is_bitwise_operator():
            result = STACK.make_operation(item.get_value())
            STACK.clear()
            STACK.push(result)
        elif item.is_compare_operator():
            result = STACK.make_compare(item.get_value())
            STACK.push(result)
        elif item.is_keyword():
            if item.get_value() == 'print':
                if not STACK.is_empty():
                    print(STACK.pop())
            elif item.get_value() == 'size':
                STACK.push(STACK.get_size())
            elif item.get_value() == 'dup':
                STACK.duplicate()
            elif item.get_value() == 'swap':
                STACK.swap()
            elif item.get_value() == 'drop':
                STACK.pop()
            elif item.get_value() == 'over':
                STACK.over()
            elif item.get_value() == 'rot':
                STACK.rotate()
            elif item.get_value() == 'if':
                statement_block, index = build_statement_block(source, items.get_index(), 'endif')
                if STACK.pop() == 'true':
                    parse_code(statement_block)
                items = Iter(source, index)
            elif item.get_value() == 'while':
                statement_block, index = build_statement_block(source, items.get_index(), 'endif')
                while STACK.pop() == 'true':
                    parse_code(statement_block)
                items = Iter(source, index)
            elif item.get_value() == 'proc':
                statement_block, index = build_statement_block(source, items.get_index() + 1, 'endproc') # +1 cuz skipping procedure name
                PROCEDURES[next_item.get_value()] = statement_block
                items = Iter(source, index)
            elif item.get_value() == 'back':
                items = Iter(source, return_index)
            elif item.get_value() == 'glob':
                use_global_variables = not use_global_variables
        else:
            if next_item.get_value() == 'store':
                if use_global_variables:
                    VARIABLES[item.get_value()] = STACK.pop()
                else:
                    variables[item.get_value()] = STACK.pop()
            elif next_item.get_value() == 'call':
                parse_code(PROCEDURES[item.get_value()])
                return_index = items.get_index()
            else:
                if use_global_variables:
                    if item.get_value() in VARIABLES:
                        STACK.push(VARIABLES[item.get_value()])
                else:
                    if item.get_value() in variables:
                        STACK.push(variables[item.get_value()])
        
        item = items.next().collect()

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as file:
        source = file.read().split()
    parse_code(source)
