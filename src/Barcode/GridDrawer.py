#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2009 Kazuhiko Arase (http://www.d-project.com/)
#               2010 Bulia Byak <buliabyak@gmail.com>
#               2018 Kirill Okhotnikov <kirill.okhotnikov@gmail.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110, USA.
#
"""
Provide the Grid rendering.
"""

from __future__ import print_function

import sys
from itertools import product

import inkex
from inkex import Group, Rectangle, Use, PathElement

class GridDrawer(object):
    def __init__(self, boxsize,yscale, invert_code, smooth_factor, symbol_id, margin=4):
        self.boxsize = boxsize
        self.yscale=yscale
        self.invertCode = invert_code
        self.smoothFactor = smooth_factor
        self.symbolId = symbol_id
        self.margin = margin

        self.grid = None

    def setGrid(self, grid):
        if len({len(g) for g in grid}) != 1:
            raise Exception("The array is not rectangular")
        else:
            self.grid = grid

    def rowCount(self):
        return len(self.grid) if self.grid is not None else 0

    def colCount(self):
        return len(self.grid[0]) if self.rowCount() > 0 else 0

    def isDark(self, col, row):
        inside = col >= 0 and 0 <= row < self.rowCount() and col < self.colCount()
        return False if not inside else self.grid[row][col] != self.invertCode

    def getSVGPos(self, col, row):
        return (col + self.margin) * self.boxsize, (row + self.margin) * self.boxsize*self.yscale

    def makeSVGRect(self, grp):
        for r in range(self.rowCount()):
            for c in range(self.colCount()):
                if self.isDark(c, r):
                    x, y = self.getSVGPos(c, r)
                    rect = Rectangle()
                    rect.set('x', str(x))
                    rect.set('y', str(y))
                    rect.set('width', str(self.boxsize*1.05))
                    rect.set('height', str(self.boxsize*self.yscale*1.05))
                    grp.append(rect)

    def makeSVGSymbol(self, grp):
        for r in range(self.rowCount()):
            for c in range(self.colCount()):
                if self.isDark(c, r):
                    x, y = self.getSVGPos(c, r)
                    symbol = Use()
                    symbol.set('xlink:href', self.symbolId)
                    symbol.set('x', str(x))
                    symbol.set('y', str(y))
                    symbol.set('width', str(self.boxsize))
                    symbol.set('height', str(self.boxsize*self.yscale))
                    grp.append(symbol)

    def getIconPathStr(self, pointStr):
        result = ""
        digBuffer = ""
        i=0
        for c in pointStr:
            if c.isdigit() or c == "-" or c == '.':
                digBuffer += c
            else:
                if len(digBuffer) > 0:
                    if i%2==0:
                      result += str(float(digBuffer) * self.boxsize)
                    else:
                      result += str(float(digBuffer) * self.boxsize*self.yscale)
                    i+=1
                    digBuffer = ""
                result += c

        if len(digBuffer) > 0:
          if i%2==0:
            result += str(float(digBuffer) * self.boxsize)
          else:
            result += str(float(digBuffer) * self.boxsize*self.yscale)
          i+=1

        return result

    def makeSVGPath(self, grp, pointStr):
        singlePath = self.getIconPathStr(pointStr)
        pathStr = ""
        for r in range(self.rowCount()):
            for c in range(self.colCount()):
                if self.isDark(c, r):
                    x, y = self.getSVGPos(c, r)
                    pathStr += "M %f,%f " % (x, y) + singlePath + " z "

        path = PathElement()
        path.set('d', pathStr)
        grp.append(path)

    def makeSVGCircle(self, grp):
        s = 'm 0.5,0.5 ' \
            'c 0.2761423745,0 0.5,0.2238576255 0.5,0.5 ' \
            'c 0,0.2761423745 -0.2238576255,0.5 -0.5,0.5 ' \
            'c -0.2761423745,0 -0.5,-0.2238576255 -0.5,-0.5 ' \
            'c 0,-0.2761423745 0.2238576255,-0.5 0.5,-0.5'
        self.makeSVGPath(grp, s)

    @staticmethod
    def moveByDirection(xyd):
        dm = {0: (1, 0), 1: (0, -1), 2: (-1, 0), 3: (0, 1)}
        return xyd[0] + dm[xyd[2]][0], xyd[1] + dm[xyd[2]][1]

    @staticmethod
    def makeDirectionsTable():
        result = []
        for cfg in product(range(2), repeat=4):
            result.append([])
            for d in range(4):
                if cfg[3 - d] == 0 and cfg[3 - (d - 1) % 4] != 0:
                    result[-1].append(d)
        return result

    def createVertexesForAdvDrawer(self):
        dirTable = self.makeDirectionsTable()
        result = []
        # Create vertex
        for r in range(self.rowCount() + 1):
            for c in range(self.colCount() + 1):
                indx = (2 ** 0 if self.isDark(c - 0, r - 1) else 0) + \
                       (2 ** 1 if self.isDark(c - 1, r - 1) else 0) + \
                       (2 ** 2 if self.isDark(c - 1, r - 0) else 0) + \
                       (2 ** 3 if self.isDark(c - 0, r - 0) else 0)

                for d in dirTable[indx]:
                    result.append((c, r, d, len(dirTable[indx]) > 1))

        return result

    def getSmoothPosition(self, v, extraSmoothFactor=1.0):
        vn = self.moveByDirection(v)
        sc = extraSmoothFactor * self.smoothFactor / 2.0
        sc1 = 1.0 - sc
        return (v[0] * sc1 + vn[0] * sc, v[1] * sc1 + vn[1] * sc), (v[0] * sc + vn[0] * sc1, v[1] * sc + vn[1] * sc1)

    def makeSVGAdv(self, grp, greedy):

        verts = self.createVertexesForAdvDrawer()
        qrPathStr = ""
        while len(verts) > 0:
            vertsIndexStart = len(verts) - 1
            vertsIndexCur = vertsIndexStart
            ringIndexes = []
            while True:
                ringIndexes.append(vertsIndexCur)
                nextPos = self.moveByDirection(verts[vertsIndexCur])
                nextIndexes = [i for i, x in enumerate(verts) if x[0] == nextPos[0] and x[1] == nextPos[1]]
                if len(nextIndexes) == 0 or len(nextIndexes) > 2:
                    raise Exception("Vertex " + str(next_c) + " has no connections")
                elif len(nextIndexes) == 1:
                    vertsIndexNext = nextIndexes[0]
                else:
                    if {verts[nextIndexes[0]][2], verts[nextIndexes[1]][2]} != {(verts[vertsIndexCur][2] - 1) % 4, (verts[vertsIndexCur][2] + 1) % 4}:
                        raise Exception("Bad next vertex directions " + str(verts[nextIndexes[0]]) + str(verts[nextIndexes[1]]))

                    # Greedy - CCW turn, proud and neutral CW turn
                    vertsIndexNext = nextIndexes[0] if (greedy == "g") == (verts[nextIndexes[0]][2] == (verts[vertsIndexCur][2] + 1) % 4) else nextIndexes[1]

                if vertsIndexNext == vertsIndexStart:
                    break

                vertsIndexCur = vertsIndexNext

            posStart, _ = self.getSmoothPosition(verts[ringIndexes[0]])
            qrPathStr += "M %f,%f " % self.getSVGPos(posStart[0], posStart[1])
            for ri in range(len(ringIndexes)):
                vc = verts[ringIndexes[ri]]
                vn = verts[ringIndexes[(ri + 1) % len(ringIndexes)]]
                if vn[2] != vc[2]:
                    if (greedy != "n") or not vn[3]:
                        # Add bezier
                        # Opt length http://spencermortensen.com/articles/bezier-circle/
                        # c = 0.552284749
                        ex = 1 - 0.552284749
                        _, bs = self.getSmoothPosition(vc)
                        _, bp1 = self.getSmoothPosition(vc, ex)
                        bp2, _ = self.getSmoothPosition(vn, ex)
                        bf, _ = self.getSmoothPosition(vn)
                        qrPathStr += "L %f,%f " % self.getSVGPos(bs[0], bs[1])
                        qrPathStr += "C %f,%f %f,%f %f,%f " \
                                     % (self.getSVGPos(bp1[0], bp1[1]) + self.getSVGPos(bp2[0], bp2[1]) +
                                        self.getSVGPos(bf[0], bf[1]))
                    else:
                        # Add straight
                        qrPathStr += "L %f,%f " % self.getSVGPos(vn[0], vn[1])

            qrPathStr += "z "

            # Delete already processed vertex
            for i in sorted(ringIndexes, reverse=True):
                del verts[i]

        path = PathElement()
        path.set('d', qrPathStr)
        grp.append(path)

    def getSVGDrawer(self, drawtype):
        drawerDict = {"neutral": lambda g: self.makeSVGAdv(g, "n"),
                      "greedy": lambda g: self.makeSVGAdv(g, "g"),
                      "proud": lambda g: self.makeSVGAdv(g, "p"),
                      "simple": lambda g: self.makeSVGPath(g, "h 1 v 1 h -1"),
                      "circle": self.makeSVGCircle,
                      "pathcustom": lambda g: self.makeSVGPath(g, self.symbolId),
                      "symbol": self.makeSVGSymbol,
                      "obsolete": self.makeSVGRect
                      }
        return drawerDict.get(drawtype)

    def makeSVG(self, grp, drawtype):
        drawer = self.getSVGDrawer(drawtype)
        if drawer is None:
            raise Exception("Unknown draw type: " + drawtype)

        canvas_width = (self.colCount() + 2 * self.margin) * self.boxsize
        canvas_height = (self.rowCount() + 2 * self.margin) * self.boxsize*self.yscale

        # white background providing margin:
        rect = Rectangle()
        rect.set('x', '0')
        rect.set('y', '0')
        rect.set('width', str(canvas_width))
        rect.set('height', str(canvas_height))
        rect.set('style', 'fill:%s;stroke:none' % ("black" if self.invertCode else "white"))
        #grp.append(rect)

        qrg = Group()
        qrg.set('style', 'fill:%s;stroke:none' % ("white" if self.invertCode else "black"))
        drawer(qrg)

        grp.append(qrg)

