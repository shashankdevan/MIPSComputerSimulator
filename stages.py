from abc import abstractmethod
import simulator
import time
import global_data

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
        self.cycles = simulator.get_cycles('IF', self.instruction)
        global_data.FU_STATUS['IF'] = True

    def execute(self):
        if self.instruction.MISSED_ICACHE:
            # print self.instruction.opcode + " wants memory bus in cycle: " + str(global_data.CLOCK_CYCLE) + " but DCACHE_USING_BUS " + str(global_data.DCACHE_USING_BUS)
            if not global_data.DCACHE_USING_BUS:
                global_data.ICACHE_USING_BUS = True
                if self.cycles > 0:
                    self.cycles -= 1

        elif self.cycles > 0:
            self.cycles -= 1

    def next(self):
        if self.cycles == 0 and global_data.FU_STATUS['ID'] == False:
            global_data.FU_STATUS['IF'] = False
            global_data.ICACHE_USING_BUS = False
            self.instruction.IF = str(global_data.CLOCK_CYCLE)
            return Decode(self.instruction)
        elif self.cycles == 0:
            global_data.ICACHE_USING_BUS = False
            self.instruction.MISSED_ICACHE = False
        return self

    def flush(self):
        if self.cycles == 0 and global_data.FU_STATUS['ID'] == False:
            global_data.FU_STATUS['IF'] = False
            global_data.ICACHE_USING_BUS = False
            self.instruction.IF = str(global_data.CLOCK_CYCLE)
            global_data.RESULT_LIST.append(self.instruction)
            return None
        elif self.cycles == 0:
            global_data.ICACHE_USING_BUS = False
            self.instruction.MISSED_ICACHE = False
        return self

class Decode(Stage):
    def __init__(self, instruction):
        self.name = 'ID'
        Stage.__init__(self, instruction)
        self.cycles = simulator.get_cycles('ID', self.instruction)
        self.NEW_PC = 0
        self.TAKE_BRANCH = False
        self.SETTING_FLUSH_NEXT = True
        self.FLAG = False

    def execute(self):
        global_data.FU_STATUS['ID'] = True

        if (self.instruction.regAvailable()):
            if self.cycles > 0:
                self.cycles -= 1

            if self.cycles == 0:
                if self.instruction.opcode == 'BNE':
                    if global_data.REGISTERS[self.instruction.dest] != global_data.REGISTERS[self.instruction.operands[0]]:
                        for stage in global_data.pipeline:
                            if stage.__class__.__name__ == "Fetch":
                                self.FLAG = True
                                stage.instruction.FLUSH_FLAG = True
                        if not self.FLAG:
                            global_data.SET_FLUSH_NEXT = True
                            self.FLAG = True
                        self.NEW_PC = global_data.get_label_index(self.instruction.operands[1])
                        self.TAKE_BRANCH = True

                if self.instruction.opcode == 'BEQ':
                    if global_data.REGISTERS[self.instruction.dest] == global_data.REGISTERS[self.instruction.operands[0]]:
                        for stage in global_data.pipeline:
                            if stage.__class__.__name__ == "Fetch":
                                self.FLAG = True
                                stage.instruction.FLUSH_FLAG = True
                        if not self.FLAG:
                            global_data.SET_FLUSH_NEXT = True
                            self.FLAG = True
                        self.NEW_PC = global_data.get_label_index(self.instruction.operands[1])
                        self.TAKE_BRANCH = True

                if self.instruction.opcode == 'J':
                    for stage in global_data.pipeline:
                        if stage.__class__.__name__ == "Fetch":
                            self.FLAG = True
                            stage.instruction.FLUSH_FLAG = True
                    if not self.FLAG:
                        global_data.SET_FLUSH_NEXT = True
                        self.FLAG = True
                    self.NEW_PC = global_data.get_label_index(self.instruction.dest)
                    self.TAKE_BRANCH = True

    def next(self):
        if self.instruction.opcode in ['HLT','BNE','J','BEQ'] and self.cycles == 0:
            if self.TAKE_BRANCH:
                global_data.JUMP = True
                global_data.JUMP_TO = self.NEW_PC
                self.TAKE_BRANCH = False

            global_data.FU_STATUS['ID'] = False
            self.instruction.ID = str(global_data.CLOCK_CYCLE)
            global_data.RESULT_LIST.append(self.instruction)
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
        self.name = 'IU'
        Stage.__init__(self, instruction)
        self.cycles = simulator.get_cycles('EX', self.instruction)
        self.TO_EXECUTE = True

    def execute(self):
        global_data.FU_STATUS['IU'] = True
        self.instruction.lockRegisters()
        if self.cycles > 0:
            self.cycles -= 1

        if self.TO_EXECUTE:
            if self.instruction.opcode == 'DADD':
                global_data.REGISTER_LATCH[self.instruction.dest] = global_data.REGISTERS[self.instruction.operands[0]] + global_data.REGISTERS[self.instruction.operands[1]]
            elif self.instruction.opcode == 'DADDI':
                global_data.REGISTER_LATCH[self.instruction.dest] = global_data.REGISTERS[self.instruction.operands[0]] + int(self.instruction.operands[1])
            elif self.instruction.opcode == 'DSUB':
                global_data.REGISTER_LATCH[self.instruction.dest] = global_data.REGISTERS[self.instruction.operands[0]] - global_data.REGISTERS[self.instruction.operands[1]]
            elif self.instruction.opcode == 'DSUBI':
                global_data.REGISTER_LATCH[self.instruction.dest] = global_data.REGISTERS[self.instruction.operands[0]] - int(self.instruction.operands[1])
            elif self.instruction.opcode == 'AND':
                global_data.REGISTER_LATCH[self.instruction.dest] = global_data.REGISTERS[self.instruction.operands[0]] & global_data.REGISTERS[self.instruction.operands[1]]
            elif self.instruction.opcode == 'ANDI':
                global_data.REGISTER_LATCH[self.instruction.dest] = global_data.REGISTERS[self.instruction.operands[0]] & int(self.instruction.operands[1])
            elif self.instruction.opcode == 'OR':
                global_data.REGISTER_LATCH[self.instruction.dest] = global_data.REGISTERS[self.instruction.operands[0]] | global_data.REGISTERS[self.instruction.operands[1]]
            elif self.instruction.opcode == 'ORI':
                global_data.REGISTER_LATCH[self.instruction.dest] = global_data.REGISTERS[self.instruction.operands[0]] | int(self.instruction.operands[1])
            else:
                pass
            self.TO_EXECUTE = False

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
        self.cycles = simulator.get_cycles('EX', self.instruction)

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
        self.cycles = simulator.get_cycles('EX', self.instruction)

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
        self.cycles = simulator.get_cycles('EX', self.instruction)

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
        self.ONLY_ONCE = True
        Stage.__init__(self, instruction)
        self.cycles = simulator.get_cycles('MEM', self.instruction)

    def execute(self):
        global_data.FU_STATUS['MEM'] = True
        if self.instruction.MISSED_DCACHE:
            if not global_data.ICACHE_USING_BUS:
                # print self.instruction.opcode + " seizing memory bus in cycle: " + str(global_data.CLOCK_CYCLE)
                global_data.DCACHE_USING_BUS = True
                if self.ONLY_ONCE:
                    self.ONLY_ONCE = False
                    global_data.JUST_ENTERED_BUS = True
                if self.cycles > 0:
                    self.cycles -= 1
        elif self.cycles > 0:
            self.cycles -= 1

    def next(self):
        if self.cycles == 0 and global_data.FU_STATUS['WB'] == False:
            global_data.FU_STATUS['MEM'] = False
            global_data.DCACHE_USING_BUS = False
            self.instruction.EX = str(global_data.CLOCK_CYCLE)
            return WriteBack(self.instruction)
        elif self.cycles == 0:
            self.instruction.MISSED_DCACHE = False
            global_data.DCACHE_USING_BUS = False
            self.instruction.Struct = 'Y'
        return self

class WriteBack(Stage):
    def __init__(self, instruction):
        self.name = 'WB'
        Stage.__init__(self, instruction)
        self.cycles = simulator.get_cycles('WB', self.instruction)

    def execute(self):
        if self.instruction.opcode == 'LW':
            global_data.FU_STATUS['WB'] = True
        for key in global_data.REGISTER_LATCH:
            global_data.REGISTERS[key] = global_data.REGISTER_LATCH[key]
        global_data.REGISTER_LATCH.clear()
        self.instruction.releaseRegisters()
        if self.cycles > 0:
            self.cycles -= 1

    def next(self):
        if self.cycles == 0:
            global_data.FU_STATUS['WB'] = False
            self.instruction.WB = str(global_data.CLOCK_CYCLE)
            global_data.RESULT_LIST.append(self.instruction)
            return None
        return self
