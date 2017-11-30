#
# Copyright (C) 2010 Geoffrey Mosini
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
Generate barcodes for Code25-interleaved 2 of 5, for Inkscape.
"""
from lxml import etree

from Base import Barcode
import sys

(NARROW_WHITE, NARROW_BLACK, WIDE_WHITE, WIDE_BLACK) = range(4)

# 1 means thick, 0 means thin
encoding = {
    '0' : '00110',
    '1' : '10001',
    '2' : '01001',
    '3' : '11000', 
    '4' : '00101',
    '5' : '10100',
    '6' : '01100',
    '7' : '00011',
    '8' : '10010',
    '9' : '01010',
}

# Start and stop code are already encoded into white (0) and black(1) bars
start_code = '1010'
stop_code = '1101'

FW=3

class Code25i(Barcode):
    # Convert a text into string binary of black and white markers
    name='Code25i'
    
    def encode(self, number):
      
      

        if not number.isdigit():
            sys.stderr.write("CODE25 can only encode numbers.\n")
            return

        # Number of figures to encode must be even, a 0 is added to the left in case it's odd.

        if self.quietmark:
          checksum=self.getChecksum(number)
          number=number+checksum

        if len(number) % 2 > 0 :
            number = '0' + number
        self.label = number

        # Number is encoded by pairs of 2 figures
        size = len(number) / 2;
        encoded = start_code;
        for i in range(size):
            # First in the pair is encoded in black (1), second in white (0)
            black =  encoding[number[i*2]]
            white = encoding[number[i*2+1]]
            for j in range(5):
                if black[j] == '1':
                    encoded += str(WIDE_BLACK)
                else:
                    encoded +=str(NARROW_BLACK)
                if white[j] == '1':
                    encoded += str(WIDE_WHITE)
                else:
                    encoded += str(NARROW_WHITE)

        encoded += stop_code

        self.inclabel = number
        return '0'*10+encoded+'0'*10;

    def generate(self):
      r,w,h=Barcode.generate(self)
      
      if self.quietmark:
        data=self.data
        bar_offset=0
        for datum in data:
          # Datum 0 tells us what style of bar is to come next
          style = self.getStyle(int(datum[0]))
          # Datum 1 tells us what width in units,
          # style tells us how wide a unit is
          width = int(datum[1]) * float(style['width'])
  
          bar_offset += width
  
        barwidth = bar_offset
        frame=etree.SubElement(r,'path')
        d='M %f,%f '%(-FW,-FW)
        d+='h %f '%(barwidth+FW*2)
        d+='v %f '%(self.height+FW*2)
        d+='h %f '%-(barwidth+FW*2)
        d+='v %f '%-(self.height+FW*2)
        d+='M %f,%f '%(0,0)
        d+='v %f '%(self.height)
        d+='h %f '%(barwidth)
        d+='v %f '%-(self.height)
        d+='h %f '%-(barwidth)
        frame.set('d',d)
        frame.set('style', 'fill:black;stroke:none')
       
      return r,w,h

    def getChecksum(self, number, magic=10):
        """Generate a UPCA/EAN13/EAN8 Checksum"""
        weight = [3,1] * len(number)
        result = 0
        # We need to work from left to right so reverse
        number = number[::-1]
        # checksum based on first digits.
        for i in range(len(number)):
           result += int(number[i]) * weight[i]
        # Modulous result to a single digit checksum
        checksum = magic - (result % magic)
        if checksum < 0 or checksum >= magic:
           return '0'
        return str(checksum)
        
    def labelOffset(self):
      if self.quietmark:
        return FW
      return 0

    def getStyle(self, index):
        """Returns the styles that should be applied to each bar"""
        result = { 'width' : 1, 'top' : 0, 'write' : True }
        if index == NARROW_BLACK:
            result['height'] = int(self.height)
        elif index == WIDE_BLACK:
            result['height'] = int(self.height)
            result['width']= 2.5
        elif index == NARROW_WHITE:
            result['write'] = False
        elif index == WIDE_WHITE:
            result['write'] = False
            result['width']= 2.5
        return result
