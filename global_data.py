import collections

#globals
CLOCK_CYCLE = 1
REGISTERS = {}
DATA = {}
INSTRUCTIONS = []
FU_STATUS = {'IF': False,
             'ID': False,
             'IU': False,
             'FPAdder': False,
             'FPMultiplier': False,
             'FPDivider': False,
             'MEM': False,
             'WB': False }
RG_STATUS = collections.defaultdict(lambda: False)

FU_CYCLES = collections.defaultdict(lambda: 0)
FU_PIPELINED = collections.defaultdict(lambda: False)
WB_USED = False

def reg_status():
    for reg in RG_STATUS:
        print reg, RG_STATUS[reg]


def resetFlags():
    WB_USED = False
