from collections import deque
from instruction import *
from stages import *
import collections, sys
import global_data, stages, d_cache
import copy

def parseInstruction(line):
    operands = []
    label = ""
    dest = ""
    opcode = ""
    offset = 0

    if ':' in line:
        label = line[:line.index(':')].upper()
        tokens = line[line.index(':') + 1:].strip().split(' ', 1)
    else:
        tokens = line.strip().split(' ', 1)
    if len(tokens) > 1:
        opcode = tokens[0].upper()
        tokens = tokens[1].split(',')
        dest = tokens[0].strip().upper()
        if len(tokens) > 1:
            for token in tokens[1:]:
                operands.append(token.strip().upper())
    else:
        opcode = tokens[0].upper()

    if opcode in ['LW', 'SW', 'L.D', 'S.D']:
        if '(' in operands[0]:
            offset = int(operands[0][:int(operands[0].index('('))])
            operands[0] = operands[0][int(operands[0].index('(')) + 1: int(operands[0].index(')'))]

    inst = Instruction(label, opcode, dest, operands)
    inst.offset = offset
    return inst

def get_exec_unit(inst):
    if inst.opcode in ['LW', 'SW', 'L.D', 'S.D', 'DADD', 'DSUB', 'DADDI', 'DSUBI', 'OR', 'ORI', 'AND', 'ANDI']:
        inst.exec_unit = 'IU'
    if inst.opcode in ['ADD.D','SUB.D']:
        inst.exec_unit = 'FPADDER'
    if inst.opcode in ['MULT.D', 'MUL.D']:
        inst.exec_unit = 'FPMULTIPLIER'
    if inst.opcode == 'DIV.D':
        inst.exec_unit = 'FPDIVIDER'


def loadInstructions(inst_file):
    cnt = 0
    for line in inst_file:
        inst = parseInstruction(line)
        inst.index = cnt
        get_exec_unit(inst)
        global_data.INSTRUCTIONS.append(inst)
        cnt += 1

def loadRegisters(reg_file):
    cnt = -1
    for line in reg_file:
        cnt = cnt + 1
        reg = 'R'
        reg = reg + str(cnt)
        global_data.REGISTERS[reg] = int(line, 2)
        global_data.RG_STATUS[reg] = False
    cnt = -1
    for i in range(32):
        cnt = cnt + 1
        reg = 'F'
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
                global_data.FU_CYCLES['FPADDER'] = int(tokens[0])
                global_data.FU_PIPELINED['FPADDER'] = tokens[1].strip().upper()
            if (FU == "FPMULTIPLIER"):
                global_data.FU_CYCLES['FPMULTIPLIER'] = int(tokens[0])
                global_data.FU_PIPELINED['FPMULTIPLIER'] = tokens[1].strip().upper()
            if (FU == "FPDIVIDER"):
                global_data.FU_CYCLES['FPDIVIDER'] = int(tokens[0])
                global_data.FU_PIPELINED['FPDIVIDER'] = tokens[1].strip().upper()
        else:
            if (FU == "MAINMEMORY"):
                global_data.MAIN_MEMORY_ACCESS_TIME = int(tokens[0].strip())
            if (FU == "I-CACHE"):
                global_data.I_CACHE_ACCESS_TIME = int(tokens[0].strip())
            if (FU == "D-CACHE"):
                global_data.D_CACHE_ACCESS_TIME = int(tokens[0].strip())

    global_data.FU_PIPELINED['MEM'] = 'YES'
    global_data.FU_CYCLES['MEM'] = 1
    global_data.DATA_MEMORY_ACCESS_LATENCY = 2 * (global_data.D_CACHE_ACCESS_TIME + global_data.MAIN_MEMORY_ACCESS_TIME)
    global_data.INSTR_MEMORY_ACCESS_LATENCY = 2 * (global_data.I_CACHE_ACCESS_TIME + global_data.MAIN_MEMORY_ACCESS_TIME)

def get_cycles(stage, instruction):
    if stage == 'IF':
        cycles = global_data.icache.readInstruction(instruction.index)
        if cycles != 1:
            instruction.MISSED_ICACHE = True
        return cycles
    elif stage == 'ID':
        return 1
    elif stage == 'EX' and instruction.opcode in ['DADD', 'DADDI','DSUB','DSUBI','AND','ANDI','OR','ORI']:
        return 1
    elif stage == 'EX' and instruction.opcode in ['LW','SW','L.D','S.D']:
        return 1
    elif stage == 'EX' and instruction.opcode in ['ADD.D', 'SUB.D']:
        return global_data.FU_CYCLES['FPADDER']
    elif stage == 'EX' and instruction.opcode in ['MULT.D', 'MUL.D']:
        return global_data.FU_CYCLES['FPMULTIPLIER']
    elif stage == 'EX' and instruction.opcode in ['DIV.D']:
        return global_data.FU_CYCLES['FPDIVIDER']

    elif stage == 'MEM' and instruction.opcode in ['LW']:
        address = global_data.REGISTERS[instruction.operands[0]] + instruction.offset
        data, cycles, combination = global_data.dcache.fetch_word(address ,1)
        global_data.REGISTERS[instruction.dest] = data
        instruction.COMBINATION = combination
        if cycles != 1:
            instruction.MISSED_DCACHE = True
        return cycles

    elif stage == 'MEM' and instruction.opcode in ['SW']:
        address = global_data.REGISTERS[instruction.operands[0]] + instruction.offset
        cycles, combination = global_data.dcache.store_word(address, global_data.REGISTERS[instruction.dest], 1)
        instruction.COMBINATION = combination
        if cycles != 1:
            instruction.MISSED_DCACHE = True
        return cycles

    elif stage == 'MEM' and instruction.opcode in ['L.D']:
        address = global_data.REGISTERS[instruction.operands[0]] + instruction.offset
        data, cycles, combination = global_data.dcache.fetch_word(address ,2)
        instruction.COMBINATION = combination
        if cycles != 2:
            instruction.MISSED_DCACHE = True
            if cycles % 2 == 1:
                instruction.missCycles = cycles - 1
            else:
                instruction.missCycles = cycles
        return cycles

    elif stage == 'MEM' and instruction.opcode in ['S.D']:
        address = global_data.REGISTERS[instruction.operands[0]] + instruction.offset
        cycles, combination = global_data.dcache.store_word(address, global_data.REGISTERS[instruction.dest], 2)
        instruction.COMBINATION = combination
        if cycles != 2:
            instruction.MISSED_DCACHE = True
            if cycles % 2 == 1:
                instruction.missCycles = cycles - 1
            else:
                instruction.missCycles = cycles
        return cycles

    elif stage == 'MEM':
        return 1
    elif stage == 'WB':
        return 1
    else:
        return 1

def print_results():
    global_data.RESULT_LIST.sort(key = lambda x: int(x.IF))

    global_data.output += '-' * 100 + '\n'
    global_data.output += "%5s %-10s\t%5s\t%5s\t%5s\t%5s\t%5s\t%5s\t%5s\t%5s\n" % (" ", "Instruction", "FT", "ID", "EX", "WB", "RAW", "WAR", "WAW", "Struct")
    global_data.output += '-' * 100 + '\n'

    global_data.RESULT_LIST[len(global_data.RESULT_LIST) - 1].ID = ''
    for inst in global_data.RESULT_LIST:
        inst.printInst()

def initialize():
    if (len(sys.argv) != 6):
        print "Usage: simulator inst.txt data.txt reg.txt config.txt result.txt"
        exit()
    inst_file = open(sys.argv[1])
    mem_file = open(sys.argv[2])
    reg_file = open(sys.argv[3])
    config_file = open(sys.argv[4])
    global_data.result_file = sys.argv[5]

    loadInstructions(inst_file)
    loadRegisters(reg_file)
    loadData(mem_file)
    loadConfig(config_file)

def displayStatistics():
    global_data.output += "Total number of requests to instruction cache: " + str(global_data.ICACHE_ACCESS) + '\n'
    global_data.output += "Total number of instruction cache hits: " + str(global_data.ICACHE_HIT) + '\n'
    global_data.output += "Total number of requests to data cache: " + str(global_data.DCACHE_ACCESS) + '\n'
    global_data.output += "Total number of data cache hits: " + str(global_data.DCACHE_HIT) + '\n'

def assignPriority():
    nonpipelined = deque()
    pipelined = deque()

    for s in global_data.EXQueue:
        if global_data.FU_PIPELINED[s.__class__.__name__.upper()] == 'NO':
            s.exec_cycles = global_data.FU_CYCLES[s.__class__.__name__.upper()]
            nonpipelined.append(s)
        elif global_data.FU_PIPELINED[s.__class__.__name__.upper()] == 'YES':
            s.exec_cycles = global_data.FU_CYCLES[s.__class__.__name__.upper()]
            pipelined.append(s)

    pipelined = list(pipelined)
    pipelined.sort(key = lambda x: int(x.exec_cycles), reverse=True)
    nonpipelined = list(nonpipelined)
    nonpipelined.sort(key = lambda x: int(x.exec_cycles), reverse=True)

    global_data.EXQueue.clear()
    global_data.EXQueue = deque(nonpipelined + pipelined)


def prioritizePipeline():

    global_data.IFQueue.clear()
    global_data.IDQueue.clear()
    global_data.IUQueue.clear()
    global_data.EXQueue.clear()
    global_data.WBQueue.clear()

    for s in global_data.pipeline:
        if s.name == 'WB':
            global_data.WBQueue.append(s)
        elif s.name == 'EX':
            global_data.EXQueue.append(s)
        elif s.name == 'IU':
            global_data.IUQueue.append(s)
        elif s.name == 'ID':
            global_data.IDQueue.append(s)
        elif s.name == 'IF':
            global_data.IFQueue.append(s)
    assignPriority()

    p = []
    p = list(global_data.WBQueue) + list(global_data.EXQueue) + list(global_data.IUQueue) + list(global_data.IDQueue) + list(global_data.IFQueue)
    global_data.pipeline.clear()
    global_data.pipeline = deque(p)

def startSimulation():
    i = 0
    fetch_stage = Fetch(copy.deepcopy(global_data.INSTRUCTIONS[i]))
    fetch_stage.execute()
    global_data.pipeline.append(fetch_stage)

    while(len(global_data.pipeline) > 0):
        prioritizePipeline()

        for stage in ['WB', 'EX', 'IU', 'ID', 'IF']:
            save_size = len(global_data.pipeline)
            while(save_size > 0):
                curr_stage = global_data.pipeline.popleft()
                if curr_stage.name == stage:
                    if curr_stage.instruction.FLUSH_FLAG:
                        next_stage = curr_stage.flush()
                    else:
                        next_stage = curr_stage.next()
                    if (next_stage != None):
                        next_stage.execute()
                        global_data.pipeline.append(next_stage)
                    else:
                        save_size -= 1
                else:
                    global_data.pipeline.append(curr_stage)
                save_size -= 1

        if(global_data.FU_STATUS['IF'] == False):
            if global_data.JUMP:
                i = global_data.JUMP_TO
                global_data.JUMP = False
            else:
                i += 1
            if i < len(global_data.INSTRUCTIONS):
                next_inst = copy.deepcopy(global_data.INSTRUCTIONS[i])
                index = i
                cache_row = (index >> 2) & 3
                tag = index >> 4
                if (not global_data.icache.cache[cache_row].isValid) or global_data.icache.cache[cache_row].TAG != tag:
                    if global_data.JUST_ENTERED_BUS:
                        global_data.DCACHE_USING_BUS = False

                if global_data.SET_FLUSH_NEXT:
                    next_inst.FLUSH_FLAG = True
                    global_data.SET_FLUSH_NEXT = False

                new_fetch_stage = Fetch(next_inst)
                new_fetch_stage.execute()
                global_data.pipeline.append(new_fetch_stage)

        global_data.JUST_ENTERED_BUS = False
        global_data.CLOCK_CYCLE += 1

    print_results()

def outputResult():
    result = open(global_data.result_file, 'w')
    print global_data.output
    result.write(global_data.output)

if __name__ == '__main__':
    initialize()
    startSimulation()
    global_data.output += '\n'
    displayStatistics()
    outputResult()
