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

import GenericGF
import DivisionResult

class GenericGFPoly:
    #private $field;
    #private $coefficients;

    def __init__(self,field, coefficients):
        if (len(coefficients) == 0) :
            raise ValueError();

        self.field = field;

        self.coefficients=coefficients
        while (len(self.coefficients)>0 and self.coefficients[0] == 0) :
            self.coefficients=self.coefficients[1:];
        if (len(self.coefficients)<=0) :
            self.coefficients = [0];

    def getField(self):
        return self.field;

    def getCoefficients(self):
        return self.coefficients;

    def getDegree(self):
        return len(self.coefficients) - 1;

    def isZero(self):
        return (self.coefficients[0] == 0);

    def getCoefficient(self,degree):
        return self.coefficients[len(self.coefficients) - 1 - degree];

    def addOrSubtract(self,other):
        if (other.getField() != self.field) :
            raise ValueError('GenericGFPolys do not have same GenericGF field');
        if (self.isZero()) :
            return other;
        if (other.isZero()) :
            return self;

        smallerCoefficients = self.getCoefficients();
        largerCoefficients = other.getCoefficients();
        if (len(smallerCoefficients) > len(largerCoefficients)) :
            (smallerCoefficients, largerCoefficients) = (largerCoefficients, smallerCoefficients);

        lengthDiff = len(largerCoefficients) - len(smallerCoefficients);
        sumDiff = largerCoefficients[0: lengthDiff]+[0]*(len(smallerCoefficients));

        for i in range( lengthDiff, len(largerCoefficients)) :
            sumDiff[i] = GenericGF.GenericGF.addOrSubtract(smallerCoefficients[i - lengthDiff], largerCoefficients[i]);

        return GenericGFPoly(self.field, sumDiff);

    def multiply(self,other):
        if (other.getField() != self.field) :
            raise ValueError('GenericGFPolys do not have same GenericGF field');
        if (self.isZero() or other.isZero()) :
            return self.field.getZero();

        aCoefficients = self.getCoefficients();
        aLength = len(aCoefficients);
        bCoefficients = other.getCoefficients();
        bLength = len(bCoefficients);
        product = [0]*(aLength + bLength - 1);

        for i in range( 0, aLength) :
            aCoeff = aCoefficients[i];
            for j in range(0,bLength) :
                product[i + j] = GenericGF.GenericGF.addOrSubtract(product[i + j], self.field.multiply(aCoeff, bCoefficients[j]));

        return GenericGFPoly(self.field, product);

    def multiplyByMonomial(self,degree, coefficient):
        if (degree < 0) :
            raise ValueError();
        if (coefficient == 0) :
            return self.field.getZero();

        product = [0]*(len(self.coefficients) + degree);
        for i in range( 0, len(self.coefficients)) :
            product[i] = self.field.multiply(self.coefficients[i], coefficient);

        return GenericGFPoly(self.field, product);

    def divide(self,other):
        if (other.getField() != self.field) :
            raise ValueError('GenericGFPolys do not have same GenericGF field');
        if (other.isZero()) :
            raise ValueError('Divide by 0');

        quotient = self.field.getZero();
        remainder = self;

        denominatorLeadingTerm = other.getCoefficient(other.getDegree());
        inverseDenominatorLeadingTerm = self.field.inverse(denominatorLeadingTerm);
        while (remainder.getDegree() >= other.getDegree() and not remainder.isZero()) :
            degreeDifference = remainder.getDegree() - other.getDegree();
            scale = self.field.multiply(remainder.getCoefficient(remainder.getDegree()), inverseDenominatorLeadingTerm);
            term = other.multiplyByMonomial(degreeDifference, scale);
            iterationQuotient = self.field.buildMonomial(degreeDifference, scale);
            quotient = quotient.addOrSubtract(iterationQuotient);
            remainder = remainder.addOrSubtract(term);

        return DivisionResult.DivisionResult(quotient, remainder);
