import os
import numpy as np

class InvertedIndex:
    def __init__(self, index_name):
        index_dir = os.path.join(index_name)
        self.docs = np.memmap(index_name + ".docs", dtype=np.uint32, mode='r')
    def __iter__(self):
        i = 2
        f = open("invData.txt", "w")
        while i < len(self.docs):
            size = self.docs[i]
            if size >= 10000:
                postingList = self.docs[i+1:size+i+1]
                newList = np.copy(postingList[:10000])
                #bytes = ipc(self.docs[i+1:size+i+1],size,self.docs[i+1],self.docs[size+i])
#                 bytes = Simple9(self.docs[i+1:size+i+1])
#                 f.write(str(size)+" "+str(self.docs[1])+" "+str(bytes)+"\n")
#                 print(str(size)+" "+str(self.docs[1])+" "+str(bytes)+"\n")
                #partitions(self.docs[i+1:size+i+1],self.docs[1],f)
                partitions(newList,postingList[9999]-postingList[0],f)
            #Three tuple containing range, size of posting list, encoding
            #(self.docs[size+i]-self.docs[i],size,SomeEncoding(self.docs[i+1:size+i+1]))
            #print(self.docs[1])
            i += size+1
        f.close()
        
    def __next__(self):
        return self
    
def partitions(postingList,range,file):
    if len(postingList) <= 10:
         bytes = GammaEncoding(postingList)
         file.write(str(len(postingList))+" "+str(range)+" "+str(bytes)+"\n")
         print(str(len(postingList))+" "+str(range)+" "+str(bytes)+"\n")
         return 
    bytes = Simple9(postingList)
    file.write(str(len(postingList))+" "+str(range)+" "+str(bytes)+"\n")
    print(str(len(postingList))+" "+str(range)+" "+str(bytes)+"\n")
    target = np.searchsorted(postingList,range/2)
    print(target)
    partitions(postingList[:target],range//2,file)
    partitions(postingList[target:],range//2,file)
    
    
    
    
    
def GammaEncoding(postingList):
    last = 0 
    countBits =  2*(np.floor(np.log2(postingList[0])).astype(int))+1
    i = 0
    while i < len(postingList):
        print(countBits)
        current = postingList[i]
        delta = current - last
        last = current
        countBits += 2*(np.floor(np.log2(delta)).astype(int))+1
        i +=1
    return np.ceil(countBits/8)

def VarByteEncoding(postingList):
    last = 0 
    countBytes = 0
    i = 0
    while i < len(postingList):
        #print(countBytes)
        current = postingList[i]
        delta = current - last - 1 
        last = current
        while delta >= 128: 
            delta = delta//128
            countBytes += 1
        countBytes += 1
        i +=1
    return countBytes
        
def myMax(begin,blockSize,target,list):
    for i in range(blockSize):
        if list[begin+i] > target:
            return False
        else:
            return True
    
def Simple9(postingList):
    i = 0 
    countBytes = 0
    newList = np.copy(postingList)
    for y in range(len(newList)):
        if (y!=0):
            newList[y] = postingList[y]-postingList[y-1]-1
#             print(newList[y])
    while i < len(newList):
        #print(countBytes)
        if (len(postingList)-1-i >= 28 and myMax(i,28,1,newList) == True):
            i+=28
        elif (len(postingList)-1-i >= 14 and myMax(i,14,3,newList) == True):
            i+=14
        elif (len(postingList)-1-i >= 9 and myMax(i,9,7,newList) == True):
            i+=9
        elif (len(postingList)-1-i >= 7 and myMax(i,7,15,newList) == True):
            i+=7
        elif (len(postingList)-1-i >= 5 and myMax(i,5,31,newList) == True):
            i+=5
        elif (len(postingList)-1-i >= 4 and myMax(i,4,127,newList) == True):
            i+=4
        elif (len(postingList)-1-i >= 3 and myMax(i,3,511,newList) == True):
            i+=3
        elif (len(postingList)-1-i >= 2 and myMax(i,2,16383,newList) == True):
            i+=2 
        else: #assuming all numbers are less than 268435456 (2^28)
            i+=1 
        countBytes+=4
    print(countBytes)
    return countBytes 
                 
def Simple9OneSweep(postingList):
    i = 0 
    counter = 0
    currentCase = 1
    countBytes = 0
    newList = np.copy(postingList[:10000])
    cases = {1:(28,1), 2:(14,3) ,3:(9,7) ,4:(7,15) ,5:(7,15) ,6:(5,31) , 7:(4,127) , 8:(3,511) , 9:(2,16383) , 10:(1,268435455)}
    for y in range(len(newList)):
        if (y!=0):
            newList[y] = postingList[y]-postingList[y-1]-1
    while i < len(newList):
        #print(countBytes)
        if newList[i] > cases[currentCase][1]:
            while newList[i] > cases[currentCase][1]:
                currentCase+=1
                if (counter >= cases[currentCase][0]):
                    counter -= cases[currentCase][0]
                    countBytes += 4 
        counter+=1 
        if (counter == cases[currentCase][0]):
            countBytes += 4
            currentCase = 1 
            counter = 0
        i += 1
#         print(counter)
    if (counter != 0):
        countBytes += 4
    print(countBytes)
    return countBytes 
def blockSizePFD(postingList, bstr,index): 
    #Assume Block Size of 128 Integers)
    offsetCount = 0 #in case the first number in postingList overflows 
    offset = []
    higherBits = []
    for y in range (index,min(index+128,len(postingList))):
        if (postingList[y] > 2**bstr -1):
            shiftNum = postingList[y] >> bstr
            higherBits.append(shiftNum) 
            offset.append(offsetCount)
            offsetCount = 0
        else:
            offsetCount += 1 
    return (Simple9(higherBits)+Simple9(offset)+bstr*16) #divide 128 by 8 for bytes 
    
def OptPFD(postingList): 
    bstrVals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,16, 20, 32]
    countBytes = 0 
    i = 0
    newList = np.copy(postingList)
    for y in range(len(postingList)):
        if (y!=0):
            newList[y] = postingList[y]-postingList[y-1]-1
    while i < len(postingList):
        print(countBytes)
        byteSizes = [] 
        for bstr in bstrVals:
            byteSizes.append(blockSizePFD(newList,bstr,i))
        countBytes += min(byteSizes)
        print(byteSizes)
        i += 128
    return countBytes 
        
    
#returns number of bits needed to IP encode numbers in array recursively */

#def ipc(postingList,  num,  low,  high):
#    print(len(postingList))
#    if (num == 0):
#        return(0)
#    mid = num//2
#    n = high-low-num-1
#    x = postingList[mid]-low-mid-1
#    c = nBits(n, x)
#    list1 = np.copy(postingList[::mid+1])
#    list2 = np.copy(postingList[mid+1::])
#    return(c+ipc(list1, len(list1), low, postingList[mid]) + ipc(list2, len(list2), postingList[mid], high))

#returns number of bits needed for an integer x known to be at most n */
#def nBits(n, x):
#    i = (n+1)//2;
#    x = 2*(x-i) if (x >= i) else 2*(i-x)-1
#    i = 1
#    j = 0
#    while (i <= n):
#        j+=1
#        i<<=1            
#    if ((j > 0) and (x < i-1-n)):
#        j-=1
#    return(j)
                    
for i, docs in enumerate(InvertedIndex("/home/josh/output/output.url.inv")):
    print(i, docs)
