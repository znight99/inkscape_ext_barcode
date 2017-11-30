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

import DynamicDataEncoder
import BinaryDataEncoder
import GenericGF
import ReedSolomonEncoder
import BitArray

class Encoder:
    DEFAULT_EC_PERCENT = 33;
    LAYERS_COMPACT = 5;
    LAYERS_FULL = 33;

    wordSize = [
         4,  6,  6,  8,  8,  8,  8,  8,  8, 10, 10,
        10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
        10, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12,
      ]

    @staticmethod
    def getBitsPerLayer(layer, full):
        if (full) :
            return (112 + 16 * layer) * layer;
        else :
            return (88 + 16 * layer) * layer;

    @staticmethod
    def bitsToWords(stuffedBits, wordSize, totalWords):
        message = [0]*totalWords
        n = int(stuffedBits.getLength() / wordSize);
        for i in range( 0, n) :
            value = 0;
            for j in range( 0,wordSize) :
                value |=  (1 << (wordSize - j - 1)) if stuffedBits.get(i * wordSize + j) else 0;
            message[i] = value;

        return message;
        
    @staticmethod
    def getGF(wordSize):
        if (wordSize==4) :
                return GenericGF.GenericGF.getInstance(GenericGF.AZTEC_PARAM);
        elif (wordSize==6) :
                return GenericGF.GenericGF.getInstance(GenericGF.AZTEC_DATA_6);
        elif (wordSize==8) :
                return GenericGF.GenericGF.getInstance(GenericGF.AZTEC_DATA_8);
        elif (wordSize==10) :
                return GenericGF.GenericGF.getInstance(GenericGF.AZTEC_DATA_10);
        elif (wordSize==12) :
                return GenericGF.GenericGF.getInstance(GenericGF.AZTEC_DATA_12);
        else:
                return None;

    @staticmethod
    def stuffBits(bits, wordSize):
        out = BitArray.BitArray();

        n = bits.getLength();
        mask = (1 << wordSize) - 2;
        i=0
        while i < n:
            word = 0;
            for j in range( 0, wordSize) :
                if (i + j >= n or bits.get(i + j)) :
                    word |= 1 << (wordSize - 1 - j);
            if ((word & mask) == mask) :
                out.append(word & mask,wordSize);
                i-=1;
            elif ((word & mask) == 0) :
                out.append(word | 1,wordSize);
                i-=1;
            else :
                out.append(word,wordSize);
            i+=wordSize
         
        n = out.getLength();
        remainder = n % wordSize;
        if (remainder != 0) :
            j = 1;
            for i in range( 0, remainder) :
                if (not out.get(n - 1 - i)) :
                    j = 0;
            for i in range( remainder, wordSize - 1) :
                out.append(1);
            out.append(1 if j == 0 else 0);

        return out;

    @staticmethod
    def generateCheckWords(stuffedBits, totalSymbolBits, wordSize):
        messageSizeInWords = int((stuffedBits.getLength() + wordSize - 1) / wordSize);
        for i in range( messageSizeInWords * wordSize - stuffedBits.getLength(), 0,-1) :
            stuffedBits.append(1);
        totalSizeInFullWords = int(totalSymbolBits / wordSize);
        messageWords = Encoder.bitsToWords(stuffedBits, wordSize, totalSizeInFullWords);

        rs = ReedSolomonEncoder.ReedSolomonEncoder(Encoder.getGF(wordSize));
        messageWords = rs.encodePadded(messageWords, totalSizeInFullWords - messageSizeInWords);

        startPad = totalSymbolBits % wordSize;
        messageBits = BitArray.BitArray();
        messageBits.append(0,startPad);

        for messageWord in messageWords :
            messageBits.append(messageWord,wordSize);
            

        return messageBits;

    @staticmethod
    def generateModeMessage(compact, layers, messageSizeInWords):
        modeMessage = BitArray.BitArray()
        if (compact) :
            modeMessage.append(layers - 1,2);
            modeMessage.append(messageSizeInWords - 1, 6);
            modeMessage = Encoder.generateCheckWords(modeMessage, 28, 4);
        else :
            modeMessage.append(layers - 1, 5);
            modeMessage.append(messageSizeInWords - 1,11);
            modeMessage = Encoder.generateCheckWords(modeMessage, 40, 4);

        return modeMessage;


    @staticmethod
    def drawBullsEye(matrix, center, size) :
        for i in range( 0,size, 2) :
            for j in range( center - i,center + i+1) :
                matrix[j][center - i]=1;
                matrix[j][center + i]=1;
                matrix[center - i][j]=1;
                matrix[center + i][j]=1;
        
        matrix[center - size][center - size]=1;
        matrix[center - size + 1][center - size]=1;
        matrix[center - size][center - size + 1]=1;
        matrix[center + size][center - size]=1;
        matrix[center + size][center - size + 1]=1;
        matrix[center + size][center + size - 1]=1;
        
        return matrix;

    @staticmethod
    def drawModeMessage(matrix, compact, matrixSize, modeMessage):
        center = int(matrixSize / 2);
        if (compact) :
            for i in range( 0, 7) :
                if (modeMessage.get(i)) :
                    matrix[center - 3 + i][center - 5]=1;
                if (modeMessage.get(i + 7)) :
                    matrix[center + 5][center - 3 + i]=1;
                if (modeMessage.get(20 - i)):
                    matrix[center - 3 + i][center + 5]=1;
                if (modeMessage.get(27 - i)) :
                    matrix[center - 5][center - 3 + i]=1;
        else :
            for i in range( 0, 10) :
                if (modeMessage.get(i)) :
                    matrix[center - 5 + i+int(i/5)][center - 7]=1;
                if (modeMessage.get(i + 10)) :
                    matrix[center + 7][center - 5 + i +int(i/5)]=1;
                if (modeMessage.get(29 - i)):
                    matrix[center - 5 + i+int(i/5)][center + 7]=1;
                if (modeMessage.get(39 - i)) :
                    matrix[center - 7][center - 5 + i+int(i/5)]=1;

        return matrix;
    
    def __init__(self):
      pass
      
    def encode(self,content, eccPercent=DEFAULT_EC_PERCENT ):
        if (len(content) == 0) :
            return None
            
        dataEncoder = DynamicDataEncoder.DynamicDataEncoder();
        #dataEncoder = BinaryDataEncoder.BinaryDataEncoder();
        bits = dataEncoder.encode(content);

        eccBits = int(bits.getLength() * eccPercent / 100 + 11);
        totalSizeBits = bits.getLength() + eccBits;

        layers = 0;
        wordSize = 0;
        totalSymbolBits = 0;
        stuffedBits = None;
        found=False
        for layers in range( 1, self.LAYERS_COMPACT) :
            if (self.getBitsPerLayer(layers, False) >= totalSizeBits) :
                if (wordSize != self.wordSize[layers]) :
                    wordSize = self.wordSize[layers];
                    stuffedBits = self.stuffBits(bits, wordSize);

                totalSymbolBits = self.getBitsPerLayer(layers, False);
                if (stuffedBits.getLength() + eccBits <= totalSymbolBits) :
                    found=True
                    break;
        compact = True;
        if (not found) :
            compact = False;
            for layers in range( 1, self.LAYERS_FULL) :
                if (self.getBitsPerLayer(layers, True) >= totalSizeBits) :
                    if (wordSize != self.wordSize[layers]) :
                        wordSize = self.wordSize[layers];
                        stuffedBits = self.stuffBits(bits, wordSize);
                    totalSymbolBits = self.getBitsPerLayer(layers, True);
                    if (stuffedBits.getLength() + eccBits <= totalSymbolBits) :
                        found=True
                        break;
        if (not found) :
            return None
            

        messageSizeInWords = int((stuffedBits.getLength() + wordSize - 1) / wordSize);
        for i in range( messageSizeInWords * wordSize -stuffedBits.getLength(),0,-1 ) :
            stuffedBits.append(1)

        #// generate check words
        rs = ReedSolomonEncoder.ReedSolomonEncoder(self.getGF(wordSize));
        
        totalSizeInFullWords = int(totalSymbolBits / wordSize);
        messageWords = self.bitsToWords(stuffedBits, wordSize, totalSizeInFullWords);
        messageWords = rs.encodePadded(messageWords, totalSizeInFullWords - messageSizeInWords);

        #// convert to bit array and pad in the beginning
        startPad = totalSymbolBits % wordSize;
        messageBits = BitArray.BitArray();
        messageBits.append(0,startPad);
        for messageWord in messageWords :
            messageBits.append(messageWord,wordSize);

        #// generate mode message
        modeMessage = self.generateModeMessage(compact, layers, messageSizeInWords);

        #// allocate symbol
        matrixSize=1
        if (compact) :
            baseMatrixSize = 11 + layers * 4;
            matrixSize =baseMatrixSize
            alignmentMap = [i for i in range(0,matrixSize)];
        else :
            baseMatrixSize = 14 + layers * 4;
            matrixSize = baseMatrixSize + 1 + 2 * int((int(baseMatrixSize / 2) - 1) / 15);
            alignmentMap = [0]* baseMatrixSize;
            origCenter = int(baseMatrixSize / 2);
            center = int(matrixSize / 2);
            for i in range( 0, origCenter) :
                newOffset = i + int(i / 15);
                alignmentMap[origCenter - i - 1] = center - newOffset - 1;
                alignmentMap[origCenter + i] = center + newOffset + 1;

        matrix = [ [0 for i in range(matrixSize)] for i in range(matrixSize) ];
 
        #// draw mode and data bits
        rowOffset=0
        for i in range( 0,  layers) :
            if (compact) :
                rowSize = (layers - i) * 4 + 9;
            else :
                rowSize = (layers - i) * 4 + 12;
            
            for j in range( 0, rowSize) :
                columnOffset = j * 2;
                for k in range( 0, 2) :
                    if (messageBits.get(rowOffset + columnOffset + k)) :
                        matrix[alignmentMap[i * 2 + k]][alignmentMap[i * 2 + j]]=1;
                    if (messageBits.get(rowOffset + rowSize * 2 + columnOffset + k)) :
                        matrix[alignmentMap[i * 2 + j]][alignmentMap[baseMatrixSize - 1 - i * 2 - k]]=1;
                    if messageBits.get(rowOffset + rowSize * 4 + columnOffset + k) :
                        matrix[alignmentMap[baseMatrixSize - 1 - i * 2 - k]][alignmentMap[baseMatrixSize - 1 - i * 2 - j]]=1;
                    if messageBits.get(rowOffset + rowSize * 6 + columnOffset + k):
                        matrix[alignmentMap[baseMatrixSize - 1 - i * 2 - j]][alignmentMap[i * 2 + k]]=1;
            rowOffset += rowSize * 8;

        matrix = self.drawModeMessage(matrix, compact, matrixSize, modeMessage);

        #// draw alignment marks
        
        if (compact) :
            matrix = self.drawBullsEye(matrix, int(matrixSize / 2), 5);
        else:
            matrix = self.drawBullsEye(matrix, int(matrixSize / 2), 7);
            j=0
            for i in range( 0,  int(baseMatrixSize / 2) - 1, 15) :
                for k in range( int(matrixSize / 2) & 1, matrixSize,2) :
                    matrix[int(matrixSize / 2) - j][k]=1;
                    matrix[int(matrixSize / 2) + j][k]=1;
                    matrix[k][ int(matrixSize / 2) - j]=1;
                    matrix[k][ int(matrixSize / 2) + j]=1;
                j+=16

        return matrix;
