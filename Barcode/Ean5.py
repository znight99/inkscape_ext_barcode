# 
# Copyright (C) 2009 Aaron C Spike
#               2010 Martin Owens
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
Python barcode renderer for EAN5 barcodes. Designed for use with Inkscape.
"""

from Base import RIGHT
from BaseEan import EanBarcode

FAMS  = [ '11000','10100','10010','10001','01100','00110','00011','01010','01001','00101' ]
START = '01011'

class Ean5(EanBarcode):
    """Provide an Ean5 barcode generator"""
    name   = 'ean5'
    length = 5

    def _encode(self, number):
        #self.x += 104.0*self.scale               # horiz offset so it does not overlap EAN13
        #self.y -= (self.height +0.5)*self.scale   # move the text to the top
        self.label ='  '+ ''.join(self.space(number))+' '+('>' if self.rightmark else ' ')
        family = sum([int(n)*int(m) for n,m in zip(number, '39393')]) % 10
        return '00'+START + '01'.join(self.encode_interleaved(family, number, FAMS))+'0'*5

    def labelOffset(self):
        return -self.height-0.5

    def getStyle(self, index):
        result = { 'width' : '1', 'top' :  float(self.fontSize())+0.5, 'write' : True }
        if index==0: # White Space
            result['write'] = False
        elif index==1: # Black Bar
            result['height'] = float(self.height)+5 - (float(self.fontSize())+0.5)
        elif index==2: # Guide Bar
            result['height'] = float(self.height) + 5
        return result
