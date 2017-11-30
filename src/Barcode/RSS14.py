"""
Python barcode renderer for RSS-14 barcodes. Designed for use with Inkscape.
"""

from Base import Barcode

gs16=[
  [0, 160,12,4,8,1,1 ],
  [161, 960,10,6,6,3,10 ],
  [961,2014,8,8,4,5,34],
  [2015,2714,6,10,3,6,70],
  [2715,2840,4,12,1,8,126],
]

gs15=[
  [0, 335,5,10,2,7,4 ],
  [336,1035,7,8,4,5,20 ],
  [1036,1515,9,6,6,3,48 ],
  [1516,1596,11,4,8,1,81],
]

csw=[
  [1,3,9,27,2,6,18,54],
  [4,12,36,29,8,24,72,58],
  [16,48,65,37,32,17,51,74],
  [64,34,23,69,49,68,46,59],
]

csws=[
  '38211',
  '35511',
  '33711',
  '31911',
  '27411',
  '25611',
  '23811',
  '15711',
  '13911',
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

class RSS14(Barcode):
    # Convert a text into string binary of black and white markers
    name="RSS-14"
      
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
    
    def getWidths(self,val,outer):
      if outer:
        gs=gs16
      else:
        gs=gs15
      for g in gs:
        if val>=g[0] and val<=g[1]:
          break
      if outer:
        vo=(val-g[0])/g[6]
        ve=(val-g[0])%g[6]
      else:
        vo=(val-g[0])%g[6]
        ve=(val-g[0])/g[6]
      wo=self.getRSSwidths(vo,g[2],4,g[4],0 if not outer else 1)
      we=self.getRSSwidths(ve,g[3],4,g[5],0 if outer else 1)
      ws=[0]*8
      for i in range(4):
         ws[i*2]=wo[i]
      for i in range(4):
         ws[i*2+1]=we[i]
      return ws
      
    def checksum(self,ws,csw):
      s=0
      for i in range(8):
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
      self.label='(01)'+text+self.getChecksum(text)
      v=int(text)
      #v+=10000000000000
      lpair=v/4537077
      rpair=v%4537077
      clout=lpair/1597
      clin=lpair%1597
      crout=rpair/1597
      crin=rpair%1597
      wslo=self.getWidths(clout,True)
      wsli=self.getWidths(clin,False)
      wsri=self.getWidths(crin,False)
      wsro=self.getWidths(crout,True)
      
      cs=self.checksum(wslo,csw[0])
      cs+=self.checksum(wsli,csw[1])
      cs+=self.checksum(wsri,csw[3])
      cs+=self.checksum(wsro,csw[2])
      cs%=79
      if cs>=8:
        cs+=1
      if cs>=72:
        cs+=1
      lcs=cs/9
      rcs=cs%9
      
      lfp=list(csws[lcs])
      rfp=list(csws[rcs])
      
      wsli.reverse()
      rfp.reverse()
      wsro.reverse()
      r=''.join(['1','1']+wslo+lfp+wsli+wsri+rfp+wsro+['1','1'])
      s=''
      for i in range(len(r)):
        c='0' if i%2==0 else '1'
        s+=c*int(r[i])
      return s

    def fontSize(self):
        """Return the ideal font size, defaults to 9px"""
        return 8

if __name__ == '__main__':
  r=RSS14({ 'text':'1234567890|231231312312312|77'})
  r.encode('2401234567890')
  #print r.r