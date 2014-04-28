import collections
import d_cache
import simulator
from collections import deque

#globals
pipeline = deque()
CLOCK_CYCLE = 1
REGISTERS = {}
REGISTER_LATCH = {}
DATA = {}
INSTRUCTIONS = []
RESULT_LIST = []
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
FLUSH_NEXT = False
JUMP = False
JUMP_TO = 0

DATA_SEGMENT_BASE_ADDR = 256

blk_row1 = []
blk_row1.append(d_cache.CacheBlock(0, []))
blk_row1.append(d_cache.CacheBlock(0, []))

blk_row2 = []
blk_row2.append(d_cache.CacheBlock(0, []))
blk_row2.append(d_cache.CacheBlock(0, []))

cache_blk_rows = []
cache_blk_rows.append(blk_row1)
cache_blk_rows.append(blk_row2)

dcache = d_cache.Cache(cache_blk_rows)


def get_label_index(label):
    for i in range(len(INSTRUCTIONS)):
        if INSTRUCTIONS[i].label == label:
            return i

def reg_status():
    for reg in RG_STATUS:
        print reg, RG_STATUS[reg]


def resetFlags():
    WB_USED = False
