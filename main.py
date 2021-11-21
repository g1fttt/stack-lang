from functools import reduce
import sys

class Item:
    def __init__(self, value):
        self.value = value

    def is_int(self):
        return self.value.isnumeric()

    def is_bool(self):
        return self.value in ['true', 'false']

    def is_operator(self):
        return self.value in ['+', '-', '*', '/']

    def is_procedure(self):
        return self.value in ['print']

    def get_value(self):
        return self.value

class Iter:
    def __init__(self, array, index=0):
        self.array = array
        self.index = index

    def next(self):
        self.index += 1
        return Item(self.array[self.index]) if self.index < len(self.array) else None

    def get_index(self):
        return self.index

class Stack:
    def __init__(self):
        self.size = 16
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
            numbers.append(int(item.get_value()))
        elif item.is_operator():
            result = reduce(operations[item.get_value()], numbers)
            numbers = [result]
    return result

def main():
    with open(sys.argv[1], 'r') as file:
        source = file.read().split()
        items = Iter(source, -1)
        item = items.next()
        stack = Stack()

        while item != None:
            if item.is_int():
                local_items = Iter(source, items.get_index() - 1)
                local_item = local_items.next()
                expr = list()

                while local_item.is_int() or local_item.is_operator():
                    expr.append(local_item)
                    local_item = local_items.next()
               
                stack.push(solve_expr(expr))
                items = Iter(source, local_items.get_index() - 1)
            elif item.is_procedure():
                if item.get_value() == 'print':
                    print(stack.pop())
            item = items.next()

if __name__ == '__main__':
    main()
