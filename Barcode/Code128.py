#
# Authored by Martin Owens <doctormo@gmail.com>
# Debugged by Ralf Heinecke & Martin Siepmann 2007-09-07
#             Horst Schottky 2010-02-27
#
# Copyright (C) 2007 Martin Owens
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
Python barcode renderer for Code128/EAN128 barcodes. Designed for use with Inkscape.
"""

from Base import Barcode
import math
import re

codeMap = [
        '11011001100','11001101100','11001100110','10010011000','10010001100',
        '10001001100','10011001000','10011000100','10001100100','11001001000',
        '11001000100','11000100100','10110011100','10011011100','10011001110',
        '10111001100','10011101100','10011100110','11001110010','11001011100',
        '11001001110','11011100100','11001110100','11101101110','11101001100',
        '11100101100','11100100110','11101100100','11100110100','11100110010',
        '11011011000','11011000110','11000110110','10100011000','10001011000',
        '10001000110','10110001000','10001101000','10001100010','11010001000',
        '11000101000','11000100010','10110111000','10110001110','10001101110',
        '10111011000','10111000110','10001110110','11101110110','11010001110',
        '11000101110','11011101000','11011100010','11011101110','11101011000',
        '11101000110','11100010110','11101101000','11101100010','11100011010',
        '11101111010','11001000010','11110001010','10100110000','10100001100',
        '10010110000','10010000110','10000101100','10000100110','10110010000',
        '10110000100','10011010000','10011000010','10000110100','10000110010',
        '11000010010','11001010000','11110111010','11000010100','10001111010',
        '10100111100','10010111100','10010011110','10111100100','10011110100',
        '10011110010','11110100100','11110010100','11110010010','11011011110',
        '11011110110','11110110110','10101111000','10100011110','10001011110',
        '10111101000','10111100010','11110101000','11110100010','10111011110',
        '10111101110','11101011110','11110101110','11010000100','11010010000',
        '11010011100','11000111010','11' ]

FNC1=u'\ue001'
FNC2=u'\ue002'
FNC3=u'\ue003'
FNC4=u'\ue004'
CODEA=u'\ue011'
CODEB=u'\ue012'
CODEC=u'\ue013'
SHIFT=u'\ue010'

START_A=103
START_B=104
START_C=105

def mapExtra(sd, chars):
    result = list(sd)
    for char in chars:
        result.append(chr(char))
    result.append(FNC3)
    result.append(FNC2)
    result.append(SHIFT)
    result.append(CODEC)
    return result

# The mapExtra method is used to slim down the amount
# of pre code and instead we generate the lists
charAB = list(' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_')
charA = mapExtra(charAB, range(0, 32)) # Offset 64
charA.append(CODEB)
charA.append(FNC4)
charA.append(FNC1)
charB = mapExtra(charAB, range(96, 128)) # Offset -32
charB.append(FNC4)
charB.append(CODEA)
charB.append(FNC1)
charC=range(100)
charC.append(CODEB)
charC.append(CODEA)
charC.append(FNC1)


class Code128(Barcode):
    """Main barcode object, generates the encoding bits here"""
    def dlen(self,text):
      dl=0
      for c in text:
        if c==FNC1:
          if dl%2==0:
            dl+=2
          else:
            break
        elif c>='0' and c<='9':
          dl+=1
        else:
          break
        if dl>=4:
          break
      return dl
    
    def fit_c(self,text):
      dl=self.dlen(text)
      if dl>=4:
        return dl%2
      return -1
    
    def fit_a(self,text):
      for c in text:
        #print c
        if c>='`' and c<=chr(127):
          break
        if c>=chr(0) and c<=chr(31):
          return True
          break
      return False
              
    def fit_b(self,text):
      for c in text:
        if c>=chr(0) and c<=chr(31):
          break
        if c>='`' and c<=chr(127):
          return True
          break
      return False
      
    def app(self,s,cs,c):
      if ord(c)>=128 and ord(c)<=255:
        s.append(cs.index(FNC4))
        s.append(cs.index(chr(ord(c)-128)))
      else:
        s.append(cs.index(c))
      return s
    
    def preprocess(self,text):
      i=0
      ext=False
      r=''
      while i<len(text):
        c=text[i]
        if not ext and ord(c)>=128 and ord(c)<=255 or ext and ord(c)>=0 and ord(c)<=127:
          j=1
          while j<5 and i+j<len(text):
            c2=text[i+j]
            if ext and ord(c2)>=128 and ord(c2)<=255 or not ext and ord(c2)>=0 and ord(c2)<=127:
              break
            j+=1
          if j>=5 or j>=3 and i+j>=len(text):
            r+=FNC4+FNC4
            ext=not ext
        if ext:
          if ord(c)>=128 and ord(c)<=255:
            r+=chr(ord(c)-128)
          else:
            r+=FNC4+c
        else:
          if ord(c)>=128 and ord(c)<=255:
            r+=FNC4+chr(ord(c)-128)
          else:
            r+=c
        i+=1
      return r
          
          
    def process(self,stext):
      text=self.preprocess(stext)
      start=START_B
      now=CODEB
      dl=self.dlen(text)
      #print self.fit_a(text)
      if dl==2 and len(text)<=2:
        start=START_C
        now=CODEC
      elif dl>=4:
        start=START_C
        now=CODEC
      elif self.fit_a(text):
        start=START_A
        now=CODEA
      s=[start]
      i=0
      #print charB
      while i <len(text):
        c=text[i]
        #print i,ord(c),hex(ord(now))
        #print s
        if now==CODEA:
          dl=self.fit_c(text[i:])
          if dl==1:
            s.append(charA.index(CODEC))
            now=CODEC
          elif dl==0:
            s.append(charA.index(CODEC))
            now=CODEC
            i-=1
          elif c>='`' and c<=chr(127):
            if self.fit_a(text[i+1:]):
              s.append(charA.index(SHIFT))
              s.append(charB.index(c))
            else:
              s.append(charA.index(CODEB))
              now=CODEB
              i-=1
          else:
            s=self.app(s,charA,c)
        elif now==CODEB:
          dl=self.fit_c(text[i:])
          if dl==1:
            s.append(charB.index(CODEC))
            now=CODEC
          elif dl==0:
            s.append(charB.index(CODEC))
            now=CODEC
            i-=1
          elif c>=chr(0) and c<=chr(31):
            if self.fit_b(text[i+1:]):
              s.append(charB.index(SHIFT))
              s.append(charA.index(c))
            else:
              s.append(charB.index(CODEA))
              now=CODEA
              i-=1
          else:
            s=self.app(s,charB,c)
          #print s
        else:
          t=0
          if c>='0' and c<='9':
            t=ord(c)-ord('0')
            if i+1<len(text) and text[i+1]>='0' and text[i+1]<='9':
              t*=10
              t+=ord(text[i+1])-ord('0')
              i+=1
              s.append(t)
            else:
              now=CODEB
              if self.fit_a(text[i:]):
                now=COBEA
              s.append(charC.index(now))
              i-=1
          elif c==FNC1:
            s=self.app(s,charC,c)
          else:
            now=CODEB
            if self.fit_a(text[i:]):
              now=CODEA
            s.append(charC.index(now))
            i-=1
        i+=1
      #print s
      return s            
      
    
    def encode(self, text):
        result = ''
        
        s=self.process(text)

        self.inclabel = text
        return '0'*10+self.encodeBlocks(s)+'0'*10

    def encodeBlocks(self, s):
        total  = 0
        pos    = 1
        encode = '';

        for c in s:

            total = total + c * pos
            if c<103:
              pos+=1
            encode = encode + codeMap[c]

        checksum = total % 103
        encode = encode + codeMap[checksum]
        encode = encode + codeMap[106]
        encode = encode + codeMap[107]

        return '0'*10+encode+'0'*10

if __name__ == '__main__':
  r=Code128({ 'text':'1234567890'})
  print r.process(u'A\x04'+FNC1+u'123b123456abcd@\x03\x80\x81\xaa\xc8\xc90234')
  
  s=r.preprocess(u'A\x04'+FNC1+u'123b123456abcd@\x03\x80\x81\xaa\xc8\xc90234')
  t=''
  for c in s:
    if c==FNC1:
      t+='[FNC1]'
    elif c==FNC2:
      t+='[FNC2]'
    elif c==FNC3:
      t+='[FNC3]'
    elif c==FNC4:
      t+='[FNC4]'
    elif ord(c)>=0 and ord(c)<=31 or ord(c)>=0x80 and ord(c)<=0xff:
      t+='['+hex(ord(c))[2:]+']'
    else:
      t+=c
  print t
  
         