from functools import reduce
import sys

class Item:
    def __init__(self, value):
        self.value = value

    def is_int(self):
        return self.value.isnumeric()

    def is_bool(self):
        return self.value in ['true', 'false']

    def is_str(self):
        return chr(34) in self.value and not self.is_bool()

    def is_operator(self):
        return self.value in ['+', '-', '*', '/']

    def is_keyword(self):
        return self.value in ['print', 'dup']

    def get_value(self):
        return self.value

class Iter:
    def __init__(self, array, index=0):
        self.array = array
        self.index = index

    def next(self, increment=True):
        if increment:
            self.index += 1
            return Iter(self.array, self.index)
        else:
            index = self.index + 1
            return Iter(self.array, index)

    def collect(self):
        return Item(self.array[self.index]) if self.index < len(self.array) else None

    def get_index(self):
        return self.index

class Stack:
    def __init__(self, size=16):
        self.size = size
        self.array = [0 for _ in range(self.size)]
        self.stack_pointer = self.size - 1

    def push(self, value):
        self.array[self.stack_pointer] = value
        if self.stack_pointer != 0:
            self.stack_pointer -= 1

    def pop(self):
        if self.stack_pointer != self.size - 1:
            self.stack_pointer += 1
        value = self.array[self.stack_pointer]
        self.array[self.stack_pointer] = 0
        return value

    def duplicate(self):
        if self.stack_pointer != self.size - 1:
            self.push(self.array[self.stack_pointer+1])

    def get_stack_pointer(self):
        return self.stack_pointer

class Memory:
    def __init__(self, size=64):
        self.size = size
        self.array = [0 for _ in range(self.size)]

    def is_address_valid(self, address):
        return address <= 0 or address >= self.size

    def write(self, address, value):
        if self.is_address_valid(address):
            self.array[address] = value

    def read(self, address):
        value = None
        if self.is_address_valid(address):
            value = self.array[address]
        return value

    def get_free_address(self):
        result = None
        for address in self.array:
            if address == 0:
                result = address
        return result

def convert_item_value(item):
    result = item.get_value()
    if item.is_int():
        result = int(item.get_value())
    return result

def solve_expr(expr): # 5 5 + -> 10
    numbers = list()
    result = None
    operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y,
    }
    for item in expr:
        if item.is_int():
            numbers.append(convert_item_value(item))
        elif item.is_operator():
            result = reduce(operations[item.get_value()], numbers)
            numbers = [result]
    return result

def build_string(array, index):
    items = Iter(array, index)
    item = items.next().collect()
    string = list()
    while item.is_str():
        string.append(item.get_value())
        item = items.next().collect()
    return (string, items.get_index() - 1)

def build_expr(array, index):
    items = Iter(array, index)
    item = items.next().collect()
    expr = list()
    while item.is_int() or item.is_operator():
        expr.append(item)
        item = items.next().collect()
    return (expr, items.get_index() - 1)

def main():
    with open(sys.argv[1], 'r') as file:
        source = file.read().split()
        items = Iter(source, -1)
        item = items.next().collect()

        memory = Memory()
        stack = Stack()

        while item != None:
            next_item = Iter(source, items.get_index()).next(increment=False).collect()

            if next_item is None:
                next_item = Item(None)

            if item.is_int() and next_item.is_int() or next_item.is_operator():
                expr, index = build_expr(source, items.get_index() - 1) 
                stack.push(solve_expr(expr))
                items = Iter(source, index)
            elif item.is_int():
                stack.push(convert_item_value(item))
            elif item.is_str():
                string, index = build_string(source, items.get_index() - 1)
                stack.push(' '.join(string)[1:-1])
                items = Iter(source, index)
            elif item.is_keyword():
                if item.get_value() == 'print':
                    print(stack.pop())
                elif item.get_value() == 'dup':
                    stack.duplicate()
            item = items.next().collect()

if __name__ == '__main__':
    main()
