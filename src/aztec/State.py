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

import Token
import DynamicDataEncoder
import BitArray

class State:
    #private $mode;
    #private $token;
    #private $shiftByteCount;
    #private $bitCount;

    def __init__(self,token, mode, binaryBytes, bitCount):
        self.token = token;
        self.mode = mode;
        self.shiftByteCount = binaryBytes;
        self.bitCount = bitCount;

    def getMode(self):
        return self.mode;

    def getToken(self):
        return self.token;

    def getBinaryShiftByteCount(self):
        return self.shiftByteCount;

    def getBitCount(self):
        return self.bitCount;

    @staticmethod
    def createInitialState():
        return State(Token.Token.createEmpty(), DynamicDataEncoder.MODE_UPPER, 0, 0);

    def latchAndAppend(self,mode, value):
        bitCount = self.bitCount;
        token = self.token;
        if (mode != self.mode) :
            latch = DynamicDataEncoder.DynamicDataEncoder.getLatch(self.mode, mode);
            token = token.add((latch & 0xFFFF), (latch >> 16));
            bitCount += (latch >> 16);
        latchModeBitCount = (4 if mode == DynamicDataEncoder.MODE_DIGIT else 5);
        token = token.add(value, latchModeBitCount);

        return State(token, mode, 0, bitCount + latchModeBitCount);

    def shiftAndAppend(self,mode, value):
        token = self.token;
        thisModeBitCount = (4 if self.mode == DynamicDataEncoder.MODE_DIGIT else 5);
        token = token.add(DynamicDataEncoder.DynamicDataEncoder.getShift(self.mode, mode), thisModeBitCount);
        token = token.add(value, 5);

        return State(token, self.mode, 0, self.bitCount + thisModeBitCount + 5);

    def addBinaryShiftChar(self,index):
        token = self.token;
        mode = self.mode;
        bitCount = self.bitCount;
        if (self.mode == DynamicDataEncoder.MODE_PUNCT or self.mode == DynamicDataEncoder.MODE_DIGIT) :
            latch = DynamicDataEncoder.DynamicDataEncoder.getLatch(mode, DynamicDataEncoder.MODE_UPPER);
            token = token.add((latch & 0xFFFF), (latch >> 16));
            bitCount += (latch >> 16);
            mode = DynamicDataEncoder.MODE_UPPER;

        if (self.shiftByteCount == 0 or self.shiftByteCount == 31) :
            deltaBitCount = 18;
        elif (self.shiftByteCount == 62) :
            deltaBitCount = 9;
        else :
            deltaBitCount = 8;
        result = State(token, mode, self.shiftByteCount + 1, bitCount + deltaBitCount);
        if (result.getBinaryShiftByteCount() == (2047 + 31)) :
            result = result.endBinaryShift(index + 1);

        return result;

    def endBinaryShift(self,index):
        if (self.shiftByteCount == 0) :
            return self;
        token = self.token;
        token = token.addBinaryShift(index - self.shiftByteCount, self.shiftByteCount);

        return State(token, self.mode, 0, self.bitCount);

    def isBetterThanOrEqualTo(self,other):
        mySize = self.bitCount + (DynamicDataEncoder.DynamicDataEncoder.getLatch(self.getMode(), other.getMode()) >> 16);
        if (other.getBinaryShiftByteCount() > 0 and (self.getBinaryShiftByteCount() == 0 or self.getBinaryShiftByteCount() > other.getBinaryShiftByteCount())) :
            mySize += 10;

        return (mySize <= other.getBitCount());

    def toBitArray(self,text):
        symbols = [];
        token = self.endBinaryShift(len(text)).getToken();
        while (token != None) :
            symbols.insert(0,token);
            token = token.getPrevious();

        bitArray = BitArray.BitArray();
        for symbol in symbols :
          
            bitArray = symbol.appendTo(bitArray, text);

        return bitArray;
