import os
import numpy as np

class InvertedIndex:
    def __init__(self, index_name):
        index_dir = os.path.join(index_name)
        self.docs = np.memmap(index_name + ".docs", dtype=np.uint32,
              mode='r')
    def __iter__(self):
        i = 2
        while i < len(self.docs):
            size = self.docs[i]
            print(DeltaEncoding(self.docs[i+1:size+i+1]))
            i += size+1
        
    def __next__(self):
        return self
    
def DeltaEncoding(postingList):
    last = 0 
    countBytes = 0
    for i in range(0, len(postingList)-1, 1):
        print("save me")
        current = postingList[i]
        delta = current - last;
        last = current;
        countBytes += delta//128
        if (countBytes%128 != 0):
            countBytes +=1
    return countBytes
        

for i, docs in enumerate(InvertedIndex("/home/josh/output/output.url.inv")):
    print(i, docs)
