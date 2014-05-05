import global_data
import simulator

class CacheBlock:
    def __init__(self, tag, words):
        self.isValid = False
        self.TAG = tag
        self.words = words
        self.LRU_FLAG = True
        self.DIRTY = False

class Cache:
    def __init__(self, cache_blk_rows):
        self.cache = cache_blk_rows

    def fetch_data(self, address):
        global_data.DCACHE_ACCESS += 1

        blk_row = ((address & 112) >> 4) & 1
        tag = (address & 112) >> 5
        word_idx = (address & 12) >> 2
        HIT = False
        return_value = 0

        for blk in self.cache[blk_row]:
            if (blk.isValid == True and blk.TAG == tag):
                global_data.DCACHE_HIT += 1
                HIT = True
                return_value = 1
                return global_data.DATA[address], return_value

        if not HIT:
            global_data.DCACHE_MISS += 1

            start_addr = (address & 112) + global_data.DATA_SEGMENT_BASE_ADDR
            incoming_blk_contents = []
            j = 0
            for i in range(4):
                incoming_blk_contents.append(global_data.DATA[start_addr + j])
                j += 4
            incoming_blk = CacheBlock(tag, incoming_blk_contents)

            if self.cache[blk_row][0].LRU_FLAG:
                if self.cache[blk_row][0].DIRTY:
                    return_value += global_data.DATA_MEMORY_ACCESS_LATENCY
                self.cache[blk_row][0] = incoming_blk
                self.cache[blk_row][0].LRU_FLAG = False
                self.cache[blk_row][0].DIRTY = False
                self.cache[blk_row][1].LRU_FLAG = True
                self.cache[blk_row][0].isValid = True
                return_value += global_data.DATA_MEMORY_ACCESS_LATENCY

            elif self.cache[blk_row][1].LRU_FLAG:
                if self.cache[blk_row][1].DIRTY:
                    return_value += 6
                self.cache[blk_row][1] = incoming_blk
                self.cache[blk_row][1].LRU_FLAG = False
                self.cache[blk_row][1].DIRTY = False
                self.cache[blk_row][0].LRU_FLAG = True
                self.cache[blk_row][1].isValid = True
                return_value += global_data.DATA_MEMORY_ACCESS_LATENCY
            return global_data.DATA[address], return_value

    def fetch_word(self, address, n):
        result = []
        total_cycles = []
        for i in range(n):
            word, cycles = self.fetch_data(address + i*4)
            result.append(word)
            total_cycles.append(cycles)

        if n == 2:
            result[0] = (result[0] << 32) | result[1]
            if (total_cycles[0] == 1 and total_cycles[1] == 6) or (total_cycles[0] == 1 and total_cycles[1] == 12):
                return result[0], sum(total_cycles), 1
            elif (total_cycles[0] == 6 and total_cycles[1] == 1) or (total_cycles[0] == 12 and total_cycles[1] == 1):
                return result[0], sum(total_cycles), 2
            else:
                return result[0], sum(total_cycles), 0
        else:
            return result[0], total_cycles[0], 0


    def store_data(self, address, data):
        global_data.DCACHE_ACCESS += 1

        blk_row = ((address & 112) >> 4) & 1
        tag = (address & 112) >> 5
        word_idx = (address & 12) >> 2
        HIT = False
        return_value = 0

        for blk in self.cache[blk_row]:
            if (blk.isValid == True and blk.TAG == tag):
                global_data.DCACHE_HIT += 1

                HIT = True
                blk.DIRTY = True
                global_data.DATA[address] = data
                return_value += 1
                return return_value

        if not HIT:
            global_data.DCACHE_MISS += 1
            global_data.DATA[address] = data

            if self.cache[blk_row][0].LRU_FLAG:
                if self.cache[blk_row][0].DIRTY:
                    return_value += 6
                self.cache[blk_row][0].LRU_FLAG = False
                self.cache[blk_row][0].DIRTY = False
                self.cache[blk_row][1].LRU_FLAG = True
                self.cache[blk_row][0].isValid = True
                return_value += global_data.DATA_MEMORY_ACCESS_LATENCY

            elif self.cache[blk_row][1].LRU_FLAG:
                if self.cache[blk_row][0].DIRTY:
                    return_value += 6
                self.cache[blk_row][1].LRU_FLAG = False
                self.cache[blk_row][1].DIRTY = False
                self.cache[blk_row][0].LRU_FLAG = True
                self.cache[blk_row][1].isValid = True
                return_value += global_data.DATA_MEMORY_ACCESS_LATENCY
            return return_value

    def store_word(self, address, data, n):
        total_cycles = []
        for i in range(n):
            cycles = self.store_data(address + i*4, data)
            total_cycles.append(cycles)

        if n == 2:
            if (total_cycles[0] == 1 and total_cycles[1] == 6) or (total_cycles[0] == 1 and total_cycles[1] == 12):
                return sum(total_cycles), 1
            elif (total_cycles[0] == 6 and total_cycles[1] == 1) or (total_cycles[0] == 12 and total_cycles[1] == 1):
                return sum(total_cycles), 2
            else:
                return sum(total_cycles), 0
        else:
            return total_cycles[0], 0


    def writeToMemory(self, blk, row):
        start_addr = (((blk.TAG << 1) ^ row) << 4) + global_data.DATA_SEGMENT_BASE_ADDR
        for i in range(4):
            j = i * 4
            global_data.DATA[start_addr + j] = blk.words[i]
