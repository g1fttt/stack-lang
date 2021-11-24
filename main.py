from functools import reduce
import sys

class Item:
    def __init__(self, value):
        self.value = value

    def is_int(self):
        result = True
        if not isinstance(self.value, int):
            result = self.value.isnumeric()
        return result

    def is_bool(self):
        return self.value in ['true', 'false']

    def is_math_operator(self):
        return self.value in ['+', '-', '*', '/']

    def is_compare_operator(self):
        return self.value in ['!=', '<=', '>=', '=', '<', '>']

    def is_keyword(self):
        return self.value in ['print', 'dup', 'drop', 'swap', 'over', 'rot', 'store', 'if', 'end']

    def is_str(self):
        #return not self.is_int() and not self.is_bool() and not self.is_math_operator() and not self.is_compare_operator() and not self.is_keyword()
        return '"' in self.value

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
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y,
        }[operation], operands)

    def make_compare(self, operation):
        operands = [self.array[self.stack_pointer-1], self.array[self.stack_pointer-2]]
        return Item('true').get_value() if reduce({
            '!=': lambda x, y: x != y,
            '<=': lambda x, y: x <= y,
            '>=': lambda x, y: x >= y,
            '=': lambda x, y: x == y,
            '<': lambda x, y: x < y,
            '>': lambda x, y: x > y,
        }[operation], operands) else Item('false').get_value()

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
    while item != None and item.is_str():
        string.append(item.get_value())
        item = items.next().collect()
    return (string, items.get_index() - 1)

def build_if_block(array, index):
    items = Iter(array, index)
    item = items.next().collect()
    if_block = list()
    while item != None and item.get_value() != 'end':
        if_block.append(item.get_value())
        item = items.next().collect()
    return (if_block, items.get_index() - 1)

STACK = Stack()
VARIABLES = {}

def parse_code(source):
    items = Iter(source, -1)
    item = items.next().collect()

    while item != None:
        next_item = Iter(source, items.get_index()).next(increment=False).collect()

        if next_item is None:
            next_item = Item('')
         
        if item.is_int() or item.is_bool():
            STACK.push(item.get_value())
        elif item.is_str():
            string, index = build_string(source, items.get_index() - 1)
            STACK.push(' '.join(string)[1:-1])
            items = Iter(source, index)
        elif item.is_math_operator():
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
                if_block, index = build_if_block(source, items.get_index())
                if STACK.pop() == 'true':
                    parse_code(if_block)
                items = Iter(source, index)
        else:
            if next_item.get_value() == 'store':
                VARIABLES[item.get_value()] = STACK.pop()
            else:
                STACK.push(VARIABLES[item.get_value()])

        item = items.next().collect()

if __name__ == '__main__':
    file = open(sys.argv[1], 'r')
    source = file.read().split()
    file.close()

    parse_code(source)
