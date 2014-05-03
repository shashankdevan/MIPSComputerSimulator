import global_data

class Instruction:
    def __init__(self, label, opcode, dest, operands):
        self.index = 0
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
        self.Struct = '-'
        self.WAW = '-'
        self.RAW = '-'
        self.WAR = '-'
        self.offset = 0
        self.FLUSH_FLAG = False
        self.MISSED_ICACHE = False
        self.MISSED_DCACHE = False
        self.COMBINATION = -1

    def processOperand(self):
        if '(' in self.operands[0]:
            self.offset = int(self.operands[0][:int(self.operands[0].index('('))])
            self.operands[0] = self.operands[0][int(self.operands[0].index('(')) + 1: int(self.operands[0].index(')'))]

    def regAvailable(self):
        if self.opcode in ['LW', 'L.D']:
            # self.processOperand()
            dest_blocked = global_data.RG_STATUS[self.dest]
            source_blocked = global_data.RG_STATUS[self.operands[0]]
            if dest_blocked:
                self.WAW = 'Y'
            if source_blocked:
                self.RAW = 'Y'
            return not(dest_blocked) and not(source_blocked)
        elif self.opcode in ['SW', 'S.D']:
            self.processOperand()
            dest_blocked = global_data.RG_STATUS[self.operands[0]]
            source_blocked = global_data.RG_STATUS[self.dest]
            if source_blocked:
                self.RAW = 'Y'
            return not(source_blocked)
        elif self.opcode in ['BEQ', 'BNE']:
            dest_blocked = global_data.RG_STATUS[self.dest]
            # print self.operands
            source_blocked = global_data.RG_STATUS[self.operands[0]]
            if dest_blocked or source_blocked:
                self.RAW = 'Y'
            return not(dest_blocked) and not(source_blocked)
        elif self.opcode in ['HLT', 'J']:
            return True
        else:
            dest_blocked = global_data.RG_STATUS[self.dest]
            source_blocked = global_data.RG_STATUS[self.operands[0]] or global_data.RG_STATUS[self.operands[1]]
            if dest_blocked:
                self.WAW = 'Y'
            if source_blocked:
                self.RAW = 'Y'
            return not(dest_blocked) and not(source_blocked)

    def lockRegisters(self):
        if self.opcode in ['LW', 'L.D']:
            global_data.RG_STATUS[self.dest] = True
        elif self.opcode in ['DADD', 'DADDI','DSUB','DSUBI','AND','ANDI','OR','ORI', 'ADD.D', 'SUB.D', 'MULT.D', 'MUL.D', 'DIV.D']:
            global_data.RG_STATUS[self.dest] = True

    def releaseRegisters(self):
        if self.opcode in ['LW', 'L.D']:
            global_data.RG_STATUS[self.dest] = False
        elif self.opcode in ['DADD', 'DADDI','DSUB','DSUBI','AND','ANDI','OR','ORI', 'ADD.D', 'SUB.D', 'MULT.D', 'MUL.D', 'DIV.D']:
            global_data.RG_STATUS[self.dest] = False

    def printInst(self):

        if (len(self.operands) == 2):
            printString = self.opcode + " " + self.dest + ', ' + self.operands[0] + ', ' +  self.operands[1]
        elif (len(self.operands) == 1):
            printString = self.opcode + " " + self.dest + ', ' + self.operands[0]
        elif (len(self.operands) == 0):
            printString = self.opcode + " " + self.dest

        print "%5s %-10s\t%5s\t%5s\t%5s\t%5s\t%5s\t%5s\t%5s\t%5s" % (self.label, printString, self.IF, self.ID, self.EX, self.WB, self.RAW, self.WAR, self.WAW, self.Struct)
