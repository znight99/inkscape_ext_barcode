# -*- coding: utf-8 -*-
import util
from constants import *
import rs

def make(data=None, **kwargs):
    hx = CompactMatrix(**kwargs)
    hxdata=util.CMData(data,util.MODE_BYTE,False)
    hx.add_data(hxdata)
    return 
    
def _check_version(version,segments):
    if version < 1 or version > 32:
        raise ValueError(
            "Invalid version (was %d, expected 1 to 32)" % version)
    if segments < 1 or segments > 32:
        raise ValueError(
            "Invalid segments (was %d, expected 1 to 32)" % segments)

class CompactMatrix:

    def __init__(self, version=None,segments=None,
                 error_correction=1,
                 border=6,
                 ):
        self.version = version and int(version)
        self.segments = segments and int(segments)
        self.error_correction = int(error_correction)
        self.interleave=False #True
        
        self.border = int(border)
        
        self.clear()

    def clear(self):
        """
        Reset the internal data.
        """
        self.modules = None
        self.modules_width = 0
        self.modules_height = 0
        self.data_cache = None
        self.data_list = []

    def add_data(self, data,optimize=True):
        if isinstance(data, util.CMData):
            self.data_list.append(data)
        else:
          #if optimize:
          #  self.data_list.extend(util.optimal_data_chunks(data))
          #else:
            self.data_list.append(util.CMData(data))
        #self.data_list=[util.CMData('深圳矽感科技有限公司',MODE_CHINESE),util.CMData('COMPACT MATRIX',MODE_UPPERCASE)]
        self.data_cache = None

    def make(self, fit=True):
        """
        :param fit: If ``True`` (or if a size has not been provided), find the
            best fit for the data to avoid data overflow errors.
        """
        self.buffer = util.BitBuffer()
        util.generate_data(self.buffer, self.data_list)

        if fit or (self.version is None or self.segments is None):
            self.best_fit(startv=self.version, starts=self.segments)
                
        self.makeImpl(False,self.best_mask_pattern())

    def makeImpl(self, test, mask_pattern):
        _check_version(self.version,self.segments)

        n=self.modules_width=34*self.segments+1+START_WIDTH+TERM_WIDTH
        m=self.modules_height=15*self.version+3
        self.modules = [None] * self.modules_height

        for row in xrange(self.modules_height):

            self.modules[row] = [None] * self.modules_width

            for col in xrange(self.modules_width):
              if ((col-START_WIDTH)%34==0 and (row>=3 and row<m-3)) or col>=START_WIDTH and col<n-TERM_WIDTH and (
                  row==0 or row==2 or row==m-1 or row==m-3 or (row==1 or row==m-2) and (col-START_WIDTH)%2==0):
                self.modules[row][col]=True
              elif col>=START_WIDTH and col<n-TERM_WIDTH and (row==1 or row==m-2) and (col-START_WIDTH)%2==1:
                self.modules[row][col]=False
        
        self.setup_start_term()
                    
        if self.data_cache is None:
            self.data_cache = util.create_data(
                self.version, self.segments, self.error_correction, self.interleave,self.buffer)
                
        self.setup_segment_info(mask_pattern,self.interleave)

        self.map_data(self.data_cache, mask_pattern)
        
    def setup_start_term(self):
      for row in range(len(self.modules)):
        c=START_MARK[row%len(START_MARK)]!='0'
        for i in range(START_WIDTH):
          self.modules[row][i]=c
        c=TERM_MARK[row%len(TERM_MARK)]!='0'
        for i in range(TERM_WIDTH):
          self.modules[row][len(self.modules[0])-i-1]=c

    def setup_segment_info(self,mask_pattern, interleave):
      for i in range(self.segments):
        dcdata=[ i>>1, (i&1)<<3|((self.segments-1)>>2), (((self.segments-1)&3)<<2)|((self.error_correction-1)>>1), (((self.error_correction-1)&1)<<3)|(mask_pattern<<1)|interleave]
        r=rs.RS(4,0x3,1)
        ecdata=r.encode(dcdata,4,11)
        dcdata+=ecdata
        
        si=[0x155]*7
        if self.version==1:
          si[0]^=((dcdata[0]&0xc)<<5)|((dcdata[1]&8)<<3)|((dcdata[0]&3)<<4)|((dcdata[1]&2)<<2)|((dcdata[6]&0xc)>>1)|((dcdata[7]&8)>>3)
          si[1]^=((dcdata[1]&0x4)<<6)|((dcdata[2]&0xc)<<4)|((dcdata[1]&1)<<5)|((dcdata[2]&3)<<3)|((dcdata[7]&4))|((dcdata[8]&0xc)>>2)
          si[2]^=((dcdata[3]&0xc)<<5)|((dcdata[4]&8)<<3)|((dcdata[3]&3)<<4)|((dcdata[4]&2)<<2)|((dcdata[9]&0xc)>>1)|((dcdata[14]&8)>>3)
          si[3]^=((dcdata[4]&0x4)<<6)|((dcdata[5]&0xc)<<4)|((dcdata[4]&1)<<5)|((dcdata[5]&3)<<3)|((dcdata[14]&0x7))
          si[4]^=((dcdata[6]&0x3)<<7)|((dcdata[7]&2)<<5)|((dcdata[10]&0xc)<<2)|((dcdata[11]&8))|((dcdata[10]&0x3)<<1)|((dcdata[11]&2)>>1)
          si[5]^=((dcdata[7]&0x1)<<8)|((dcdata[8]&3)<<6)|((dcdata[11]&4)<<3)|((dcdata[12]&0xc)<<1)|((dcdata[11]&0x1)<<2)|((dcdata[12]&3))
          si[6]^=((dcdata[9]&0x3)<<7)|((dcdata[13]&0xc)<<2)|((dcdata[13]&3)<<1)
        else:
          si[0]^=((dcdata[0]&0xc)<<5)|((dcdata[1]&0x8)<<3)|((dcdata[0]&0x3)<<4)|((dcdata[1]&0x2)<<2)|((dcdata[2]&0xe)>>1)
          si[1]^=((dcdata[1]&0x4)<<6)|((dcdata[3]&0xc)<<4)|((dcdata[1]&0x1)<<5)|((dcdata[3]&0x3)<<3)|((dcdata[2]&0x1)<<2)|((dcdata[5]&0xc)>>2)
          si[2]^=((dcdata[5]&0xc)<<5)|((dcdata[6]&0x8)<<3)|((dcdata[5]&0x3)<<4)|((dcdata[6]&0x2)<<2)|((dcdata[5]&0x3)<<1)|((dcdata[8]&0x8)>>3)
          si[3]^=((dcdata[6]&0x4)<<6)|((dcdata[7]&0xc)<<4)|((dcdata[6]&0x1)<<5)|((dcdata[7]&0x3)<<3)|((dcdata[8]&0x7))
          si[4]^=((dcdata[9]&0xc)<<5)|((dcdata[10]&0x8)<<3)|((dcdata[9]&0x3)<<4)|((dcdata[10]&0x2)<<2)|((dcdata[11]&0xe)>>1)
          si[5]^=((dcdata[10]&0x4)<<6)|((dcdata[12]&0xc)<<4)|((dcdata[10]&0x1)<<5)|((dcdata[12]&0x3)<<3)|((dcdata[11]&0x1)<<2)|((dcdata[14]&0xc)>>2)
          si[6]^=((dcdata[13]&0xc)<<5)|((dcdata[13]&0x3)<<4)|((dcdata[14]&0x3)<<1)
              
        for j in range(7):
          x=START_WIDTH+1+i*34+(j//(5*self.version-1))*3
          y=15*(self.version)-1-(j%(5*self.version-1))*3
          d=si[j]
          for k in range(9):
            self.modules[y-k%3][x+(k//3)]=(d&(1<<(8-k)))!=0
    

    def best_fit(self, startv=None, starts=None):
        """
        Find the minimum size required to fit in the data.
        """
        if startv is None:
            startv = 1
        if starts is None:
            starts = 1
        _check_version(startv,starts)

        # Corresponds to the code in util.create_data, except we don't yet know
        # version, so optimistically assume start and check later
        
        d = (len(self.buffer)+8)//9
        ec=self.error_correction

        r=float(starts)/(startv*2)
        while starts<=32 and startv<=32:
          c=((5*startv-1)*11-7)*starts
          e=(c*ec*8)//100
          if c-e>d:
            break
          if float(starts)/(startv*2)<r and starts<32:
            starts+=1
          elif startv<32:
            startv+=1
          else:
            raise OverflowError('Too many characters')
            
        self.version=startv
        self.segments=starts
                
        return self.version,self.segments
        
    def best_mask_pattern(self):
        min_lost_point = 0
        pattern = 0

        for i in xrange(4):
            self.makeImpl(True, i)

            lost_point = util.lost_point(self.modules,self.version,self.segments)

            if i == 0 or min_lost_point > lost_point:
                min_lost_point = lost_point
                pattern = i

        return pattern
        
    def map_data(self, data,mask_pattern):
      p=0
      for i in range(self.segments):
        for j in range(7,(self.version*5-1)*11):
          x=START_WIDTH+1+i*34+(j//(5*self.version-1))*3
          xx=j//(5*self.version-1)
          y=15*(self.version)-1-(j%(5*self.version-1))*3
          if p<len(self.data_cache):
            d=data[p]^util.mask_func(mask_pattern,xx,(5*self.version-1-y//3))
            for k in range(9):
              self.modules[y-k%3][x+(k//3)]=(d&(1<<(8-k)))!=0
          p+=1
                    
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
