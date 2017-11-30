"""
Python barcode renderer for RSS-14 barcodes. Designed for use with Inkscape.
"""

from Base import Barcode

gs=[
  [0,183063,17,9,6,3,28],
  [183064,820063,13,13,5,4,728],
  [820064,1000775,9,17,3,6,6454],
  [1000776,1491020,15,11,5,4,203],
  [1491021,1979844,11,15,4,5,2408],
  [1979845,1996938,19,7,8,1,1],
  [1996939,2013570,7,19,1,8,16632],
]

csw=[
  [1,3,9,27,81,65,17,51,64,14,42,37,22,66],
  [20,60,2,6,18,54,73,41,34,13,39,28,84,74],
]

cssq=[
  0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
  16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,
  32,33,34,35,36,37,38,39,40,41,42,43,45,52,57,63,
  64,65,66,73,74,75,76,77,78,79,82,126,127,128,129,130,
  132,141,142,143,144,145,146,210,211,212,213,214,215,216,217,220,
  316,317,318,319,320,322,323,326,
]

def combins(n,m):
  if n-m>m:
    mind=m
    maxd=n-m
  else:
    mind=n-m
    maxd=m
  i=n
  j=1
  s=1
  while i>maxd:
    s*=i
    i-=1
    if j<=mind:
      s/=j
      j+=1
  while j<=mind:
    s/=j
    j+=1
  return s

class RSS14l(Barcode):
    # Convert a text into string binary of black and white markers
    name="RSS-14 Limited"
      
    def getRSSwidths(self,val,n,elements,maxWidth,noNarrow):
      widths=[0 for i in range(elements)]
      narrowMask=0
      for bar in range(elements-1):
        elmWidth=1
        narrowMask|=(1<<bar)
        while True:
          subVal=combins(n-elmWidth-1,elements-bar-2)
          if ((not noNarrow) and (narrowMask==0) and (n-elmWidth-(elements-bar-1)>=elements-bar-1)):
            subVal-=combins(n-elmWidth-(elements-bar),elements-bar-2)
          if elements-bar-1>1:
            lessVal=0
            for mxwElement in range(n-elmWidth-(elements-bar-2),maxWidth,-1):
              lessVal+=combins(n-elmWidth-mxwElement-1,elements-bar-3)
            subVal-=lessVal*(elements-1-bar)
          elif n-elmWidth>maxWidth:
            subVal-=1
          val-=subVal
          if val<0:
            break
          elmWidth+=1
          narrowMask&=~(1<<bar)
        val+=subVal
        n-=elmWidth
        widths[bar]=str(elmWidth)
      widths[elements-1]=str(n)
      return widths
    
    def getWidths(self,val):
      for g in gs:
        if val>=g[0] and val<=g[1]:
          break
      vo=(val-g[0])/g[6]
      ve=(val-g[0])%g[6]
      wo=self.getRSSwidths(vo,g[2],7,g[4],1)
      we=self.getRSSwidths(ve,g[3],7,g[5],0)
      ws=[0]*14
      for i in range(7):
         ws[i*2]=wo[i]
      for i in range(7):
         ws[i*2+1]=we[i]
      return ws
      
    def checksum(self,ws,csw):
      s=0
      for i in range(14):
        s+=int(ws[i])*csw[i]
      return s
    
    def getChecksum(self, number, magic=10):
      """Generate a UPCA/EAN13/EAN8 Checksum"""
      weight = [3,1] * len(number)
      result = 0
      # We need to work from left to right so reverse
      number = number[::-1]
      # checksum based on first digits.
      for i in range(len(number)):
         result += int(number[i]) * weight[i]
      # Modulous result to a single digit checksum
      checksum = magic - (result % magic)
      if checksum < 0 or checksum >= magic:
         return '0'
      return str(checksum)
 
    def encode(self,text):
      if not text.isdigit():
            return self.error(text, 'Not a Number, must be digits 0-9 only')
      if len(text)>14:
        return self.error(text,'Wrong size, must not exceed 14 digits, check digit will be ignored')
      if len(text)==14:
        text=text[0:-1]
      if len(text)<13:
        text='0'*(13-len(text))+text
      if (text[0]!='0' and text[0]!='1'):
        return self.error(text,'Wrong code, the first digit must be 0 or 1')
      self.label='(01)'+text+self.getChecksum(text)
      v=int(text)
      #v+=10000000000000
      lpair=v/2013571
      rpair=v%2013571
      wsl=self.getWidths(lpair)
      wsr=self.getWidths(rpair)
      
      cs=self.checksum(wsl,csw[0])
      cs+=self.checksum(wsr,csw[1])
      cs%=89
      fpo=self.getRSSwidths(cssq[cs]/21,8,6,3,1)
      fpe=self.getRSSwidths(cssq[cs]%21,8,6,3,1)
      
      fp=['1']*14
      for i in range(6):
         fp[i*2]=fpo[i]
      for i in range(6):
         fp[i*2+1]=fpe[i]
     
      r=''.join(['1','1']+wsl+fp+wsr+['1','1'])
      self.r=r
      s=''
      for i in range(len(r)):
        c='0' if i%2==0 else '1'
        s+=c*int(r[i])
      return s

    def fontSize(self):
        """Return the ideal font size, defaults to 9px"""
        return 6

if __name__ == '__main__':
  r=RSS14l({ 'text':'1234567890|231231312312312|77'})
  r.encode('9876543210')
  print r.r