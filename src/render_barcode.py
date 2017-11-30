#!/usr/bin/env python
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
Inkscape's general barcode extension. Run from within inkscape or use the
Barcode module provided for outside or scripting.
"""

import inkex
import sys
from Barcode import getBarcode

class InsertBarcode(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("-l", "--height",
                        action="store", type="int",
                        dest="height", default=30,
                        help="Barcode Height")
        self.OptionParser.add_option("-t", "--type",
                        action="store", type="string",
                        dest="type", default='',
                        help="Barcode Type")
        self.OptionParser.add_option("-d", "--text",
                        action="store", type="string",
                        dest="text", default='',
                        help="Text to print on barcode")
        self.OptionParser.add_option("-a", "--addon",
                        action="store", type="string",
                        dest="addon", default='',
                        help="Addon barcode(2 or 5 digits)")
        self.OptionParser.add_option("-q", "--quietmark",
                        action="store", type="inkbool",
                        dest="quietmark", default=False,
                        help="Display quiet mark")


    def effect(self):
        x, y = self.view_center
        bargen = getBarcode( self.options.type,
            text=self.options.text,
            height=self.options.height,
            document=self.document,
            x=0, y=0,
            scale=self.unittouu('0.33mm'),
			      addon= self.options.addon,
			      quietmark= self.options.quietmark,
        )
        if bargen is not None:
            barcode,w,h = bargen.generate()
            if barcode is not None:
                (x,y) = self.view_center   #Put in in the centre of the current view
                y-=h/2.0
                x-=w/2.0
                centre=(x,y)
                grp_transform = 'translate' + str( centre )
                grp_name = 'Barcode'
                grp_attribs = {inkex.addNS('label','inkscape'):grp_name,
                               'transform':grp_transform }
                grp = inkex.etree.SubElement(self.current_layer, 'g', grp_attribs)#the group to put everything in
                if not isinstance(barcode,list):
                  barcode=[barcode]
                for bc in barcode:
                  grp.append(bc)
            else:
                sys.stderr.write("No barcode was generated\n")
        else:
            sys.stderr.write("Unable to make barcode with: " + str(self.options) + "\n")

def test_barcode():
    bargen = getBarcode("Ean13", text="123456789101")
    if bargen is not None:
        barcode,w,h = bargen.generate()
    if barcode:
        print inkex.etree.tostring(barcode, pretty_print=True)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Debug mode without inkex
        test_barcode()
        exit(0)
    e = InsertBarcode()
    e.affect()

