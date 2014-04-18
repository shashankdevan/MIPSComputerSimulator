import collections

#globals
CLOCK_CYCLE = 0
REGISTERS = collections.defaultdict(lambda: False)
INSTRUCTIONS = []
FU_STATUS = {'IF': False,
             'ID': False,
             'IU': False,
             'FPAdder': False,
             'FPMultiplier': False,
             'FPDivider': False,
             'WB': False }
REPEAT = True
