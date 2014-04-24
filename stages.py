from abc import abstractmethod
from simulator import *
import time

class Stage:
    def __init__(self, instruction):
        self.instruction = instruction
        self.cycles = 0

    @abstractmethod
    def execute(self): pass

    @abstractmethod
    def next(self): pass

class Fetch(Stage):
    def __init__(self, instruction):
        self.name = 'IF'
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('IF', self.instruction.opcode)
        global_data.FU_STATUS['IF'] = True

    def execute(self):
        if self.cycles > 0:
            self.cycles -= 1

    def next(self):
        if self.cycles == 0 and global_data.FU_STATUS['ID'] == False:
            global_data.FU_STATUS['IF'] = False
            self.instruction.IF = str(global_data.CLOCK_CYCLE)
            return Decode(self.instruction)
        else:
            return self

class Decode(Stage):
    def __init__(self, instruction):
        self.name = 'ID'
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('ID', self.instruction.opcode)

    def execute(self):
        global_data.FU_STATUS['ID'] = True
        if (self.instruction.regAvailable()):
            if self.cycles > 0:
                self.cycles -= 1

    def next(self):
        if self.instruction.opcode in ['HLT','BNE','J','BEQ'] and self.cycles == 0:
            global_data.FU_STATUS['ID'] = False
            self.instruction.ID = str(global_data.CLOCK_CYCLE)
            return None
        elif self.cycles == 0 and global_data.FU_STATUS[self.instruction.exec_unit] == False:
            global_data.FU_STATUS['ID'] = False
            self.instruction.ID = str(global_data.CLOCK_CYCLE)

            if self.instruction.exec_unit == 'IU':
                return IU(self.instruction)
            elif self.instruction.exec_unit == 'FPAdder':
                return FPAdder(self.instruction)
            elif self.instruction.exec_unit == 'FPMultiplier':
                return FPMultiplier(self.instruction)
            else:
                return FPDivider(self.instruction)
        else:
            if self.cycles == 0:
                self.instruction.Struct = 'Y'
                return self
            return self


class IU(Stage):
    def __init__(self, instruction):
        self.name = 'EX'
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('EX', self.instruction.opcode)

    def execute(self):
        global_data.FU_STATUS['IU'] = True
        self.instruction.lockRegisters()
        if self.cycles > 0:
            self.cycles -= 1

    def next(self):
        if self.cycles == 0 and global_data.FU_STATUS['MEM'] == False:
            global_data.FU_STATUS['IU'] = False
            self.instruction.EX = str(global_data.CLOCK_CYCLE)
            return Mem(self.instruction)
        else:
            if self.cycles == 0:
                self.instruction.Struct = 'Y'
        return self


class FPAdder(Stage):
    def __init__(self, instruction):
        self.name = 'EX'
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('EX', self.instruction.opcode)

    def execute(self):
        if global_data.FU_PIPELINED['FPAdder'] == 'no':
            global_data.FU_STATUS['FPAdder'] = True

        self.instruction.lockRegisters()
        if self.cycles > 0:
            self.cycles -= 1

    def next(self):
        if self.cycles == 0 and global_data.FU_STATUS['WB'] == False:
            global_data.FU_STATUS['FPAdder'] = False
            self.instruction.EX = str(global_data.CLOCK_CYCLE)
            return WriteBack(self.instruction)
        else:
            if self.cycles == 0:
                self.instruction.Struct = 'Y'
        return self


class FPMultiplier(Stage):
    def __init__(self, instruction):
        self.name = 'EX'
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('EX', self.instruction.opcode)

    def execute(self):
        if global_data.FU_PIPELINED['FPMultiplier'] == 'no':
            global_data.FU_STATUS['FPMultiplier'] = True
        self.instruction.lockRegisters()
        if self.cycles > 0:
            self.cycles -= 1

    def next(self):
        if self.cycles == 0 and global_data.FU_STATUS['WB'] == False:
            global_data.FU_STATUS['FPMultiplier'] = False
            self.instruction.EX = str(global_data.CLOCK_CYCLE)
            return WriteBack(self.instruction)
        else:
            if self.cycles == 0:
                self.instruction.Struct = 'Y'
        return self


class FPDivider(Stage):
    def __init__(self, instruction):
        self.name = 'EX'
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('EX', self.instruction.opcode)

    def execute(self):
        if global_data.FU_PIPELINED['FPDivider'] == 'no':
            global_data.FU_STATUS['FPDivider'] = True
        self.instruction.lockRegisters()
        if self.cycles > 0:
            self.cycles -= 1

    def next(self):
        if self.cycles == 0 and global_data.FU_STATUS['WB'] == False:
            global_data.FU_STATUS['FPDivider'] = False
            self.instruction.EX = str(global_data.CLOCK_CYCLE)
            return WriteBack(self.instruction)
        else:
            if self.cycles == 0:
                self.instruction.Struct = 'Y'
        return self


class Mem(Stage):
    def __init__(self, instruction):
        self.name = 'EX'
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('MEM', self.instruction.opcode)

    def execute(self):
        global_data.FU_STATUS['MEM'] = True
        if self.cycles > 0:
            self.cycles -= 1

    def next(self):
        if self.cycles == 0 and global_data.FU_STATUS['WB'] == False:
            global_data.FU_STATUS['MEM'] = False
            self.instruction.EX = str(global_data.CLOCK_CYCLE) #Note here, instruction.EX is updated
            return WriteBack(self.instruction)
        else:
            if self.cycles == 0:
                self.instruction.Struct = 'Y'
        return self


class WriteBack(Stage):
    def __init__(self, instruction):
        self.name = 'WB'
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('WB', self.instruction.opcode)

    def execute(self):
        global_data.FU_STATUS['WB'] = True
        self.instruction.releaseRegisters()
        if self.cycles > 0:
            self.cycles -= 1

    def next(self):
        if self.cycles == 0:
            global_data.FU_STATUS['WB'] = False
            self.instruction.WB = str(global_data.CLOCK_CYCLE)
        return None
        return self
