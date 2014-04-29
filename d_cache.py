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
        blk_row = ((address & 112) >> 4) & 1
        tag = (address & 112) >> 5
        word_idx = (address & 12) >> 2
        HIT = False
        return_value = 0

        #check if present in cache
        for blk in self.cache[blk_row]:
            if (blk.isValid == True and blk.TAG == tag):
                HIT = True
                return_value += 1
                return blk.words[word_idx], return_value

        #get from memory if it's a MISS
        if not HIT:
            start_addr = (address & 112) + global_data.DATA_SEGMENT_BASE_ADDR
            incoming_blk_contents = []
            j = 0
            for i in range(4):
                incoming_blk_contents.append(global_data.DATA[start_addr + j])
                j += 4
            incoming_blk = CacheBlock(tag, incoming_blk_contents)

            if self.cache[blk_row][0].LRU_FLAG:
                #write if for dirty bit = true
                if self.cache[blk_row][0].DIRTY:
                    return_value += 6
                    self.writeToMemory(self.cache[blk_row][0])
                self.cache[blk_row][0] = incoming_blk
                self.cache[blk_row][0].LRU_FLAG = False
                self.cache[blk_row][0].DIRTY = False
                self.cache[blk_row][1].LRU_FLAG = True
                self.cache[blk_row][0].isValid = True
                return_value += 6

            elif self.cache[blk_row][1].LRU_FLAG:
                #write if for dirty bit = true
                if self.cache[blk_row][0].DIRTY:
                    return_value += 6
                    self.writeToMemory(self.cache[blk_row][1])
                self.cache[blk_row][1] = incoming_blk
                self.cache[blk_row][1].LRU_FLAG = False
                self.cache[blk_row][1].DIRTY = False
                self.cache[blk_row][0].LRU_FLAG = True
                self.cache[blk_row][1].isValid = True
                return_value += 6
            else:
                print "None of the blocks available! LRU not proper!" #can remove this line
            return incoming_blk_contents[word_idx], return_value

    def fetch_word(self, address, n):
        result = []
        total_cycles = 0
        for i in range(n):
            word, cycles = self.fetch_data(address + i*4)
            result.append(word)
            total_cycles += cycles
        if n == 2:
            result[0] = (result[0] << 32) | result[1]
        return result[0], total_cycles


    def store_data(self, address, data):
        blk_row = ((address & 112) >> 4) & 1
        tag = (address & 112) >> 5
        word_idx = (address & 12) >> 2
        HIT = False
        return_value = 0

        #check if present in cache
        for blk in self.cache[blk_row]:
            if (blk.isValid == True and blk.TAG == tag):
                HIT = True
                blk.DIRTY = True
                blk.words[word_idx] = data
                return_value += 1
                return return_value

        #not present in cache
        if not HIT:
            global_data.DATA[address] = data #write data to memory

            if self.cache[blk_row][0].LRU_FLAG:
                #write if for dirty bit = true
                if self.cache[blk_row][0].DIRTY:
                    return_value += 6
                    self.writeToMemory(self.cache[blk_row][0])
                self.cache[blk_row][0].words[word_idx] = data
                self.cache[blk_row][0].LRU_FLAG = False
                self.cache[blk_row][0].DIRTY = False
                self.cache[blk_row][1].LRU_FLAG = True
                self.cache[blk_row][0].isValid = True
                return_value += 6

            elif self.cache[blk_row][1].LRU_FLAG:
                #write if for dirty bit = true
                if self.cache[blk_row][0].DIRTY:
                    return_value += 6
                    self.writeToMemory(self.cache[blk_row][1])
                self.cache[blk_row][1].words[word_idx] = data
                self.cache[blk_row][1].LRU_FLAG = False
                self.cache[blk_row][1].DIRTY = False
                self.cache[blk_row][0].LRU_FLAG = True
                self.cache[blk_row][1].isValid = True
                return_value += 6
            else:
                print "None of the blocks available! LRU not proper!" #can remove this line
            return return_value

    def store_word(self, address, data, n):
        cycles = self.store_data(address, data)
        return cycles

if __name__ == '__main__':
    data_file = open('data.txt')
    simulator.loadData(data_file)

    blk_row1 = []
    blk_row1.append(CacheBlock(0, [2,65,112,84]))
    blk_row1.append(CacheBlock(2, [4,50,25,120]))

    blk_row2 = []
    blk_row2.append(CacheBlock(1, [2,65,112,84]))
    blk_row2.append(CacheBlock(2, [4,50,118,120]))

    cache_blk_rows = []
    cache_blk_rows.append(blk_row1)
    cache_blk_rows.append(blk_row2)

    dcache = Cache(cache_blk_rows)
    print dcache.fetch_data(118)
