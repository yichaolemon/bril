from mycfg import blocks_by_label, form_blocks, blocks_to_json
import json
import sys


class LVN:
    def __init__(self):
        # map from variable to value number
        self.environment = {}
        # index is the value number, items are tuples (value, canonical variable)
        self.value_table = []
        # key is value, value is value number
        self.value_to_number = {}

    def make_value(self, op, args):
        arg_numbers = tuple(self.environment[arg] for arg in args)
        return (op, arg_numbers)

    def add_instr(self, instr):
        dest = instr["dest"]
        args = instr["args"]
        op = instr["op"]
        value = self.make_value(op, args)
        if value in self.value_to_number:
            number = self.value_to_number[value]
        else:
            number = len(self.value_table)
            self.value_table.append((value, dest))
            self.value_to_number[value] = number
        self.environment[dest] = number


    def reconstruct_instr(self, instr):
        dest = instr["dest"]
        args = instr["args"]
        op = instr["op"]
        # See if we can replace the whole value.
        value = self.make_value(op, args)
        canonical = self.value_table[self.value_to_number[value]][1]
        if canonical != dest:
            instr["op"] = "id"
            instr["args"] = [canonical]
        else:
            # The first time value is defined.
            instr["args"] = [self.value_table[number][1] for number in value[1]]

def lvn_block(block):
    # compute local value numbering and modifies block in place
    lvn = LVN()

    for instr in block:
        lvn.add_instr(instr)
        lvn.reconstruct_instr(instr)


def lvn():
    prog = json.load(sys.stdin)
    for func in prog['functions']:
        block_by_label, labels = blocks_by_label(form_blocks(func['instrs']))
        for block in block_by_label.values():
            lvn_block(block)
        func["instrs"] = blocks_to_json(labels, block_by_label)
    print(json.dumps(prog))


if __name__ == '__main__':
    lvn()
