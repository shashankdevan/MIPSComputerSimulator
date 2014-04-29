import global_data

class ICacheBlock:
    def __init__(self):
        self.TAG = 0
        self.words = [0, 0, 0, 0]
        self.isValid = False

class ICache:
    def __init__(self, icache_blocks):
        self.cache = icache_blocks

    def readInstruction(self, index):
        global_data.ICACHE_ACCESS += 1
        cache_row = (index >> 2) & 3
        tag = index >> 4
        if global_data.icache.cache[cache_row].isValid and global_data.icache.cache[cache_row].TAG == tag:
            global_data.ICACHE_HIT += 1
            return 1
        else:
            global_data.MEMORY_BUS_BUSY = True
            global_data.ICACHE_MISS += 1
            global_data.icache.cache[cache_row].isValid = True
            return self.fetch_instr(index)

    def fetch_instr(self, index):
        cache_row = (index >> 2) & 3
        tag = index >> 4
        global_data.icache.cache[cache_row].TAG = tag
        return 6
