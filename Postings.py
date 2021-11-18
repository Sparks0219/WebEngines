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
            #Three tuple containing range, size of posting list, encoding
            #(self.docs[size+i]-self.docs[i],size,SomeEncoding(self.docs[i+1:size+i+1]))
            #print(OptPFD(self.docs[i+1:size+i+1]))
            OptPFD([0,1]*64)
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
    countBytes = 0
    #deltaLst = [postingList[y]-postingList[y-1]-1 if y != 0 else postingList[y] for y in range(len(postingList))]
    while i < len(postingList):
        #print(countBytes)
        if (len(postingList[i::]) >= 28 and max(postingList[i:i+28]) <= 1):
            i+=28
        elif (len(postingList[i::]) >= 14 and max(postingList[i:i+14]) <= 3):
            i+=14
        elif (len(postingList[i::]) >= 9 and max(postingList[i:i+9]) <= 7):
            i+=9
        elif (len(postingList[i::]) >= 7 and max(postingList[i:i+7]) <= 15):
            i+=7
        elif (len(postingList[i::]) >= 5 and max(postingList[i:i+5]) <= 31):
            i+=5
        elif (len(postingList[i::]) >= 4 and max(postingList[i:i+4]) <= 127):
            i+=4
        elif (len(postingList[i::]) >= 3 and max(postingList[i:i+3]) <= 511):
            i+=3
        elif (len(postingList[i::]) >= 2 and max(postingList[i:i+2]) <= 16383):
            i+=2 
        else: #assuming all numbers are less than 268435456 (2^28)
            i+=1 
        countBytes+=4 
    return countBytes 
                 
    
def blockSizePFD(postingList, bstr,index): 
    #Assume Block Size of 128 Integers)
    offsetCount = 0 
    offset = []
    higherBits = []
    for y in range (index,index+128):
        if (postingList[index] > 2^bstr -1):
            shiftNum = postingList[index] >> bstr
            higherBits.append(shiftNum) 
            offset.append(offsetCount+1)
            offsetCount = 0
        else:
            offsetCount += 1 
    return (Simple9(higherBits)+Simple9(offset)+bstr*16) #divide 128 by 8 for bytes 
    
def OptPFD(postingList): 
    bstrVals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,16, 20, 32]
    countBytes = 0 
    i = 0
    while i < len(postingList):
        print(len(postingList))
        print(countBytes)
        byteSizes = [] 
        for bstr in bstrVals:
            byteSizes.append(blockSizePFD(postingList,bstr,i))
        countBytes += min(byteSizes)
        i += 128
    return countBytes 
         
                 
for i, docs in enumerate(InvertedIndex("/home/josh/output/output.url.inv")):
    print(i, docs)
