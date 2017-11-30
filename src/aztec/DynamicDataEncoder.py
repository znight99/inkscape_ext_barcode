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

import State
import Token

MODE_UPPER = 0;
MODE_LOWER = 1;
MODE_DIGIT = 2;
MODE_MIXED = 3;
MODE_PUNCT = 4;

class DynamicDataEncoder :


    shiftTable = None;
    latchTable = None;
    charMap = None;
    modeNames = ['UPPER', 'LOWER', 'DIGIT', 'MIXED', 'PUNCT'];

    def __init__(self):
      pass
      
    def encode(self,data):
        text = [ d for d in data ];
        states = [State.State.createInitialState()];
        for index in range( 0, len(text)) :
            nextChar = (text[index + 1] if (index + 1 < len(text)) else  '');
            if text[index]=='\r':
                    pairCode = (2 if (nextChar == '\n') else 0);
            elif text[index]=='.':
                    pairCode = (3 if (nextChar == ' ') else 0);
            elif text[index]==',':
                    pairCode = (4 if (nextChar == ' ') else 0);
            elif text[index]==':':
                    pairCode = (5 if (nextChar == ' ') else 0);
            else:
                    pairCode = 0;
            if (pairCode > 0) :
                states = self.updateStateListForPair(states, index, pairCode);
                index+=1;
            else :
                states = self.updateStateListForChar(states, index, text);

        minState = states[0];
        for state in states:
            if (state.getBitCount() < minState.getBitCount()) :
                minState = state;

        return minState.toBitArray(text);

    @staticmethod
    def updateStateListForChar(states, index, text):
        result = [];
        for state in states :
            result = DynamicDataEncoder.updateStateForChar(state, index, text, result);

        return DynamicDataEncoder.simplifyStates(result);

    @staticmethod
    def updateStateForChar(state, index, text, result = []):
        ch = text[index];
        charInCurrentTable = (DynamicDataEncoder.getCharMapping(state.getMode(), ch) > 0);
        stateNoBinary = None;
        for mode in range( 0, MODE_PUNCT+1) :
            charInMode = DynamicDataEncoder.getCharMapping(mode, ch);
            if (charInMode > 0) :
                if (stateNoBinary == None) :
                    stateNoBinary = state.endBinaryShift(index);
                if (not charInCurrentTable or mode == state.getMode() or mode == MODE_DIGIT) :
                    result .append( stateNoBinary.latchAndAppend(mode, charInMode));
                if ( not charInCurrentTable and DynamicDataEncoder.getShift(state.getMode(), mode) >= 0) :
                    result.append( stateNoBinary.shiftAndAppend(mode, charInMode));
        if (state.getBinaryShiftByteCount() > 0 or DynamicDataEncoder.getCharMapping(state.getMode(), ch) == 0) :
            result.append( state.addBinaryShiftChar(index));

        return result;

    @staticmethod
    def updateStateListForPair(states, index, pairCode):
        result = [];
        for state in states :
            result = DynamicDataEncoder.updateStateForPair(state, index, pairCode, result);

        return DynamicDataEncoder.simplifyStates(result);

    @staticmethod
    def updateStateForPair(state, index, pairCode, result = []):
        stateNoBinary = state.endBinaryShift(index);

        result.append( stateNoBinary.latchAndAppend(MODE_PUNCT, pairCode));
        if (state.getMode() != MODE_PUNCT) :
            result.append( stateNoBinary.shiftAndAppend(MODE_PUNCT, pairCode));
        if (pairCode == 3 or pairCode == 4) :
            result.append( stateNoBinary.latchAndAppend(MODE_DIGIT, 16 - pairCode).latchAndAppend(MODE_DIGIT, 1));
        if (state.getBinaryShiftByteCount() > 0) :
            result.append( state.addBinaryShiftChar(index).addBinaryShiftChar(index + 1));

        return result;

    @staticmethod
    def simplifyStates(states):
        result = [];
        for newState in states :
            add = True;
            removeList=[]
            for i in range( 0, len(result)) :
                if (result[i].isBetterThanOrEqualTo(newState)) :
                    add = False;
                    break;
                if (newState.isBetterThanOrEqualTo(result[i])) :
                    removeList.append(i)
            if (add) :
                result.append( newState);
            for i in range(len(removeList)-1,-1,-1):
                result=result[0:i]+result[i+1:]
        return result;

    @staticmethod
    def getModeName(mode):
        return DynamicDataEncoder.modeNames[mode];

    @staticmethod
    def getLatch(fromMode, toMode):
        if (None == DynamicDataEncoder.latchTable) :
            DynamicDataEncoder.latchTable = [
                [
                    0,
                    (5 << 16) + 28,                          #// UPPER -> LOWER
                    (5 << 16) + 30,                           #// UPPER -> DIGIT
                    (5 << 16) + 29,                           #// UPPER -> MIXED
                    (10 << 16) + (29 << 5) + 30,              #// UPPER -> MIXED -> PUNCT
                ], [
                    (9 << 16) + (30 << 4) + 14,               #// LOWER -> DIGIT -> UPPER
                    0,
                    (5 << 16) + 30,                           #// LOWER -> DIGIT
                    (5 << 16) + 29,                           #// LOWER -> MIXED
                    (10 << 16) + (29 << 5) + 30,              #// LOWER -> MIXED -> PUNCT
                ], [
                    (4 << 16) + 14,                           #// DIGIT -> UPPER
                    (9 << 16) + (14 << 5) + 28,               #// DIGIT -> UPPER -> LOWER
                    0,
                    (9 << 16) + (14 << 5) + 29,               #// DIGIT -> UPPER -> MIXED
                    (14 << 16) + (14 << 10) + (29 << 5) + 30, #// DIGIT -> UPPER -> MIXED -> PUNCT
                ], [
                    (5 << 16) + 29,                           #// MIXED -> UPPER
                    (5 << 16) + 28,                           #// MIXED -> LOWER
                    (10 << 16) + (29 << 5) + 30,              #// MIXED -> UPPER -> DIGIT
                    0,
                    (5 << 16) + 30,                           #// MIXED -> PUNCT
                ], [
                    (5 << 16) + 31,                           #// PUNCT -> UPPER
                    (10 << 16) + (31 << 5) + 28,              #// PUNCT -> UPPER -> LOWER
                    (10 << 16) + (31 << 5) + 30,              #// PUNCT -> UPPER -> DIGIT
                    (10 << 16) + (31 << 5) + 29,              #// PUNCT -> UPPER -> MIXED
                    0,
                ] ]

        return DynamicDataEncoder.latchTable[fromMode][toMode];

    @staticmethod
    def getShift(fromMode, toMode):
        if (None == DynamicDataEncoder.shiftTable) :
            DynamicDataEncoder.shiftTable = [ [-1 for i in range(6)] for i in range(6)]
            DynamicDataEncoder.shiftTable[MODE_UPPER][MODE_PUNCT] = 0;
            DynamicDataEncoder.shiftTable[MODE_LOWER][MODE_PUNCT] = 0;
            DynamicDataEncoder.shiftTable[MODE_LOWER][MODE_UPPER] = 28;

            DynamicDataEncoder.shiftTable[MODE_MIXED][MODE_PUNCT] = 0;

            DynamicDataEncoder.shiftTable[MODE_DIGIT][MODE_PUNCT] = 0;
            DynamicDataEncoder.shiftTable[MODE_DIGIT][MODE_UPPER] = 15;

        return DynamicDataEncoder.shiftTable[fromMode][toMode];

    @staticmethod
    def getCharMapping(mode, char):
        if (None == DynamicDataEncoder.charMap) :
            DynamicDataEncoder.charMap = [[0 for i in range(256)] for i in range(5)];

            DynamicDataEncoder.charMap[MODE_UPPER][ord(' ')] = 1;
            for c in range( ord('A'), ord('Z')+1) :
                DynamicDataEncoder.charMap[MODE_UPPER][c] = (c - ord('A') + 2);

            DynamicDataEncoder.charMap[MODE_LOWER][ord(' ')] = 1;
            for c in range( ord('a'), ord('z')+1) :
                DynamicDataEncoder.charMap[MODE_LOWER][c] = (c - ord('a') + 2);

            DynamicDataEncoder.charMap[MODE_DIGIT][ord(' ')] = 1;
            for c in range( ord('0'), ord('9')+1) :
                DynamicDataEncoder.charMap[MODE_DIGIT][c] = (c - ord('0') + 2);
            DynamicDataEncoder.charMap[MODE_DIGIT][ord(',')] = 12;
            DynamicDataEncoder.charMap[MODE_DIGIT][ord('.')] = 13;

            mixedTable = [
                '\0', ' ', '\1', '\2', '\3', '\4', '\5', '\6', '\7', '\b', '\t', '\n',
                '\13', '\f', '\r', '\33', '\34', '\35', '\36', '\37', '@', '\\', '^',
                '_', '`', '|', '~', '\177',
              ]
            for i in range( 0, len(mixedTable)) :
                DynamicDataEncoder.charMap[MODE_MIXED][ord(mixedTable[i])] = i;

            punctTable = [
                '\0', '\r', '\0', '\0', '\0', '\0', '!', '\'', '#', '$', '%', '&', '\'',
                '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?',
                '[', ']', '{', '}',
              ]
            for i in range( 0,len(punctTable)) :
                if (ord(punctTable[i]) > 0) :
                    DynamicDataEncoder.charMap[MODE_PUNCT][ord(punctTable[i])] = i;

        return DynamicDataEncoder.charMap[mode][ord(char)];
