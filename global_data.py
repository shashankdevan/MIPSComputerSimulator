import collections
import d_cache

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


def reg_status():
    for reg in RG_STATUS:
        print reg, RG_STATUS[reg]


def resetFlags():
    WB_USED = False
