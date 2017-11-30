import util,constants
import rs
from bisect import bisect_left

def make(data=None, **kwargs):
    hx = Hanxin(**kwargs)
    hxdata=util.HXData(data,util.MODE_BINARY,False)
    hx.add_data(hxdata)
    return 
    
def _check_version(version):
    if version < 1 or version > 84:
        raise ValueError(
            "Invalid version (was %d, expected 1 to 84)" % version)

class Hanxin:

    def __init__(self, version=None,
                 error_correction=constants.ERROR_CORRECT_L1,
                 border=3,
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

    def add_data(self, data):
        if isinstance(data, util.HXData):
            self.data_list.append(data)
        else:
          #    if optimize:
          #        self.data_list.extend(util.optimal_data_chunks(data))
          #    else:
          self.data_list.append(util.HXData(data))
        self.data_cache = None

    def make(self, fit=True):
        """
        :param fit: If ``True`` (or if a size has not been provided), find the
            best fit for the data to avoid data overflow errors.
        """
        self.buffer = util.BitBuffer()
        util.generate_data(self.buffer,self.data_list)
        
        if fit or (self.version is None):
            self.best_fit(start=self.version)
        self.makeImpl(False, self.best_mask_pattern())

    def makeImpl(self, test, mask_pattern):
        _check_version(self.version)
        n=self.modules_count = self.version * 2 + 21
        self.modules = [None] * self.modules_count

        for row in xrange(self.modules_count):

            self.modules[row] = [None] * self.modules_count

            for col in xrange(self.modules_count):
              if (row<9 and (col<9 or col>n-10)) or row>n-10 and (col<9 or col>n-10):
                self.modules[row][col] = False   # (col + row) % 3
              else:
                self.modules[row][col] = None   # (col + row) % 3
            
        self.setup_position_probe_pattern(0, 0,0)
        self.setup_position_probe_pattern(self.modules_count - 1, 0,1)
        self.setup_position_probe_pattern(self.modules_count - 1, self.modules_count - 1,2)
        self.setup_position_probe_pattern(6, self.modules_count - 7,1)
        self.setup_revise_polyline()
        if self.data_cache is None:
            self.data_cache = util.create_data(
                self.version, self.error_correction, self.buffer)
        
        self.map_data(self.data_cache, mask_pattern)
        self.setup_type_info(mask_pattern)

    def setup_type_info(self, mask_pattern):
      dcdata=[0,0,0]
      dcdata[0]=((self.version+20)>>4)
      dcdata[1]=((self.version+20)&0xf)
      dcdata[2]=(self.error_correction<<2)|mask_pattern

      r=rs.RS(4,0x3,1)
      ecdata=r.encode(dcdata,3,4)
           
      dcdata=dcdata+ecdata
      dcdata+=[0xa,0xa]
      n=self.modules_count
      for i in xrange(34):
        if i<9:
          x=i
          y=8
        elif i<17:
          x=8
          y=7-(i-9)
        elif i<26:
          x=n-1-8
          y=(i-17)
        else:
          x=n-8+(i-26)
          y=8
        self.modules[y][x]=(dcdata[i//4]&(1<<(3-i%4)))!=0
        self.modules[n-1-y][n-1-x]=(dcdata[i//4]&(1<<(3-i%4)))!=0

    def setup_position_probe_pattern(self, col,row, rot):
        stx=col
        sty=row
        for i in range(7):
          stx=col
          for j in range(7):
            if (i!=1 or j==0) and (j!=1 or i==0)\
              and (i!=3 or j==2 or j==0) and (j!=3 or i==2 or i==0):
             self.modules[sty][stx]=True
            stx+=(1 if (rot==0 or rot==3) else -1)
          sty+=(1 if rot<2 else -1)
            

    def setup_revise_polyline(self):
      if util.RP_K[self.version]<=0:
        return
      n=self.modules_count
      k=util.RP_K[self.version]
      r=util.RP_R[self.version]
      if self.version>10:
        m=(n-r)//k
      else:
        m=1
      for t in xrange(m+2):
        if t==0:
          stx=0
        else:
          stx=n-1-(m+1-t)*k
        for s in xrange(m+1):
          if (s+t)%2==(0 if m%2==1 else 1):
            sty=s*k
            if t==m+1 and s==0:
              continue
            if s==m:
              ll=n-1-k*m
            else:
              ll=k
            for w in xrange(ll+1):
              if not ((stx==0 or stx==n-1) and (sty<=8 or sty>=n-9)):
                self.modules[sty][stx]=True
                if stx>0 and sty+1<n and (stx<n-1 or w<ll) and not ((stx==0 or stx==n-1) and (sty<=9 or sty>=n-10)):
                  self.modules[sty+1][stx-1]=False
              sty+=1
            if t==0 and sty-ll>8:
              self.modules[sty-ll][stx]=False
              self.modules[sty-ll][stx+1]=False
              self.modules[sty-ll-2][stx]=False
              self.modules[sty-ll-2][stx+1]=False
              self.modules[sty-ll-1][stx+1]=False
            if t==m+1 and sty<n-9:
              self.modules[sty][stx]=False
              self.modules[sty][stx-1]=False
              self.modules[sty-2][stx]=False
              self.modules[sty-2][stx-1]=False
              self.modules[sty-1][stx-1]=False
      for t in xrange(m+2):
        if t==m+1:
          sty=n-1
        else:
          sty=t*k
        for s in xrange(m+1):
          if (s+t)%2==(1 if m%2==1 else 0):
            if s==0:
              stx=0
            else:
              stx=n-1-(m+1-s)*k
            if t==0 and s==m:
              continue
            if s==0:
              ll=n-1-k*m
            else:
              ll=k
            for w in xrange(ll+1):
              if not ((sty==0 or sty==n-1) and (stx<=8 or stx>=n-9)):
                self.modules[sty][stx]=True
                if sty<n-1 and w!=ll:
                  self.modules[sty+1][stx]=False
              stx+=1
            if t==0 and stx-ll>8:
              self.modules[sty][stx-ll]=False
              self.modules[sty+1][stx-ll]=False
              self.modules[sty][stx-ll-2]=False
              self.modules[sty+1][stx-ll-2]=False
              self.modules[sty+1][stx-ll-1]=False
            if t==m+1 and stx<n-9:
              self.modules[sty][stx]=False
              self.modules[sty-1][stx]=False
              self.modules[sty][stx-2]=False
              self.modules[sty-1][stx-2]=False
              self.modules[sty-1][stx-1]=False
      self.modules[0][n-k-1]=True
      self.modules[0][n-k-1+1]=False
      self.modules[0][n-k-1-1]=False
      self.modules[1][n-k-1-1]=False
      self.modules[1][n-k-1]=False
      self.modules[1][n-k-1+1]=False
      self.modules[k][n-1]=True
      self.modules[k-1][n-1]=False
      self.modules[k+1][n-1]=False
      self.modules[k-1][n-2]=False
      self.modules[k][n-2]=False
      self.modules[k+1][n-2]=False
            
      
    def best_fit(self, start=None):
        """
        Find the minimum size required to fit in the data.
        """
        if start is None:
            start = 1
        _check_version(start)

        # Corresponds to the code in util.create_data, except we don't yet know
        # version, so optimistically assume start and check later
 
        needed_bits = len(self.buffer)
        self.version = bisect_left(util.BIT_LIMIT_TABLE[self.error_correction],
                                   needed_bits, start)
        if self.version >=85:
            raise OverflowError('Too many characters')

        return self.version
        
    def best_mask_pattern(self):
        min_lost_point = 0
        pattern = 0

        for i in xrange(4):
            self.makeImpl(True, i)

            lost_point = util.lost_point(self.modules)

            if i == 0 or min_lost_point > lost_point:
                min_lost_point = lost_point
                pattern = i

        return pattern

    def map_data(self, data, mask_pattern):

        n=self.modules_count
        
        mask_func = util.mask_func(mask_pattern)

        data_len = len(data)
        
        x=y=0
        t=(data_len-1)//13+1
        for i in xrange(13):
          for j in xrange(t):
            if j*13+i<data_len:
              c=data[j*13+i]
            else:
              continue
            for k in xrange(8):
              while x<n and y<n and self.modules[y][x]!=None:
                x+=1
                if x>=n:
                  x=0
                  y+=1
              if x>=n or y>=n:
                break
              self.modules[y][x]=((c&0x80)!=0);
              if (mask_func(y+1,x+1)):
                self.modules[y][x]=not self.modules[y][x]
              c<<=1
        while y<n:
          while x<n:
            if self.modules[y][x]==None:
              self.modules[y][x]=(mask_func(y+1,x+1))
            x+=1
          x=0
          y+=1
                    
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
