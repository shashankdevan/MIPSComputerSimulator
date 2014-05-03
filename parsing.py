
def parseInstruction(line):
    operands = []
    label = ""
    dest = ""
    opcode = ""

    if ':' in line:
        label = line[:line.index(':')]
        tokens = line[line.index(':') + 1:].strip().split(' ', 1)
        print "After first split tokens: ",
        print tokens
    else:
        tokens = line.strip().split(' ', 1)
    if len(tokens) > 1:
        opcode = tokens[0]
        tokens = tokens[1].split(',')
        dest = tokens[0]
        if len(tokens) > 1:
            for token in tokens[1:]:
                operands.append(token.strip())
    else:
        opcode = tokens[0]

    print "Label: (" + label + ")"
    print "Opcode: (" + opcode + ")"
    print "Dest: (" + dest + ")"
    print "Operands: (",
    print operands,
    print ")"


def main():
    parseInstruction("HLT")

main()
