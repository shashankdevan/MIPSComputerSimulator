import collections

#globals
CLOCK_CYCLE = 0
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
