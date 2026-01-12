#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
'''
Modified by znight@yeah.net
from zxing
'''

import inkex
from lxml import etree
from barcode.GridDrawer import GridDrawer

import sys,codecs

import pdf417
import pdf417.PDF417


import gettext
_ = gettext.gettext
    

#RENDERING ROUTINES ==================================================
#   Take the array of 1's and 0's and render as a series of black
#   squares. A binary 1 is a filled square
#=====================================================================
    
class PDF417x(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        
    def add_arguments(self, pars):
        #PARSE OPTIONS
        pars.add_argument("--text",
             type=str,
            dest="text", default='Inkscape')

        pars.add_argument("--ECC",
             type=int,
            dest="ECC", default=0)
 
        pars.add_argument("--size",
             type=int,
            dest="SIZE", default=1)
        pars.add_argument("--yHeight",
             type=float,
            dest="YHEIGHT", default=3.0)
        pars.add_argument("--aspect",
             type=float,
            dest="ASPECT", default=3.0)

        pars.add_argument("--Cols",
             type=int,
            dest="COLS", default=1)
            
        pars.add_argument("--Rows",
             type=int,
            dest="ROWS", default=3)

        pars.add_argument("--encoding", default="utf-8")
        pars.add_argument("--drawtype", default="greedy")
        pars.add_argument("--smoothval", type=float, default=0.2)
        pars.add_argument("--symbolid", default='')
            
    def effect(self):
        
        so = self.options
        
        if so.text == '':  #abort if converting blank text
            inkex.errormsg(_('Please enter an input string'))
        else:
        
            #INKSCAPE GROUP TO CONTAIN EVERYTHING
                        
            # Python 2 and 3 compatibility.
            if sys.version_info >= (3, 0, 0):
                # for Python 3 ugly hack to represent bytes as str for Python2 compatibility
                text_str = str(so.text)
                text_bytes = bytes(so.text, so.encoding).decode("latin-1")
            else:
                text_str = str(so.text).decode(sys.getfilesystemencoding())
                text_bytes = text_str.encode(so.encoding)

            q=pdf417.PDF417.PDF417(False)
            q.setDimensions(30,so.COLS,90,so.ROWS)
            q.generateBarcodeLogic(text_bytes,so.ECC,so.ASPECT*so.YHEIGHT)
            
            
            
            m=q.barcodeMatrix.getScaledMatrix(1,1)
            
            if m and len(m)>0 and len(m[0])>0:
              (x,y) = self.svg.namedview.center   #Put in in the centre of the current view
              size=so.SIZE*self.svg.unittouu('0.33mm')
              y-=len(m)/2.0*size*so.YHEIGHT
              x-=len(m[0])/2.0*size
              centre=(x,y)
              grp_transform = 'translate' + str( centre )
              grp_name = 'PDF417'
              grp_attribs = {inkex.addNS('label','inkscape'):grp_name,
                             'transform':grp_transform }
              grp = etree.SubElement(self.svg.get_current_layer(), 'g', grp_attribs)#the group to put everything in
              
              qrDraw = GridDrawer(size,so.YHEIGHT, False, so.smoothval, so.symbolid, 4)
              qrDraw.setGrid(m)
              qrDraw.makeSVG(grp, so.drawtype)

              #render_pdf417( m, size, so.YHEIGHT, 0,0, grp )    # generate the SVG elements
            
if __name__ == '__main__':
    e = PDF417x()
    e.run()

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
