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
        return '"' in self.value and not self.is_bool()

    def is_operator(self):
        return self.value in ['+', '-', '*', '/']

    def is_keyword(self):
        return self.value in ['print', 'dup', 'drop', 'swap', 'over', 'rot', 'store']

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
        self.push(self.array[self.stack_pointer-1])

    def swap(self):
        temp = self.array[self.stack_pointer-1]
        self.array[self.stack_pointer-1] = self.array[self.stack_pointer-2]
        self.array[self.stack_pointer-2] = temp

    def over(self):
        self.push(self.array[self.stack_pointer-2])

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

    def is_empty(self):
        return len(list(filter(lambda x: x == 0, self.array))) == self.size

    def debug(self):
        print(self.array, self.stack_pointer)

def build_string(array, index):
    items = Iter(array, index)
    item = items.next().collect()
    string = list()
    while item != None and not item.is_int() and not item.is_bool() and not item.is_keyword():
        string.append(item.get_value())
        item = items.next().collect()
    return (string, items.get_index() - 1)

def main():
    with open(sys.argv[1], 'r') as file:
        source = file.read().split()
        items = Iter(source, -1)
        item = items.next().collect()

        stack = Stack()
        variables = {}

        while item != None:
            next_item = Iter(source, items.get_index()).next(increment=False).collect()

            if next_item is None:
                next_item = Item('')

            if item.is_int() or item.is_bool():
                stack.push(item.get_value())
            elif item.is_str():
                string, index = build_string(source, items.get_index() - 1)
                stack.push(' '.join(string)[1:-1])
                items = Iter(source, index)
            elif item.is_operator():
                result = stack.make_operation(item.get_value())
                stack.clear()
                stack.push(result)
            elif item.is_keyword():
                if item.get_value() == 'print':
                    if not stack.is_empty():
                        print(stack.pop())
                elif item.get_value() == 'dup':
                    stack.duplicate()
                elif item.get_value() == 'swap':
                    stack.swap()
                elif item.get_value() == 'drop':
                    stack.pop()
                elif item.get_value() == 'over':
                    stack.over()
            else:
                if next_item.get_value() == 'store' or next_item.get_value() == '!':
                    variables[item.get_value()] = stack.pop()
                else:
                    stack.push(variables[item.get_value()])

            item = items.next().collect()

if __name__ == '__main__':
    main()
