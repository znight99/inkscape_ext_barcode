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

import GenericGFPoly

AZTEC_DATA_12 = 1; #// x^12 + x^6 + x^5 + x^3 + 1
AZTEC_DATA_10 = 2; #// x^10 + x^3 + 1
AZTEC_DATA_8 = 3; #// x^8 + x^5 + x^3 + x^2 + 1
AZTEC_DATA_6 = 4; #// x^6 + x + 1
AZTEC_PARAM = 5; #// x^4 + x + 1

class GenericGF:

    #private $expTable;
    #private $logTable;
    #private $primitive;
    #private $size;
    #private $generatorBase;

    def __init__(self,primitive, size, generatorBase):
        self.primitive = primitive;
        self.size = size;
        self.generatorBase = generatorBase;

        self.initialize();

    @staticmethod
    def getInstance(type):
        if type==AZTEC_DATA_12:
                return GenericGF(0x1069, 4096, 1);
        elif type==AZTEC_DATA_10:
                return GenericGF(0x409, 1024, 1);
        elif type==AZTEC_DATA_8:
                return GenericGF(0x012D, 256, 1);
        elif type==AZTEC_DATA_6:
                return GenericGF(0x43, 64, 1);
        elif type==AZTEC_PARAM:
                return GenericGF(0x13, 16, 1);
        else:
                raise ValueError('No such type defined');

    def initialize(self):
        self.expTable = [0] *self.size;
        self.logTable = [0]* self.size;
        x = 1;
        for i in range( 0, self.size) :
            self.expTable[i] = x;
            x <<= 1;
            if (x >= self.size) :
                x ^= self.primitive;
                x &= (self.size - 1);
        for i in range( 0, self.size) :
            self.logTable[self.expTable[i]] = i;

    def exp(self,a):
        return self.expTable[a];

    def log(self,a):
        if (a == 0) :
            raise ValueError();

        return self.logTable[a];

    def multiply(self,a, b):
        if (a == 0 or b == 0) :
            return 0;

        return self.expTable[(self.logTable[a] + self.logTable[b]) % (self.size - 1)];

    def inverse(self,a):
        if (a == 0) :
            raise ValueError();

        return self.expTable[(self.size - self.logTable[a] - 1)];

    def buildMonomial(self,degree, coefficient):
        if (degree < 0) :
            raise ValueError();
        
        if (coefficient == 0) :
            return self.getZero();

        coefficients = [0]*(degree + 1);
        coefficients[0] = coefficient;

        return GenericGFPoly.GenericGFPoly(self, coefficients);

    def getSize(self):
        return self.size;

    def getGeneratorBase(self):
        return self.generatorBase;

    def getZero(self):
        return GenericGFPoly.GenericGFPoly(self, [0]);

    @staticmethod
    def addOrSubtract(a, b):
        if (not isinstance(a,int) or not isinstance(b,int)) :
            raise TypeError('Can not add or substract non-integers');

        return a ^ b;
