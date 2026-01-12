#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
'''
Created by znight@yeah.net
'''

import inkex
from lxml import etree
import gridmatrix

from barcode.GridDrawer import GridDrawer

import sys

import gettext
_ = gettext.gettext
    


class GridMatrix(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        
    def add_arguments(self, pars):
        #PARSE OPTIONS
        pars.add_argument("--text",
            type=str,
            dest="TEXT", default='Inkscape')

        pars.add_argument("--version",
            type=int,
            dest="VERSION", default=1)
            
        pars.add_argument("--ECC",
            type=int,
            dest="ECC", default=1)
 
        pars.add_argument("--size", type=float, default=1.0)
        pars.add_argument("--drawtype", default="greedy")
        pars.add_argument("--smoothval", type=float, default=0.2)
        pars.add_argument("--symbolid", default='')
            
    def effect(self):
        
        so = self.options
        
        so.encoding='utf-8'
        if so.TEXT == '':  #abort if converting blank text
            inkex.errormsg(_('Please enter an input string'))
        else:
            # Python 2 and 3 compatibility.
            if sys.version_info >= (3, 0, 0):
                # for Python 3 ugly hack to represent bytes as str for Python2 compatibility
                text_str = str(so.TEXT)
                text_bytes = bytes(so.TEXT, so.encoding).decode("latin-1")
            else:
                text_str = str(so.TEXT).decode(sys.getfilesystemencoding())
                text_bytes = text_str.encode(so.encoding)
        
            #INKSCAPE GROUP TO CONTAIN EVERYTHING
                        
            ver=so.VERSION
            q= gridmatrix.main.GridMatrix(version=ver, error_correction=so.ECC)
            q.add_data(text_bytes)
            q.make()
            
            size=so.size*self.svg.unittouu('1mm')
            m=q.modules
            if m and len(m)>0 and len(m[0])>0:
              (x,y) = self.svg.namedview.center   #Put in in the centre of the current view
              y-=len(m)/2.0*size
              x-=len(m[0])/2.0*size
              centre=(x,y)
              grp_transform = 'translate' + str( centre )
              grp_name = 'GridMatrix'
              grp_attribs = {inkex.addNS('label','inkscape'):grp_name,
                             'transform':grp_transform }
              grp = etree.SubElement(self.svg.get_current_layer(), 'g', grp_attribs)#the group to put everything in
              
              qrDraw = GridDrawer(size, 1,False, self.options.smoothval, self.options.symbolid, 4)
              qrDraw.setGrid(m)
              qrDraw.makeSVG(grp,self.options.drawtype)
              #render_code( m, size, 0,0,grp )    # generate the SVG elements
            
if __name__ == '__main__':
    e = GridMatrix()
    e.run()

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
