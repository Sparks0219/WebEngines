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
                bytes = Simple9(postingList)
                f.write(str(size)+" "+str(self.docs[1])+" "+str(bytes)+"\n")
                print(str(size)+" "+str(self.docs[1])+" "+str(bytes)+"\n")
                #partitions(newList,postingList[9999]-postingList[0],f)
            i += size+1
        f.close()
        
    def __next__(self):
        return self
    
def partitions(postingList,range,file):
    if len(postingList) == 0:
        return
    if len(postingList) <= 10:
         bytes = GammaEncoding(postingList)
         file.write(str(len(postingList))+" "+str(range)+" "+str(bytes)+"\n")
         print(postingList)
         print(str(len(postingList))+" "+str(range)+" "+str(bytes))
         return 
    bytes = Simple9(postingList)
    file.write(str(len(postingList))+" "+str(range)+" "+str(bytes)+"\n")
    target = np.searchsorted(postingList,range//2+postingList[0])
    print(postingList)
    print(str(len(postingList))+" "+str(range)+" "+str(bytes))
    partitions(postingList[:target],range//2,file)
    partitions(postingList[target:],np.ceil(range/2),file)
    
    
    
    
    
def GammaEncoding(postingList):
    last = 0 
    countBits =  2*(np.floor(np.log2(postingList[0])).astype(int))+1
    i = 0
    while i < len(postingList):
        #print(countBits)
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
    return True
        
    
def Simple9(postingList):
    i = 0 
    countBytes = 0
    newList = np.copy(postingList[:10000])
    for y in range(len(newList)):
        if (y!=0):
            newList[y] = postingList[y]-postingList[y-1]-1
            #print(newList[y])
    while i < len(newList):
        if (len(newList)-1-i >= 28 and myMax(i,28,1,newList) == True):
            #print("CASE 1")
            i+=28
        elif (len(newList)-1-i >= 14 and myMax(i,14,3,newList) == True):
            #print("CASE 2")
            i+=14
        elif (len(newList)-1-i >= 9 and myMax(i,9,7,newList) == True):
            #print("CASE 3")
            i+=9
        elif (len(newList)-1-i >= 7 and myMax(i,7,15,newList) == True):
            #print("CASE 4")
            i+=7
        elif (len(newList)-1-i >= 5 and myMax(i,5,31,newList) == True):
            #print("CASE 5")
            i+=5
        elif (len(newList)-1-i >= 4 and myMax(i,4,127,newList) == True):
            #print("CASE 6")
            i+=4
        elif (len(newList)-1-i >= 3 and myMax(i,3,511,newList) == True):
            #print("CASE 7")
            i+=3
        elif (len(newList)-1-i >= 2 and myMax(i,2,16383,newList) == True):
            #print("CASE 8")
            i+=2 
        else: #assuming all numbers are less than 268435456 (2^28)
            #print("CASE 9")
            i+=1 
        countBytes+=4
#     print(countBytes)
    return countBytes 

#S9 One Sweep Version 
def Simple9OneSweep(postingList):
    i = 0 
    counter = 0
    currentCase = 1
    countBytes = 0
    newList = np.copy(postingList[:10000])
    cases = {1:(28,1), 2:(14,3) ,3:(9,7) ,4:(7,15) ,5:(5,31) , 6:(4,127) , 7:(3,511) , 8:(2,16383) , 9:(1,268435455)}
    for y in range(len(newList)):
        if (y!=0):
            newList[y] = postingList[y]-postingList[y-1]-1
    while i < len(newList):
        #If a value that cannot be fit in the current case appears, goes to a higher case that can process it
        if newList[i] > cases[currentCase][1]:
            while newList[i] > cases[currentCase][1]:
                currentCase+=1
                #If we go to a higher case, then the elements we have already been processed can be fit into a smaller case 
                #(i.e. going from 28 -> 14, already covered 16 elements)
                if (counter >= cases[currentCase][0]):
                    #print("CASE "+str(currentCase))
                    counter -= cases[currentCase][0]
                    countBytes += 4 
        counter+=1 
        #If we have covered sufficient elements for our current case, then start again 
        if (counter == cases[currentCase][0]):
            #print("CASE "+str(currentCase))
            countBytes += 4
            currentCase = 1 
            counter = 0
        i += 1
#         print(counter)
    if (counter != 0):
        countBytes += 4
    print(countBytes)
    return countBytes 

#Helper function for OptPFD, computes the cost for a certain bstrVal
def blockSizePFD(postingList, bstr,index): 
    #Assume Block Size of 128 Integers)
    offsetCount = 0
    #Uses offset to store where overflow values appear
    offset = []
    #Uses higherBits to store the actual bits that overflowed
    higherBits = []
    #For each chunk of 128 integers
    for y in range (index,min(index+128,len(postingList))):
        #Case where an overflow occurs
        if (postingList[y] > 2**bstr -1):
            shiftNum = postingList[y] >> bstr
            higherBits.append(shiftNum) 
            offset.append(offsetCount)
            offsetCount = 0
        else:   
            offsetCount += 1 
    return (Simple9(higherBits)+Simple9(offset)+bstr*16) #divide 128 by 8 for bytes 

#Main OptPFD function, after computing the cost for all bstrVals, picks the optimal one 
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
        #Uses a temporary list to hold the byte size cost using each bstrVals 
        byteSizes = [] 
        for bstr in bstrVals:
            byteSizes.append(blockSizePFD(newList,bstr,i))
        #Picks the optimal one to use
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
