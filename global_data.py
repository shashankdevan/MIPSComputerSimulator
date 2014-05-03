import collections
import d_cache, i_cache
import simulator
from collections import deque

#globals
pipeline = deque()

IFQueue = deque()
IDQueue = deque()
IUQueue = deque()
EXQueue = deque()
WBQueue = deque()

CLOCK_CYCLE = 1
REGISTERS = {}
REGISTER_LATCH = {}
DATA = {}
INSTRUCTIONS = []
RESULT_LIST = []
FU_STATUS = {'IF': False,
             'ID': False,
             'IU': False,
             'FPADDER': False,
             'FPMULTIPLIER': False,
             'FPDIVIDER': False,
             'MEM': False,
             'WB': False }
RG_STATUS = collections.defaultdict(lambda: False)

FU_CYCLES = collections.defaultdict(lambda: 0)
FU_PIPELINED = collections.defaultdict(lambda: False)
MAIN_MEMORY_ACCESS_TIME = 0
D_CACHE_ACCESS_TIME = 0
I_CACHE_ACCESS_TIME = 0
DATA_MEMORY_ACCESS_LATENCY = 0
INSTR_MEMORY_ACCESS_LATENCY = 0




WB_USED = False
FLUSH_NEXT = False
SET_FLUSH_NEXT = False
JUMP = False
JUMP_TO = 0

DATA_SEGMENT_BASE_ADDR = 256
JUST_ENTERED_BUS = False
ICACHE_USING_BUS = False
DCACHE_USING_BUS = False

blk_row1 = []
blk_row1.append(d_cache.CacheBlock(0, [0,0,0,0]))
blk_row1.append(d_cache.CacheBlock(0, [0,0,0,0]))

blk_row2 = []
blk_row2.append(d_cache.CacheBlock(0, [0,0,0,0]))
blk_row2.append(d_cache.CacheBlock(0, [0,0,0,0]))

cache_blk_rows = []
cache_blk_rows.append(blk_row1)
cache_blk_rows.append(blk_row2)

dcache = d_cache.Cache(cache_blk_rows)

DCACHE_ACCESS = 0
DCACHE_HIT = 0
DCACHE_MISS = 0


icache_blocks = []
icache_blocks.append(i_cache.ICacheBlock())
icache_blocks.append(i_cache.ICacheBlock())
icache_blocks.append(i_cache.ICacheBlock())
icache_blocks.append(i_cache.ICacheBlock())

icache = i_cache.ICache(icache_blocks)
ICACHE_ACCESS = 0
ICACHE_HIT = 0
ICACHE_MISS = 0

def get_label_index(label):
    for i in range(len(INSTRUCTIONS)):
        if INSTRUCTIONS[i].label == label:
            return i

def reg_status():
    for reg in RG_STATUS:
        print reg, RG_STATUS[reg]

def resetFlags():
    WB_USED = False
