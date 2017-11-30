#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
'''
Modified by znight@yeah.net

'''

import inkex, simplestyle

import datamatrix

import sys,codecs

import gettext
_ = gettext.gettext
    
symbols = {
    'sq10': (10, 10),
    'sq12': (12, 12),
    'sq14': (14, 14),
    'sq16': (16, 16),
    'sq18': (18, 18),
    'sq20': (20, 20),
    'sq22': (22, 22),
    'sq24': (24, 24),
    'sq26': (26, 26),
    'sq32': (32, 32),
    'sq36': (36, 36),
    'sq40': (40, 40),
    'sq44': (44, 44),
    'sq48': (48, 48),
    'sq52': (52, 52),
    'sq64': (64, 64),
    'sq72': (72, 72),
    'sq80': (80, 80),
    'sq88': (88, 88),
    'sq96': (96, 96),
    'sq104': (104, 104),
    'sq120': (120, 120),
    'sq132': (132, 132),
    'sq144': (144, 144),
    'rect8x18': (8, 18),
    'rect8x32': (8, 32),
    'rect12x26': (12, 26),
    'rect12x36': (12, 36),
    'rect16x36': (16, 36),
    'rect16x48': (16, 48),
}

#RENDERING ROUTINES ==================================================
#   Take the array of 1's and 0's and render as a series of black
#   squares. A binary 1 is a filled square
#=====================================================================

#SVG element generation routine
def draw_SVG_square((w,h), (x,y), c,parent):
    cc=['white','black','grey']
    style = {   'stroke'        : 'none',
                'stroke-width'  : '0',
                'fill'          : cc[c],
                'fill-opacity': str(0.5 if c==2 else 1.0)
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
def render_code( q, size, cx,cy,parent):
                 
     for y in range(len(q)):    
       for x in range(len(q[y])):
           if q[y][x]==None:
             draw_SVG_square((size*1.1,size*1.1), (x*size+cx ,y*size+cy), 2,parent)
           elif q[y][x]: #A binary 1 is a filled square
             draw_SVG_square((size*1.1,size*1.1), (x*size+cx ,y*size+cy), 1,parent)
     
class DataMatrix(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        
        #PARSE OPTIONS
        self.OptionParser.add_option("--text",
            action="store", type="string",
            dest="TEXT", default='Inkscape')
        self.OptionParser.add_option("--symbol",
            action="store", type="string",
            dest="SYMBOL", default='')
        self.OptionParser.add_option("--size",
            action="store", type="int",
            dest="SIZE", default=1)
            
    def effect(self):
        
        so = self.options

        if (so.SYMBOL != '' and (so.SYMBOL in symbols)):
            rows = symbols[so.SYMBOL][0]
            cols = symbols[so.SYMBOL][1]
        else:
          rows=cols=16
        
        if so.TEXT == '':  #abort if converting blank text
            inkex.errormsg(_('Please enter an input string'))
        else:
        
            #INKSCAPE GROUP TO CONTAIN EVERYTHING
            
            
            #GENERATE THE DATAMATRIX
            ms = datamatrix.datamatrix.encode( unicode(so.TEXT,'mbcs').encode('utf-8') if sys.getfilesystemencoding()=='mbcs' else so.TEXT, (rows, cols) ) #get the pattern of squares

            size=so.SIZE*self.unittouu('1mm')
            if ms and len(ms)>0 and len(ms[0])>0 and len(ms[0][0])>0:
              (x,y) = self.view_center   #Put in in the centre of the current view
              y-=len(ms[0])/2.0*size
              x-=len(ms[0][0])/2.0*size
              centre=(x,y)
              grp_transform = 'translate' + str( centre )
              grp_name = 'DataMatrix'
              grp_attribs = {inkex.addNS('label','inkscape'):grp_name,
                             'transform':grp_transform }
              grp = inkex.etree.SubElement(self.current_layer, 'g', grp_attribs)#the group to put everything in
              
              cx=0
              for m in ms:
                render_code( m, size, cx,0, grp )    # generate the SVG elements
                cx+=len(m[0])*size*1.5
if __name__ == '__main__':
    e = DataMatrix()
    e.affect()

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
