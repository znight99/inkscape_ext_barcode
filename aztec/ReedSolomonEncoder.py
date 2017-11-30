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

class ReedSolomonEncoder:
    #private $field;
    #private $cachedGenerators;

    def __init__(self,field):
        self.field = field;
        self.cachedGenerators = [];
        self.cachedGenerators+=[ GenericGFPoly.GenericGFPoly(field, [1])];


    def buildGenerator(self,degree):
        if (degree >= len(self.cachedGenerators)) :
            lastGenerator = self.cachedGenerators[-1];
            for d in range( len(self.cachedGenerators), degree+1) :
                nextCoefficent = self.field.exp(d - 1 + self.field.getGeneratorBase());
                nextGenerator = lastGenerator.multiply(GenericGFPoly.GenericGFPoly(self.field, [1, nextCoefficent]));
                self.cachedGenerators.append(nextGenerator);
                lastGenerator = nextGenerator;

        return self.cachedGenerators[degree];

    def encode(self,data, ecBytes):
        if (ecBytes == 0) :
            raise ValueError('No error correction bytes');
        if (len(data) == 0) :
            raise ValueError('No data bytes provided');

        generator = self.buildGenerator(ecBytes);
        info = GenericGFPoly.GenericGFPoly(self.field, data);
        info = info.multiplyByMonomial(ecBytes, 1);

        remainder = info.divide(generator).getRemainder();
        coefficients = remainder.getCoefficients();
        for i in range(ecBytes-len(coefficients)):
          coefficients.insert(0,0)
        paddedCoefficients=coefficients;

        return data+ paddedCoefficients;

    def encodePadded(self,paddedData, ecBytes):
        dataLength = len(paddedData) - ecBytes;

        return self.encode(paddedData[0:dataLength], ecBytes);
