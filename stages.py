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
            return None
        elif self.cycles == 0 and global_data.FU_STATUS['EX'] == False:
            global_data.FU_STATUS['ID'] = False
            self.instruction.ID = str(global_data.CLOCK_CYCLE)
            return Execute(self.instruction)
        else:
            return self


class Execute(Stage):
    def __init__(self, instruction):
        Stage.__init__(self, instruction)
        self.cycles = get_cycles('EX', self.instruction.opcode)

    def execute(self):
        global_data.FU_STATUS['EX'] = True
        self.cycles -= 1

    def next(self):
        if self.cycles == 0 and global_data.FU_STATUS['WB'] == False:
            global_data.FU_STATUS['EX'] = False
            self.instruction.EX = str(global_data.CLOCK_CYCLE)
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
