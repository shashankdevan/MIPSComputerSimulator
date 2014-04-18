class Instruction:
    def __init__(self, label, opcode, dest, operands):
        self.label = label
        self.opcode = opcode
        self.dest = dest
        self.operands = operands
        self.exec_unit = ""
        self.IF = "-"
        self.ID = "-"
        self.EX = "-"
        self.MEM = "-"
        self.WB = "-"

    def printInst(self):

        if (len(self.operands) == 2):
            printString = self.opcode + " " + self.dest + ', ' + self.operands[0] + ', ' +  self.operands[1]
        elif (len(self.operands) == 1):
            printString = self.opcode + " " + self.dest + ', ' + self.operands[0]
        elif (len(self.operands) == 0):
            printString = self.opcode + " " + self.dest

        print "%5s %-10s\t%8s\t%8s\t%8s\t%8s\t%8s" % (self.label, printString, self.IF, self.ID, self.EX, self.MEM, self.WB)
