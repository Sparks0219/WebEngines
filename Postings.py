import os
import numpy as np

class InvertedIndex:
    def __init__(self, index_name):
        index_dir = os.path.join(index_name)
        self.docs = np.memmap(index_name + ".docs", dtype=np.uint32, mode='r')
    def __iter__(self):
        i = 2
        while i < len(self.docs):
            size = self.docs[i]
            print(GammaEncoding(self.docs[i+1:size+i+1]))
            i += size+1
        
    def __next__(self):
        return self
    
def GammaEncoding(postingList):
    last = 0 
    countBytes = 0
    i = 0
    while i < len(postingList):
        print(countBytes)
        current = postingList[i]
        delta = current - last
        last = current
        countBytes += 2*(np.ceil(np.log2(delta)).astype(int))-1
        i +=1
    return countBytes
        
    

for i, docs in enumerate(InvertedIndex("/home/josh/output/output.url.inv")):
    print(i, docs)
