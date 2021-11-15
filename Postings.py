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
            print(VarByteEncoding(self.docs[i+1:size+i+1]))
            #print(GammaEncoding(self.docs[i+1:size+i+1]))
            i += size+1
        
    def __next__(self):
        return self
    
def GammaEncoding(postingList):
    last = 0 
    countBits = 0
    i = 0
    while i < len(postingList):
        print(countBits)
        current = postingList[i]
        delta = current - last
        last = current
        countBits += 2*(np.floor(np.log2(1)).astype(int))+1
        i +=1
    return np.ceil(countBits/8)

def VarByteEncoding(postingList):
    last = 0 
    countBytes = 0
    i = 0
    while i < len(postingList):
        print(countBytes)
        current = postingList[i]
        delta = current - last - 1 
        last = current
        while delta >= 128: 
            delta = delta//128
            countBytes += 1
        countBytes += 1
        i +=1
    return countBytes
        
    
def Simple9(postingList):
    i = 0 
    postingList = [postingList[i]-postingList[i-1] for i in range(len(postingList)) if i == 0 else postingList[i]]
    while i < len(postingList):
        print(countBytes) 
        if (max(postingList[i:28]) <= 1):
            i+=28
        else if (max(postingList[i:14] <= 3):
            i+=14
        else if (max(postingList[i:9] <= 7):
            i+=9
        else if (max(postingList[i:7] <= 15):
            i+=7
        else if (max(postingList[i:5] <= 31):
            i+=5
        else if (max(postingList[i:4] <= 127):
            i+=4
        else if (max(postingList[i:3] <= 511):
            i+=3
        else if (max(postingList[i:2] <= 16383):
            i+=2 
        else: #assuming all numbers are less than 268435456 (2^28)
            i+=1 
        countBytes+=4 
#def PforDelta(postingList): 

for i, docs in enumerate(InvertedIndex("/home/josh/output/output.url.inv")):
    print(i, docs)
