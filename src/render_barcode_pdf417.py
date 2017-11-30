#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
'''
Modified by znight@yeah.net
from zxing
'''

import inkex, simplestyle

import sys,codecs

import pdf417
import pdf417.PDF417


import gettext
_ = gettext.gettext
    

#RENDERING ROUTINES ==================================================
#   Take the array of 1's and 0's and render as a series of black
#   squares. A binary 1 is a filled square
#=====================================================================

#SVG element generation routine
def draw_SVG_square((w,h), (x,y), parent):

    style = {   'stroke'        : 'none',
                'stroke-width'  : '0',
                'fill'          : '#000000'
            }
                
    attribs = {
        'style'     :simplestyle.formatStyle(style),
        'height'    : str(h),
        'width'     : str(w),
        'x'         : str(x),
        'y'         : str(y)
            }
    circ = inkex.etree.SubElement(parent, inkex.addNS('rect','svg'), attribs )
    
#turn a 2D array of 1's and 0's into a set of black squares
def render_pdf417( q, size,yh,cx,cy,parent):
                 
     for y in range(len(q)):     #loop over all the modules in the datamatrix
       for x in range(len(q[y])):
           
                if q[y][x] == 1: #A binary 1 is a filled square
                    draw_SVG_square((size*1.1,size*yh*1.1), (cx+x*size ,cy+y*yh*size), parent)
                elif q[y][x] != 0: #we have an invalid bit value
                    inkex.errormsg(_('Invalid bit value, this is a bug!'))
    
class PDF417x(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        
        #PARSE OPTIONS
        self.OptionParser.add_option("--text",
            action="store", type="string",
            dest="TEXT", default='Inkscape')

        self.OptionParser.add_option("--ECC",
            action="store", type="int",
            dest="ECC", default=0)
 
        self.OptionParser.add_option("--size",
            action="store", type="int",
            dest="SIZE", default=1)
        self.OptionParser.add_option("--yHeight",
            action="store", type="float",
            dest="YHEIGHT", default=3.0)
        self.OptionParser.add_option("--aspect",
            action="store", type="float",
            dest="ASPECT", default=3.0)

        self.OptionParser.add_option("--Cols",
            action="store", type="int",
            dest="COLS", default=1)
            
        self.OptionParser.add_option("--Rows",
            action="store", type="int",
            dest="ROWS", default=3)
            
    def effect(self):
        
        so = self.options
        
        if so.TEXT == '':  #abort if converting blank text
            inkex.errormsg(_('Please enter an input string'))
        else:
        
            #INKSCAPE GROUP TO CONTAIN EVERYTHING
                        

            q=pdf417.PDF417.PDF417(False)
            q.setDimensions(30,so.COLS,90,so.ROWS)
            q.generateBarcodeLogic(unicode(so.TEXT,'mbcs').encode('utf-8') if sys.getfilesystemencoding()=='mbcs' else so.TEXT,so.ECC,so.ASPECT*so.YHEIGHT)
            
            
            
            m=q.barcodeMatrix.getScaledMatrix(1,1)
            
            if m and len(m)>0 and len(m[0])>0:
              (x,y) = self.view_center   #Put in in the centre of the current view
              size=so.SIZE*self.unittouu('0.33mm')
              y-=len(m)/2.0*size*so.YHEIGHT
              x-=len(m[0])/2.0*size
              centre=(x,y)
              grp_transform = 'translate' + str( centre )
              grp_name = 'PDF417'
              grp_attribs = {inkex.addNS('label','inkscape'):grp_name,
                             'transform':grp_transform }
              grp = inkex.etree.SubElement(self.current_layer, 'g', grp_attribs)#the group to put everything in
              render_pdf417( m, size, so.YHEIGHT, 0,0, grp )    # generate the SVG elements
            
if __name__ == '__main__':
    e = PDF417x()
    e.affect()

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
