import collections

#globals
CLOCK_CYCLE = 0
REGISTERS = collections.defaultdict(lambda: False)
INSTRUCTIONS = []
FU_STATUS = {'IF': False,
             'ID': False,
             'IU': False,
             'FP_Adder': False,
             'FP_Multiplier': False,
             'FP_Divider': False,
             'WB': False }
REPEAT = True
