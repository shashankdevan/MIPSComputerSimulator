from collections import deque
from instruction import *
from stages import *
import collections, sys
import global_data, d_cache
import copy

def parseInstruction(line):
    operands = []
    label = ""
    dest = ""
    opcode = ""

    if ':' in line:
        label = line[:line.index(':')]
        tokens = line[line.index(':') + 1:].split()
    else:
        tokens = line.split()
    opcode = tokens[0]
    if len(tokens) > 1:
        dest = tokens[1].strip(',')
        for operand in tokens[2:]:
            operands.append(operand.strip(','))
    return Instruction(label, opcode, dest, operands)

def get_exec_unit(inst):
    if inst.opcode in ['LW', 'SW', 'L.D', 'S.D', 'DADD', 'DSUB', 'DADDI', 'DSUBI', 'OR', 'ORI', 'AND', 'ANDI']:
        inst.exec_unit = 'IU'
    if inst.opcode in ['ADD.D','SUB.D']:
        inst.exec_unit = 'FPAdder'
    if inst.opcode in ['MULT.D', 'MUL.D']:
        inst.exec_unit = 'FPMultiplier'
    if inst.opcode == 'DIV.D':
        inst.exec_unit = 'FPDivider'


def loadInstructions(inst_file):
    for line in inst_file:
        inst = parseInstruction(line)
        get_exec_unit(inst)
        global_data.INSTRUCTIONS.append(inst)

def loadRegisters(reg_file):
    cnt = -1
    for line in reg_file:
        cnt = cnt + 1
        reg = 'R'
        reg = reg + str(cnt)
        global_data.REGISTERS[reg] = int(line, 2)
        global_data.RG_STATUS[reg] = False


def loadData(mem_file):
    addr = 256
    for line in mem_file:
        global_data.DATA[addr] = int(line, 2)
        addr += 4

def loadConfig(config_file):
    for line in config_file:
        FU = ''.join(line[:line.index(':')].upper().strip().split())
        tokens = line[line.index(':') + 1:].strip().split(',')
        if len(tokens) == 2:
            if (FU == "FPADDER"):
                global_data.FU_CYCLES['FPAdder'] = int(tokens[0])
                global_data.FU_PIPELINED['FPAdder'] = tokens[1]
            elif (FU == "FPMULTIPLIER"):
                global_data.FU_CYCLES['FPMultiplier'] = int(tokens[0])
                global_data.FU_PIPELINED['FPMultiplier'] = tokens[1]
            elif (FU == "FPDIVIDER"):
                global_data.FU_CYCLES['FPDivider'] = int(tokens[0])
                global_data.FU_PIPELINED['FPDivider'] = tokens[1]
            else:
                pass
        #put code to store I-Cache and D-Cache nos.

def get_cycles(stage, instruction):
    if stage == 'IF':
        return 1
    elif stage == 'ID':
        return 1
    elif stage == 'EX' and instruction.opcode in ['DADD', 'DADDI','DSUB','DSUBI','AND','ANDI','OR','ORI']:
        return 1
    elif stage == 'EX' and instruction.opcode in ['LW','SW','L.D','S.D']:
        return 1
    elif stage == 'EX' and instruction.opcode in ['ADD.D', 'SUB.D']:
        return global_data.FU_CYCLES['FPAdder']
    elif stage == 'EX' and instruction.opcode in ['MULT.D', 'MUL.D']:
        return global_data.FU_CYCLES['FPMultiplier']
    elif stage == 'EX' and instruction.opcode in ['DIV.D']:
        return global_data.FU_CYCLES['FPDivider']
    elif stage == 'MEM' and instruction.opcode in ['LW','SW']:
        address = global_data.REGISTERS[instruction.operands[0]] + instruction.offset
        data, cycles = global_data.dcache.fetch_word(address ,1)
        return cycles
    elif stage == 'MEM' and instruction.opcode in ['L.D','S.D']:
        address = global_data.REGISTERS[instruction.operands[0]] + instruction.offset
        data, cycles = global_data.dcache.fetch_word(address ,2)
        return cycles
    elif stage == 'MEM':
        return 1
    elif stage == 'WB':
        return 1
    else:
        return 1

def print_results():
    global_data.RESULT_LIST.sort(key = lambda x: int(x.IF))

    print '-' * 100
    print "%5s %-10s\t%5s\t%5s\t%5s\t%5s\t%5s\t%5s\t%5s\t%5s" % (" ", "Instruction", "FT", "ID", "EX", "WB", "RAW", "WAR", "WAW", "Struct")
    print '-' * 100
    for inst in global_data.RESULT_LIST:
        inst.printInst()

def initialize():
    if (len(sys.argv) != 5):
        print "Usage: simulator inst.txt data.txt reg.txt config.txt result.txt"
        exit()
    inst_file = open(sys.argv[1])
    mem_file = open(sys.argv[2])
    reg_file = open(sys.argv[3])
    config_file = open(sys.argv[4])
    loadInstructions(inst_file)
    loadRegisters(reg_file)
    loadData(mem_file)
    loadConfig(config_file)


def startSimulation():
    pipeline = deque()
    i = NEW_PC = 0
    fetch_stage = Fetch(copy.deepcopy(global_data.INSTRUCTIONS[i]))
    fetch_stage.execute()
    pipeline.append(fetch_stage)

    while(len(pipeline) > 0):
        for stage in ['WB', 'EX', 'IU', 'ID', 'IF']:
            save_size = len(pipeline)

            while(save_size > 0):
                curr_stage = pipeline.popleft()

                if curr_stage.name == stage:
                    if global_data.FLUSH:
                        next_stage = curr_stage.flush()
                    else:
                        next_stage = curr_stage.next()

                    if (next_stage != None):
                        NEW_PC = next_stage.execute()
                        pipeline.append(next_stage)
                    else:
                        save_size -= 1
                else:
                    pipeline.append(curr_stage)
                save_size -= 1

        if(global_data.FU_STATUS['IF'] == False):
           if NEW_PC != -1:
               i = NEW_PC
           else:
               i += 1
           if i < len(global_data.INSTRUCTIONS):
               new_fetch_stage = Fetch(copy.deepcopy(global_data.INSTRUCTIONS[i]))
               new_fetch_stage.execute()
               pipeline.append(new_fetch_stage)

        global_data.CLOCK_CYCLE += 1


    print_results()

if __name__ == '__main__':
    initialize()
    startSimulation()
