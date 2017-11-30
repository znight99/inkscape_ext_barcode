# -*- coding: utf-8 -*-
import util
from constants import *
import rs
from bisect import bisect_left

def make(data=None, **kwargs):
    hx = GridMatrix(**kwargs)
    hxdata=util.GMData(data,util.MODE_BYTE,False)
    hx.add_data(hxdata)
    return 
    
def _check_version(version):
    if version < 1 or version > 13:
        raise ValueError(
            "Invalid version (was %d, expected 1 to 13)" % version)

class GridMatrix:

    def __init__(self, version=None,
                 error_correction=3,
                 border=6,
                 ):
        self.version = version and int(version)
        self.error_correction = int(error_correction)
        self.border = int(border)
        
        self.clear()

    def clear(self):
        """
        Reset the internal data.
        """
        self.modules = None
        self.modules_count = 0
        self.data_cache = None
        self.data_list = []

    def add_data(self, data,optimize=True):
        if isinstance(data, util.GMData):
            self.data_list.append(data)
        else:
          #if optimize:
          #  self.data_list.extend(util.optimal_data_chunks(data))
          #else:
            self.data_list.append(util.GMData(data))

        self.data_cache = None

    def make(self, fit=True):
        """
        :param fit: If ``True`` (or if a size has not been provided), find the
            best fit for the data to avoid data overflow errors.
        """
        self.buffer = util.BitBuffer()
        util.generate_data(self.buffer, self.data_list)
        
        if fit or (self.version is None):
            self.best_fit(start=self.version)
        
        if self.version==1 and self.error_correction==1:
          self.error_correction=2
        
        self.makeImpl(False)

    def makeImpl(self, test):
        _check_version(self.version)
        self.block_count=self.version * 2 + 1
        n=self.modules_count = self.block_count*6
        self.modules = [None] * self.modules_count

        for row in xrange(self.modules_count):

            self.modules[row] = [None] * self.modules_count

            for col in xrange(self.modules_count):
              if col%6==0 or col%6==5 or row%6==0 or row%6==5:
                if (row//6+col//6)%2==0:
                  self.modules[row][col] = True   # (col + row) % 3
                else:
                  self.modules[row][col] = False   # (col + row) % 3
              else:
                self.modules[row][col] = None   # (col + row) % 3
        
        ct=self.version
        for row in xrange(self.block_count):
          for col in xrange(self.block_count):
            lm=(5+max(abs(row-ct),abs(col-ct))-self.error_correction)%4
            if self.error_correction==1:
              lm=3-lm
            self.modules[row*6+1][col*6+1]=(lm&2)!=0
            self.modules[row*6+1][col*6+2]=(lm&1)!=0
            
        if self.data_cache is None:
            self.data_cache = util.create_data(
                self.version, self.error_correction, self.buffer)
        self.map_data(self.data_cache)            
      
    def best_fit(self, start=None):
        """
        Find the minimum size required to fit in the data.
        """
        if start is None:
            start = 1
        _check_version(start)

        # Corresponds to the code in util.create_data, except we don't yet know
        # version, so optimistically assume start and check later

        d = (len(self.buffer)+6)//7
        
        ec=self.error_correction
        if start==1 and ec==1:
          ec=2
        cm=(10*d+10-ec-1)//(10-ec)
        
        self.version = bisect_left(TOTAL_CODEWORD_NUM,
                                   cm, start)
        if self.version >13:
            raise OverflowError('Too many characters')

        c=pow((2*self.version+1),2)*2
        ec=((c-d)*10)//c
        if ec>5:
          ec=5
        self.error_correction=ec
        
        return self.version
        
    def map_data(self, data):

        n=self.block_count
        bx=self.version
        by=self.version
        i=0
        j=0
        while True:
          
          for t in xrange(i//2+1):
            for k in xrange(14):
                self.modules[by*6+(k+2)//4+1][bx*6+(k+2)%4+1]=(data[j+(1-k//7)]&(1<<(6-k%7)))!=0
            j+=2
            bx+=[0,1,0,-1][i%4]
            by+=[-1,0,1,0][i%4]
            if bx<0 or bx>=n*6 or by<0 or by>=n*6:
              break
          if bx<0 or bx>=n*6 or by<0 or by>=n*6:
            break

          i+=1
            
          
                    
    def get_matrix(self):
        """
        Return the symbol as a multidimensonal array, including the border.

        To return the array without a border, set ``self.border`` to 0 first.
        """
        if self.data_cache is None:
            self.make()

        if not self.border:
            return self.modules

        width = len(self.modules) + self.border*2
        code = [[False]*width] * self.border
        x_border = [False]*self.border
        for module in self.modules:
            code.append(x_border + module + x_border)
        code += [[False]*width] * self.border

        return code
