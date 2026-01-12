#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
'''
Modified by znight@yeah.net
from metzli and zxing

'''

import inkex
from lxml import etree
import aztec
import aztec.Encoder
from barcode.GridDrawer import GridDrawer

import codecs
import sys

import gettext
_ = gettext.gettext
    

#RENDERING ROUTINES ==================================================
#   Take the array of 1's and 0's and render as a series of black
#   squares. A binary 1 is a filled square
#=====================================================================

#SVG element generation routine
    
class Aztec(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        
    def add_arguments(self, pars):
        #PARSE OPTIONS
        pars.add_argument("--text", default="Inkscape")
        pars.add_argument("--ECC", type=int,default="33")
        pars.add_argument("--encoding", default="utf-8")
        pars.add_argument("--size", type=float,default=1)
        pars.add_argument("--drawtype", default="greedy")
        pars.add_argument("--smoothval", type=float, default=0.2)
        pars.add_argument("--invert", type=inkex.Boolean, default="false")
        pars.add_argument("--symbolid", default='')
           
    def effect(self):
        
        so = self.options
        
        if so.text == '':  #abort if converting blank text
            inkex.errormsg(_('Please enter an input string'))
        else:
            # Python 2 and 3 compatibility.
            if sys.version_info >= (3, 0, 0):
                # for Python 3 ugly hack to represent bytes as str for Python2 compatibility
                text_str = str(so.text)
                text_bytes = bytes(so.text, so.encoding).decode("latin-1")
            else:
                text_str = str(so.text).decode(sys.getfilesystemencoding())
                text_bytes = text_str.encode(so.encoding)
        
            #INKSCAPE GROUP TO CONTAIN EVERYTHING
            

            #circ = etree.SubElement(grp, inkex.addNS('text','svg'), {} )
            #circ.text=str(so.TEXT)    
            size=so.size*self.svg.unittouu('1mm')
            
            r= aztec.Encoder.Encoder()
            q=r.encode(text_bytes,so.ECC)
            
            if q and len(q)>0 and len(q[0])>0:
              (x,y) = self.svg.namedview.center   #Put in in the centre of the current view
              y-=len(q)/2.0*size
              x-=len(q[0])/2.0*size
              centre=(x,y)            
              grp_transform = 'translate' + str( centre )
              grp_name = 'Aztec'
              grp_attribs = {inkex.addNS('label','inkscape'):grp_name,
                             'transform':grp_transform }
              grp = etree.SubElement(self.svg.get_current_layer(), 'g', grp_attribs)#the group to put everything in
              grp.set('inkscape:label', 'Aztec Code: ' + text_str)
              qrDraw = GridDrawer(so.size,1, so.invert, so.smoothval, so.symbolid, 4)
              qrDraw.setGrid(q)
              qrDraw.makeSVG(grp, so.drawtype)
              return grp
            
if __name__ == '__main__':
    e = Aztec()
    e.run()

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
