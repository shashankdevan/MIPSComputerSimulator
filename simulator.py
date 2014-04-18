from collections import deque
from instruction import *
from stages import *
import collections, sys
import global_data

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
        inst.exec_unit = 'FP_Adder'
    if inst.opcode == 'MULT.D':
        inst.exec_unit = 'FP_Multiplier'
    if inst.opcode == 'DIV.D':
        inst.exec_unit = 'FP_Divider'


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

def get_cycles(stage, opcode):
    if stage == 'IF':
        return 1
    elif stage == 'ID':
        return 1
    elif stage == 'EX' and opcode in ['DADD', 'DADDI','DSUB','DSUBI','AND','ANDI','OR','ORI']:
        return 2
    elif stage == 'EX' and opcode in ['LW','SW','L.D','S.D']:
        return 2
    elif stage == 'EX' and opcode in ['ADD.D', 'SUB.D']:
        return 4
    elif stage == 'EX' and opcode in ['MULT.D']:
        return 6
    elif stage == 'EX' and opcode in ['DIV.D']:
        return 20
    elif stage == 'WB':
        return 1
    else:
        return 1

def print_results():
    for inst in global_data.INSTRUCTIONS:
        inst.printInst()


def initialize():
    if (len(sys.argv) != 3):
        print "Usage: simulator inst.txt data.txt reg.txt config.txt result.txt"
        exit()
    inst_file = open(sys.argv[1])
    reg_file = open(sys.argv[2])
    loadInstructions(inst_file)
    loadRegisters(reg_file)

def startSimulation():
    i = 0
    pipeline = deque()

    fetch_stage = Fetch(global_data.INSTRUCTIONS[i])
    pipeline.append(fetch_stage)

    while(len(pipeline) > 0):
        global_data.CLOCK_CYCLE += 1
        size = len(pipeline)
        while(size > 0):
            curr_stage = pipeline.popleft()
            curr_stage.execute()
            next_stage = curr_stage.next()

            if (next_stage != None):
                pipeline.append(next_stage)
            size -= 1

        if(global_data.FU_STATUS['IF'] == False and (i+1) < len(global_data.INSTRUCTIONS)):
            i += 1
            pipeline.append(Fetch(global_data.INSTRUCTIONS[i]))

    print_results()

if __name__ == '__main__':
    initialize()
    startSimulation()
