from constants import *
import rs

CONTROL_CODE='!"#$%&,()*+,-./:;<=>?@[\\]^_`{|}~'

CHAR_MAP={
   ' ':1000,'+':1003,'-':1006,'.':1009,',':1012,'\n':1015,'\r':1015
}

class RSBlock:

    def __init__(self, total_count, data_count):
        self.total_count = total_count 
        self.data_count = data_count

def mask_func(mask_pattern,i,j):
    if mask_pattern==0:
      return 0xaa if (i+j)%2==0 else 0x155
    elif mask_pattern==1:
      return 0xba if (i+j)%2==0 else 0x145
    elif mask_pattern==2:
      return 0x193 if (i+j)%2==0 else 0x129
    elif mask_pattern==3:
      return 0x55 if (i+j)%2==0 else 0xab

def lost_point(modules,v,s):

    lost_point = 0

    lost_point += _lost_point_level1(modules,  v,s)
    lost_point += _lost_point_level2(modules,  v,s)
    lost_point += _lost_point_level3(modules,  v,s)

    return lost_point

def _lost_point_level1(modules,v,s):
    c=0
    y0=3
    for k in range(s):
      x0=START_WIDTH+1+k*34
      for i in range(33):
        f=True
        for j in range(v*15-3):
          if not modules[j+y0][i+x0]:
            f=False
            break
        if f:
          c+=1
    return c*10000

def _lost_point_level2(modules, v,s):
    c=0
    y0=3
    for k in range(s):
      x0=START_WIDTH+1+k*34
      for i in range(33-2):
        for j in range(v*15-3-2):
          t=modules[j+y0][i+x0]
          if modules[j+y0][i+x0+1]==t and modules[j+y0][i+x0+2]==t and modules[j+y0+1][i+x0]==t and modules[j+y0+1][i+x0+1]==t\
             and modules[j+y0+1][i+x0+2]==t and modules[j+y0+2][i+x0]==t and modules[j+y0+2][i+x0+1]==t and modules[j+y0+2][i+x0+2]==t:
            c+=1 
    return c*3

def _lost_point_level3(modules, v,s):
    c=0
    y0=3
    for k in range(s):
      x0=START_WIDTH+1+k*34
      for i in range(33):
        for j in range(v*15-3):
          if modules[j+y0][i+x0]:
            c+=1

    return abs(50-(c*100//(s*33*(v*15-3))))*100

def to_bytestring(data):
    """
    Convert data to a (utf-8 encoded) byte-string if it isn't a byte-string
    already.
    """
    if not isinstance(data, str ):
        data = unicode(data).encode('utf-8')
    return data

def is_number(data):
  g=[]
  sym=' '
  pos_sym=-1
  loc_sym=-1
  i=0
  while i<len(data):
    c=data[i]
    if c>='0' and c<='9':
      g.append(ord(c)-48)
      if len(g)==3:
        g=[]
        pos_sym=-1
        loc_sym=-1
    elif pos_sym<0 and (c==' ' or c=='+' or c=='-' or c=='.' or c==','):
      pos_sym=len(g)
      loc_sym=i
      sym=c
    elif pos_sym<0 and c=='\r':
      c2=data[i+1] if i+1<len(data) else 0
      if c2=='\n':
        pos_sym=len(g)
        loc_sym=i
        sym=c2
        i+=1
      else:
        return i
    else:
      return i
    i+=1
  if len(g)>0:
    pass
  elif pos_sym>=0:
    return loc_sym
  return -1
  
def is_lowercase(data):
  for i in range(len(data)):
    c=data[i]
    if c>='a' and c<'z' or c==' ':
      pass
    else:
      return i
  return -1

def is_uppercase(data):
  for i in range(len(data)):
    c=data[i]
    if c>='A' and c<'Z' or c==' ':
      pass
    else:
      return i
  return -1

def is_alphanum(data):
  for i in range(len(data)):
    c=data[i]
    if c>='0' and c<='9' or c>='A' and c<='Z' or c>='a' and c<='z' or c==' ':
      pass
    else:
      return i
  return -1

def is_control(data):
  for i in range(len(data)):
    c=data[i]
    if ord(c)<0 or ord(c)>127:
      return i
    elif ord(c)>=0 and ord(c)<=31 or CONTROL_CODE.find(c)>=0:
      pass
    else:
      return i
  return -1

def is_text(data):
  for i in range(len(data)):
    c=data[i]
    if ord(c)>=0 and ord(c)<127:
      pass
    else:
      return i
  return -1

def is_chinese(data):
    return True

def control_count(data):
  t=0
  for c in data:
    if ord(c)>=0 and ord(c)<=31 or CONTROL_CODE.find(c)>=0:
      t+=1
  return t

def optimal_data_chunks(mdata):
  try:
    data=unicode(mdata,'utf-8').encode('gb18030')
  except UnicodeEncodeError:
    return [CMData(mdata)]
  except UnicodeDecodeError:
    return [CMData(mdata)]

  ll=len(data)
  ms=[None]*ll
  i=0
  while i<ll:
    c=data[i]
    if ord(c)>=0x81 and ord(c)<=0xfe:
      c2=data[i+1] if i+1<ll else 0
      if ord(c)>=0xa1 and ord(c)<=0xa9 and ord(c2)>=0xa0 and ord(c2)<=0xff:
        ms[i]=ms[i+1]=MODE_CHINESE
      elif ord(c)>=0xb0 and ord(c)<=0xf7 and ord(c2)>=0xa0 and ord(c2)<=0xff:
        ms[i]=ms[i+1]=MODE_CHINESE
      i+=2
    else:
      if c>='a' and c<='z':
        ms[i]=MODE_LOWERCASE
      elif c>='A' and c<='Z':
        ms[i]=MODE_UPPERCASE
      i+=1
  i=0
  while i<ll-1:
    c=data[i]
    c2=data[i+1] if i+1<ll else 0
    if c==' ':
      if i-1>=0 and (ms[i-1]==MODE_LOWERCASE or ms[i-1]==MODE_UPPERCASE):
        ms[i]=ms[i-1]
      i+=1
    elif i-1>=0 and ms[i-1]==MODE_CHINESE and (c>='0' and c<='9' and c2>='0' and c2<='9' or c=='\r' and c2=='\n'):
      ms[i]=ms[i+1]=MODE_CHINESE
      i+=2
    else:
      i+=1
  i=ll-1
  while i>0:
    c=data[i]
    c2=data[i-1] if i-1>=0 else 0
    if c==' ':
      if (ms[i] is None) and i+1<ll and (ms[i+1]==MODE_LOWERCASE or ms[i+1]==MODE_UPPERCASE):
        ms[i]=ms[i+1]
      i-=1
    elif (ms[i] is None) and (ms[i-1] is None) and i+1<ll and ms[i+1]==MODE_CHINESE and (c>='0' and c<='9' and c2>='0' and c2<='9' or c=='\r' and c2=='\n'):
      ms[i]=ms[i-1]=MODE_CHINESE
      i-=2
    else:
      i-=1
  i=0
  while i<ll:
    c=data[i]
    if (ms[i] is None) and (c>='0' and c<='9' or c in CHAR_MAP):
      t=i
      while t<ll and ms[t] is None and (data[t]>='0' and data[t]<='9' or data[t] in CHAR_MAP):
        t+=1
      s=is_number(data[i:t])
      if s<0:
        s=t
      else:
        s+=i
      for j in range(i,s):
        ms[j]=MODE_NUMBER
      i=s
    i+=1
  for i in range(ll):
    if ms[i] is None:
      ms[i]=MODE_BYTE
  lm=None
  lp=-1
  r=[]
  for i in range(ll):
    if i+1>=ll or ms[i+1]!=lm:
      ch=data[lp:i+1].decode('gb18030').encode('utf-8')
      r.append(CMData(ch,lm))
      if i+1<ll:
        lm=ms[i+1]
        lp=i+1
  # adjustion needed
  return r
  
def optimal_mode(data):
    """
    Calculate the optimal mode for this chunk of data.
    """
    if is_number(data)<0:
        return MODE_NUMBER
    elif is_lowercase(data)<0:
      return MODE_LOWERCASE
    elif is_uppercase(data)<0:
      return MODE_UPPERCASE
    elif is_text(data)<0:
      if control_count(data)>len(data)*0.3:
        return MODE_BYTE
      else:
        return MODE_ALPHANUM
    # ignore chinese mode
    return MODE_BYTE

class CMData:

    def __init__(self, data, mode=None, check_data=True):
        if check_data:
            data = to_bytestring(data)

        if mode is None:
            self.mode = optimal_mode(data)
        else:
            self.mode = mode
            if mode not in (MODE_CHINESE,MODE_NUMBER, MODE_LOWERCASE,MODE_UPPERCASE,MODE_ALPHANUM,MODE_BYTE,MODE_ECI,MODE_FNC1,MODE_FNC1_2,MODE_FNC2,MODE_FNC3):
                raise TypeError("Invalid mode (%s)" % mode)

        self.data = data

    def __len__(self):
        return len(self.data)

    def write(self, buffer):
        if self.mode==MODE_CHINESE:
          data=unicode(self.data,'utf-8').encode('gb18030')
          i=0
          ll=len(data)
          while i<ll:
            c=data[i]
            if ord(c)>=0xa1 and ord(c)<=0xfe:
              c2=data[i+1] if i+1<ll else 0
              if ord(c)>=0xa1 and ord(c)<0xa9 and ord(c2)>=0xa0 and ord(c2)<=0xff:
                buffer.put((ord(c)-0xa1)*0x60+(ord(c2)-0xa0),13)
              elif ord(c)>=0xb0 and ord(c)<0xf7 and ord(c2)>=0xa0 and ord(c2)<=0xff:
                buffer.put((ord(c)-0xb0+9)*0x60+(ord(c2)-0xa0),13)
              else:
                buffer.put(7777+ord(c),13)
                buffer.put(7777+ord(c2),13)
              i+=2
            else:
              if c=='\r':
                c2=data[i+1] if i+1<ll else 0
                if c2=='\n':
                  buffer.put(7776,13)
                  i+=1
                else:
                  buffer.put(7777+ord(c),13)
              if c>='0' and c<='9':
                c2=data[i+1] if i+1<ll else 0
                if c2>='0' and c2<='9':
                  buffer.put(8033+(ord(c)-48)*10+(ord(c2)-48),13)
                  i+=1
                else:
                  buffer.put(7777+ord(c),13)
              else:
                buffer.put(7777+ord(c),13)
              i+=1
        elif self.mode == MODE_NUMBER:
            d=[]
            g=[]
            sym=' '
            pos_sym=-1
            i=0
            while i<len(self.data):
              c=self.data[i]
              if c>='0' and c<='9':
                g.append(ord(c)-48)
                if len(g)==3:
                  if pos_sym>=0 and sym in CHAR_MAP:
                    d.append(CHAR_MAP[sym]+pos_sym)
                  d.append(g[0]*100+g[1]*10+g[2])
                  g=[]
                  pos_sym=-1
              elif pos_sym<0 and (c==' ' or c=='+' or c=='-' or c=='.' or c==','):
                pos_sym=len(g)
                sym=c
              elif pos_sym<0 and c=='\r':
                c2=self.data[i+1] if i+1<len(self.data) else 0
                if c2=='\n':
                  pos_sym=len(g)
                  sym=c2
                  i+=1
              i+=1
            if len(g)>0:
              buffer.put(3-len(g),2)
              if pos_sym>=0 and sym in CHAR_MAP:
                d.append(CHAR_MAP[sym]+pos_sym)
              g+=[0]*(3-len(g))
              d.append(g[0]*100+g[1]*10+g[2])
            else:
              buffer.put(0,2)
            for t in d:
              buffer.put(t,10)
        elif self.mode == MODE_LOWERCASE:
          for c in self.data:
            if c>='a' and c<'z':
              buffer.put(ord(c)-97,5)
            elif c==' ':
              buffer.put(26,5)
            elif ord(c)>=0 and ord(c)<127:
              buffer.put(125,7)
              if ord(c)>=0 and ord(c)<=31:
                buffer.put(ord(c),6)
              else:
                buffer.put(CONTROL_CODE.find(c)+32,6)
        elif self.mode == MODE_UPPERCASE:
          for c in self.data:
            if c>='A' and c<'Z':
              buffer.put(ord(c)-65,5)
            elif c==' ':
              buffer.put(26,5)
            elif ord(c)>=0 and ord(c)<127:
              buffer.put(125,7)
              if ord(c)>=0 and ord(c)<=31:
                buffer.put(ord(c),6)
              else:
                buffer.put(CONTROL_CODE.find(c)+32,6)
        elif self.mode == MODE_ALPHANUM:
          for c in self.data:
            if c>='0' and c<='9':
              buffer.put(ord(c)-48,6)
            elif c>='A' and c<'Z':
              buffer.put(ord(c)-65+10,6)
            elif c>='a' and c<'z':
              buffer.put(ord(c)-97+36,6)
            elif c==' ':
              buffer.put(62,6)
            elif ord(c)>=0 and ord(c)<127:
              buffer.put(1014,10)
              if ord(c)>=0 and ord(c)<=31:
                buffer.put(ord(c),6)
              else:
                buffer.put(CONTROL_CODE.find(c)+32,6)
        elif self.mode==MODE_ECI:
          ec=int(self.data)
          if ec<=1023:
            buffer.put(ec,11)
          elif ec<=32767:
            buffer.put(ec|0x10000,17)
          elif ec<=999999:
            buffer.put(ec|0x300000,22)
        elif self.mode==MODE_FNC1:
          pass
        elif self.mode==MODE_FNC1_2: # not implement
          pass
        elif self.mode==MODE_FNC2:# not implement
          buffer.put(0,8) # digital signature
          buffer.put(0,4) # CM code number-1
          buffer.put(0,4) # CM code seq no.
        elif self.mode==MODE_FNC3: # not implement
          pass
        else: # MODE_BYTE
          pl=len(self.data)
          cp=0
          while pl>0:
            if pl>16384:
              ll=16384
            else:
              ll=pl
            if cp>0:
              buffer.put(MODE_BYTE,4)
            buffer.put(ll-1,14)
            for c in self.data[cp:cp+ll]:
              buffer.put(ord(c),8)
            cp+=ll
            pl-=ll

    def __repr__(self):
        return repr(self.data)

class BitBuffer:

    def __init__(self):
        self.buffer = []
        self.length = 0

    def __repr__(self):
        return ".".join([str(n) for n in self.buffer])

    def get(self, index):
        buf_index = index // 9
        return ((self.buffer[buf_index] >> (8 - index % 9)) & 1) == 1

    def put(self, num, length):
        for i in xrange(length):
            self.put_bit(((num >> (length - i - 1)) & 1) == 1)

    def __len__(self):
        return self.length

    def put_bit(self, bit):
        buf_index = self.length // 9
        if len(self.buffer) <= buf_index:
            self.buffer.append(0)
        if bit:
            self.buffer[buf_index] |= (1 << (8-self.length % 9))
        self.length += 1

def create_bytes(num, buffer, rs_blocks, interleave):
    offset = 0
  
    rsm=rs.RS(9,0x11,1)

    lb=len(rs_blocks)
    dcdata=[None]*lb
    ml=-1
    for r in xrange(lb):
     
        dcCount = rs_blocks[r].data_count
        ecCount = rs_blocks[r].total_count - dcCount

        dcdata[r] = [0] * dcCount

        for i in xrange(dcCount):
            dcdata[r][i] = 0x1ff & buffer.buffer[i + offset]
        offset += dcCount
        
        ecdata=rsm.encode(dcdata[r],dcCount,ecCount)
        
        dcdata[r]+=ecdata

        if len(dcdata[r])>ml:
          ml=len(dcdata[r])
    if interleave:
      data=[0]*num
      i=0
      sty=0
      stx=0
      while True:
        if stx<lb and sty<len(dcdata[stx]):
          data[i]=dcdata[stx][sty]
          i+=1
        stx+=1
        if stx>=lb:
          stx=0
          sty+=1
          if sty>=ml:
            break
    else:
      data=[]
      for r in range(lb):
        data.extend(dcdata[r])
    
    return data

def shift_to_mode(buffer,last,now):
  if now is None:
    if last in MODE_SHIFT_TABLE:
      buffer.put(MODE_SHIFT_TABLE[last][0],MODE_SHIFT_SIZE[last][0])
    return
  if last is None:
    buffer.put(now,4)
    return
  if last==now:
    return
  if last in MODE_SHIFT_TABLE:
    if now < len(MODE_SHIFT_TABLE[last]) and MODE_SHIFT_TABLE[now]!=-1:
      buffer.put(MODE_SHIFT_TABLE[last][now],MODE_SHIFT_SIZE[last][now])
      return
    buffer.put(MODE_SHIFT_TABLE[last][0],MODE_SHIFT_SIZE[last][0])
  buffer.put(now,4)

def generate_data(buffer,  data_list):
    lastmode=None
    for i in xrange(len(data_list)):
        data=data_list[i]
        if not data.mode is None and len(data.data)>0:
          shift_to_mode(buffer,lastmode,data.mode)
          lastmode=data.mode
          data.write(buffer)
    shift_to_mode(buffer,lastmode,None)

def create_data(version, segments, error_correction, interleave, buffer):
    
    # Calculate the maximum number of bits for the given version.
    d=(len(buffer)+8)//9
    ec=error_correction
    c=((5*version-1)*11-7)*segments
    e=(c*ec*8)//100
    p=c-e-d
    
    if p<0:
        raise OverflowError(
            "Code length overflow. Data size (%s) > size available (%s)" %
            (d, c-e))

    # Delimit the string into 8-bit words, padding with 0s if necessary.
    delimit = len(buffer) % 9
    if delimit:
        for i in xrange(9 - delimit):
            buffer.put_bit(False)

    # Add special alternating padding bitstrings until buffer is full.
    for i in xrange(p):
        buffer.put(PAD0, 9)


    b=(c+510)//511
    if c%b==0:
      n1=c//b
      n2=0
      b1=b
      b2=0
    else:
      n1=(c//b)+1
      n2=n1-1
      b1=c-b*n2
      b2=b-b1
    if e%b==0:
      e1=e//b
      e2=0
      b3=b
      b4=0
    else:
      e1=(e//b)+1
      e2=e1-1
      b3=e-b*e2
      b4=b-b3
    rbs=[]
    for i in xrange(b):
      if i<b1:
        m=n1
      else:
        m=n2
      if i<b3:
        f=e1
      else:
        f=e2
      rbs.append(RSBlock(m,m-f))
      
    
    return create_bytes(c,buffer, rbs, interleave)
