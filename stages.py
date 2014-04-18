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
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('ID', self.instruction.opcode)
        global_data.FU_STATUS['ID'] = True

    def execute(self):
        if self.cycles > 0:
            self.cycles -= 1

    def next(self):
        if self.instruction.opcode in ['HLT','BNE','J','BEQ']:
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
            return self


class IU(Stage):
    def __init__(self, instruction):
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('EX', self.instruction.opcode)

    def execute(self):
        global_data.FU_STATUS['IU'] = True
        self.cycles -= 1

    def next(self):
        if self.cycles == 0 and global_data.FU_STATUS['MEM'] == False:
            global_data.FU_STATUS['IU'] = False
            self.instruction.EX = str(global_data.CLOCK_CYCLE)
            return Mem(self.instruction)
        return self


class FPAdder(Stage):
    def __init__(self, instruction):
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('EX', self.instruction.opcode)

    def execute(self):
        global_data.FU_STATUS['FPAdder'] = True
        self.cycles -= 1

    def next(self):
        if self.cycles == 0 and global_data.FU_STATUS['WB'] == False:
            global_data.FU_STATUS['FPAdder'] = False
            self.instruction.EX = str(global_data.CLOCK_CYCLE)
            return WriteBack(self.instruction)
        return self


class FPMultiplier(Stage):
    def __init__(self, instruction):
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('EX', self.instruction.opcode)

    def execute(self):
        global_data.FU_STATUS['FPMultiplier'] = True
        self.cycles -= 1

    def next(self):
        if self.cycles == 0 and global_data.FU_STATUS['WB'] == False:
            global_data.FU_STATUS['FPMultiplier'] = False
            self.instruction.EX = str(global_data.CLOCK_CYCLE)
            return WriteBack(self.instruction)
        return self


class FPDivider(Stage):
    def __init__(self, instruction):
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('EX', self.instruction.opcode)

    def execute(self):
        global_data.FU_STATUS['FPDivider'] = True
        self.cycles -= 1

    def next(self):
        if self.cycles == 0 and global_data.FU_STATUS['WB'] == False:
            global_data.FU_STATUS['FPDivider'] = False
            self.instruction.EX = str(global_data.CLOCK_CYCLE)
            return WriteBack(self.instruction)
        return self


class Mem(Stage):
    def __init__(self, instruction):
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('MEM', self.instruction.opcode)

    def execute(self):
        global_data.FU_STATUS['MEM'] = True
        self.cycles -= 1

    def next(self):
        if self.cycles == 0 and global_data.FU_STATUS['WB'] == False:
            global_data.FU_STATUS['MEM'] = False
            self.instruction.MEM = str(global_data.CLOCK_CYCLE)
            return WriteBack(self.instruction)
        return self


class WriteBack(Stage):
    def __init__(self, instruction):
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('WB', self.instruction.opcode)

    def execute(self):
        global_data.FU_STATUS['IF'] = True
        self.cycles -= 1

    def next(self):
        if self.cycles == 0:
            global_data.FU_STATUS['WB'] = False
            self.instruction.WB = str(global_data.CLOCK_CYCLE)
            return None
        return self
