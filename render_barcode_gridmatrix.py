#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
'''
Created by znight@yeah.net
'''

import inkex, simplestyle

import gridmatrix

import codecs
import sys

import gettext
_ = gettext.gettext
    

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
    
class GridMatrix(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        
        #PARSE OPTIONS
        self.OptionParser.add_option("--text",
            action="store", type="string",
            dest="TEXT", default='Inkscape')

        self.OptionParser.add_option("--version",
            action="store", type="int",
            dest="VERSION", default=1)
            
        self.OptionParser.add_option("--ECC",
            action="store", type="int",
            dest="ECC", default=1)
 
        self.OptionParser.add_option("--size",
            action="store", type="int",
            dest="SIZE", default=1)
            
    def effect(self):
        
        so = self.options
        
        if so.TEXT == '':  #abort if converting blank text
            inkex.errormsg(_('Please enter an input string'))
        else:
        
            #INKSCAPE GROUP TO CONTAIN EVERYTHING
                        
            ver=so.VERSION
            q= gridmatrix.main.GridMatrix(version=ver, error_correction=so.ECC)
            q.add_data(unicode(so.TEXT,'mbcs').encode('utf-8') if sys.getfilesystemencoding()=='mbcs' else so.TEXT)
            q.make()
            
            size=so.SIZE*self.unittouu('1mm')
            m=q.modules
            if m and len(m)>0 and len(m[0])>0:
              (x,y) = self.view_center   #Put in in the centre of the current view
              y-=len(m)/2.0*size
              x-=len(m[0])/2.0*size
              centre=(x,y)
              grp_transform = 'translate' + str( centre )
              grp_name = 'GridMatrix'
              grp_attribs = {inkex.addNS('label','inkscape'):grp_name,
                             'transform':grp_transform }
              grp = inkex.etree.SubElement(self.current_layer, 'g', grp_attribs)#the group to put everything in
              
              render_code( m, size, 0,0,grp )    # generate the SVG elements
            
if __name__ == '__main__':
    e = GridMatrix()
    e.affect()

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
