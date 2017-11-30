
class Polynomial:

    def __init__(self, rs, num, shift):
        self.rs=rs
        if not num:
            raise Exception("%s/%s" % (len(num), shift))

        offset = 0

        for item in num:
            if item != 0:
                break
            offset += 1

        self.num = [0] * (len(num) - offset + shift)
        for i in xrange(len(num) - offset):
            self.num[i] = num[i + offset]

    def __getitem__(self, index):
        return self.num[index]

    def __iter__(self):
        return iter(self.num)

    def __len__(self):
        return len(self.num)

    def __mul__(self, other):
        num = [0] * (len(self) + len(other) - 1)

        for i, item in enumerate(self):
            for j, other_item in enumerate(other):
                num[i + j] ^= self.rs.gexp(self.rs.glog(item) + self.rs.glog(other_item))

        return Polynomial(self.rs,num, 0)

    def __mod__(self, other):
        difference = len(self) - len(other)
        if difference < 0:
            return self

        ratio = self.rs.glog(self[0]) - self.rs.glog(other[0])

        num = self[:]

        num = [
            item ^ self.rs.gexp(self.rs.glog(other_item) + ratio)
            for item, other_item in zip(self, other)]
        if difference:
            num.extend(self[-difference:])

        # recursive call
        return Polynomial(self.rs,num, 0) % other

class RS:
  def glog(self,n):
    if n < 1:
        raise ValueError("glog(%s)" % n)
    return self.LOG_TABLE[n]
  
  
  def gexp(self,n):
    return self.EXP_TABLE[n %(len(self.EXP_TABLE)-1)]
    
  def g(self,t):
    rsPoly = Polynomial(self,[1], 0)
    for i in range(t):
        rsPoly = rsPoly * Polynomial(self,[1, self.gexp(i+self.offset)], 0)
    return rsPoly
  
  def __init__(self,n,g,offset):  
    self.offset=offset
    self.EXP_TABLE = [0]*(1<<n)
    self.LOG_TABLE = [0]*(1<<n)

    for i in range(n):
        self.EXP_TABLE[i] = 1 << i

    for i in range(n, 1<<n):
      for j in range(n):
        if (g&(1<<j)):
          self.EXP_TABLE[i] ^= self.EXP_TABLE[i - (n-j)]

    for i in range((1<<n)-1):
        self.LOG_TABLE[self.EXP_TABLE[i]] = i

  def encode(self,dcdata,k,t):
      # Get error correction polynomial.
      n=k+t
      rsPoly=self.g(t)
          
      rawPoly = Polynomial(self,dcdata, len(rsPoly) - 1)

      modPoly = rawPoly % rsPoly

      ecdata = [0] * (len(rsPoly) - 1)
      for i in range(len(ecdata)):
          modIndex = i + len(modPoly) - len(ecdata)
          if (modIndex >= 0):
              ecdata[i] = modPoly[modIndex]
          else:
              ecdata[i] = 0
      return ecdata

if __name__ == '__main__':
  rs=RS(4,0x3,1)
  dc=[1,6,3]
  ec=rs.encode(dc,3,4)
  print str(ec)
  