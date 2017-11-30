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

class Token:
    #private $previous;
    #private $totalBitCount;

    def __init__(self,previous , totalBitCount):
        self.previous = previous;
        self.totalBitCount = totalBitCount;

    def getPrevious(self):
        return self.previous;

    def getTotalBitCount(self):
        return self.totalBitCount;

    def add(self,value, bitCount):
        return SimpleToken(self, self.totalBitCount + bitCount, value, bitCount);

    def addBinaryShift(self,start, byteCount):
        bitCount = (byteCount * 8);
        if (byteCount <= 31) :
            bitCount += 10;
        elif (byteCount <= 62) :
            bitCount += 20;
        else :
            bitCount += 21;

        return BinaryShiftToken(self, self.totalBitCount + bitCount, start, byteCount);

    @staticmethod
    def createEmpty():
        return SimpleToken(None, 0, 0, 0);

    def appendTo(self,bitArray, text):
        pass

class BinaryShiftToken(Token):
    #private $shiftStart;
    #private $shiftByteCount;

    def __init__(self,previous, totalBitCount, shiftStart, shiftByteCount):
        Token.__init__(self,previous, totalBitCount);
        self.shiftStart = shiftStart;
        self.shiftByteCount = shiftByteCount;

    def appendTo(self,bitArray, text):
        for i in range( 0, self.shiftByteCount) :
            if (i == 0 or (i == 31 and self.shiftByteCount <= 62)) :
                bitArray.append(31, 5);
                if (self.shiftByteCount > 62) :
                    bitArray.append(self.shiftByteCount - 31, 16);
                elif (i == 0) :
                    bitArray.append(min(self.shiftByteCount, 31), 5);
                else:
                    bitArray.append(self.shiftByteCount - 31, 5);
            bitArray.append(ord(text[self.shiftStart + i]), 8);

        return bitArray;

class SimpleToken (Token):
    #private $value;
    #private $bitCount;

    def __init__(self,previous, totalBitCount, value, bitCount):
        Token.__init__(self,previous, totalBitCount);
        self.value = value;
        self.bitCount = bitCount;

    def appendTo(self,bitArray, text):
        bitArray.append(self.value, self.bitCount);

        return bitArray;

