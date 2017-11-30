'''
 * Copyright 2013 Metzli and ZXing authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

class BitArray:
    #private data;

    def __init__(self,length = 0):
        self.data = [];
        self.resize(length);

    def resize(self,length):
        if (length > len(self.data)) :
            self.data += [0]*(length-len(self.data));
        elif (length < len(self.data)) :
            self.data = self.data[ 0:length];

    def getLength(self):
        return len(self.data);

    def get(self,index):
        self.checkIndex(index);

        return self.data[index];

    def tryGet(self,index):
        if (index < 0 or index >= len(self.data)) :
            return 0;
        else :
            return self.data[index];

    def set(self,index, bit = 1):
        self.checkIndex(index);
        self.data[index] = (bit & 1);

    def flip(self,index):
        self.checkIndex(index);
        self.data[index] = (1 - self.data[index]);

    def clear(self):
        for i in range( len(self.data)) :
            self.data[i] = 0;

    def append(self,data, bits = 1):
        for i in range( bits - 1,-1,-1) :
            self.data .append( (data >> i) & 1);

    def appendBytes(self,bytes):
        for i in range( 0, len(bytes)) :
            self.append(ord(bytes[i]), 8);

    def asArray(self):
        return self.data;


    def checkIndex(self,index):
        if (index < 0 or index >= len(self.data)) :
            raise IndexError();

    def asDWArray(self):
        a=[]
        for i in range(0,len(self.data),32):
          w=0
          for j in range(31,-1,-1):
            w<<=1
            if (i+j<len(self.data) and self.data[i+j]):
              w|=1
          a.append(w)
        return a