from constants import *
import rs

class RSBlock:

    def __init__(self, total_count, data_count):
        self.total_count = total_count
        self.data_count = data_count


def rs_blocks(version, error_correction):
    if error_correction not in RS_BLOCK_OFFSET:
        raise Exception("bad rs block @ version: %s / error_correction: %s" %
            (version, error_correction))
    offset = RS_BLOCK_OFFSET[error_correction]
    rs_block = RS_BLOCK_TABLE[(version - 1) * 4 + offset]

    blocks = []

    for i in xrange(0, len(rs_block), 3):
        count, total_count, data_count = rs_block[i:i + 3]
        for j in xrange(count):
            blocks.append(RSBlock(total_count, data_count))

    return blocks

_data_count = lambda block: block.data_count
BIT_LIMIT_TABLE = [
    [0] + [8*sum(map(_data_count, rs_blocks(version, error_correction)))
           for version in xrange(1, 85)]
    for error_correction in xrange(4)
]


def mask_func(pattern):
    """
    Return the mask function for the given mask pattern.
    """
    if pattern == 0:   # 000
        return lambda i, j: False
    if pattern == 1:   # 001
        return lambda i, j: (i+j) % 2 == 0
    if pattern == 2:   # 010
        return lambda i, j: ((i+j)%3+(j%3))%2==0
    if pattern == 3:   # 011
        return lambda i, j: (i%j+j%i+i%3+j%3)%2==0
    raise TypeError("Bad mask pattern: " + pattern)

def lost_point(modules):
    modules_count = len(modules)

    lost_point = 0

    lost_point = _lost_point_level1(modules, modules_count)
    lost_point += _lost_point_level2(modules, modules_count)

    return lost_point

def _lost_point_level1(modules, n):
  s=0
  for i in xrange(n):
    lt=None
    t=0
    for j in xrange(n):
      if modules[i][j]==lt:
        t+=1
      else:
        lt=modules[i][j]
        t=1
      if t==4:
        s+=16
      if t>4:
        s+=4
  for i in xrange(n):
    lt=None
    t=0
    for j in xrange(n):
      if modules[j][i]==lt:
        t+=1
      else:
        lt=modules[j][i]
        t=1
      if t==4:
        s+=16
      if t>4:
        s+=4
  return s  

def _lost_point_level2(modules, modules_count):
    modules_range_short = xrange(modules_count-6)

    lost_point = 0
    for row in xrange(modules_count):
        this_row = modules[row]
        for col in modules_range_short:
            if (this_row[col]
                    and not this_row[col + 1]
                    and this_row[col + 2]
                    and not this_row[col + 3]
                    and this_row[col + 4]
                    and this_row[col + 5]
                    and this_row[col + 6]) or (this_row[col]
                    and this_row[col + 1]
                    and this_row[col + 2]
                    and not this_row[col + 3]
                    and this_row[col + 4]
                    and not this_row[col + 5]
                    and this_row[col + 6]):
                lost_point += 50

    for col in xrange(modules_count):
        for row in modules_range_short:
            if (modules[row][col]
                    and not modules[row + 1][col]
                    and modules[row + 2][col]
                    and not modules[row + 3][col]
                    and modules[row + 4][col]
                    and modules[row + 5][col]
                    and modules[row + 6][col]) or (modules[row][col]
                    and modules[row + 1][col]
                    and modules[row + 2][col]
                    and not modules[row + 3][col]
                    and modules[row + 4][col]
                    and not modules[row + 5][col]
                    and modules[row + 6][col]):
                lost_point += 50

    return lost_point
    
def to_bytestring(data):
    """
    Convert data to a (utf-8 encoded) byte-string if it isn't a byte-string
    already.
    """
    if not isinstance(data, str ):
        data = unicode(data).encode('utf-8')
    return data

def is_text(data):
  for c in data:
    t=ord(c)
    if t>0x1b and t<0x20 or t>0x7f:
      return False
  return True

def is_chinese1(data):
    try:
      data=unicode(data,'utf-8').encode('gb2312')
    except UnicodeEncodeError:
      return False
    except UnicodeDecodeError:
      return False

    i=0
    while i<len(data):
      c=ord(data[i])
      if c>=0x81 and c<=0xfe:
        c2=ord(data[i+1]) if i+1<len(data) else 0
        if c2>=0x30 and c2<=0x39:
          i+=4
          return False
        else:
          if c>=0xb0 and c<=0xd7 and c2>=0xa1 and c2<=0xfe:
              pass
          elif c>=0xa1 and c<=0xa3 and c2>=0xa1 and c2<=0xfe:
              pass
          elif c==0xa8 and c2>=0xa1 and c2<=0xc0:
              pass
          elif c>=0xd8 and c<=0xf7 and c2>=0xa1 and c2<=0xfe:
              return False
          else:
            return False
          i+=2
      else:
        i+=1
        return False
    return True

def is_chinese1or2(data):
    try:
      data=unicode(data,'utf-8').encode('gb2312')
    except UnicodeEncodeError:
      return False
    except UnicodeDecodeError:
      return False

    i=0
    while i<len(data):
      c=ord(data[i])
      if c>=0x81 and c<=0xfe:
        c2=ord(data[i+1]) if i+1<len(data) else 0
        if c2>=0x30 and c2<=0x39:
          i+=4
          return False
        else:
          if c>=0xb0 and c<=0xd7 and c2>=0xa1 and c2<=0xfe:
              pass
          elif c>=0xa1 and c<=0xa3 and c2>=0xa1 and c2<=0xfe:
              pass
          elif c==0xa8 and c2>=0xa1 and c2<=0xc0:
              pass
          elif c>=0xd8 and c<=0xf7 and c2>=0xa1 and c2<=0xfe:
              pass
          else:
            return False
          i+=2
      else:
        i+=1
        return False
    return True

def is_gb18030_2(data):
    try:
      data=unicode(data,'utf-8').encode('gb18030')
    except UnicodeEncodeError:
      return False
    except UnicodeDecodeError:
      return False

    i=0
    while i<len(data):
      c=ord(data[i])
      if c>=0x81 and c<=0xfe:
        c2=ord(data[i+1]) if i+1<len(data) else 0
        if c2>=0x30 and c2<=0x39:
          i+=4
          return False
        else:
          if c2>=0x40 and c2<=0x7e:
            pass
          elif c2>=0x80 and c2<=0xfe:
            pass
          else:
            return False
          i+=2
      else:
        i+=1
        return False
    return True

def is_gb18030_4(data):
    try:
      data=unicode(data,'utf-8').encode('gb18030')
    except UnicodeEncodeError:
      return False
    except UnicodeDecodeError:
      return False

    i=0
    while i<len(data):
      c=ord(data[i])
      if c>=0x81 and c<=0xfe:
        c2=ord(data[i+1]) if i+1<len(data) else 0
        if c2>=0x30 and c2<=0x39:
          c3=ord(data[i+2]) if i+2<len(data) else 0
          c4=ord(data[i+3]) if i+3<len(data) else 0
          if c3>=0x81 and c3<=0xfe and c4>=0x30 and c4<=0x39:
            pass
          else:
            return False
          i+=4
        else:
          i+=2
          return False
      else:
        i+=1
        return False
    return True

def optimal_mode(data):
    """
    Calculate the optimal mode for this chunk of data.
    """
    if data.isdigit():
        return MODE_NUMBER
    elif is_text(data):
        return MODE_TEXT
    #elif is_chinese1or2(data):
    #    s=unicode(data,'utf-8')
    #    if is_chinese1(s[0:1].encode('utf-8')):
    #      return MODE_CHINESE_1
    #    return MODE_CHINESE_2
    #elif is_gb18030_2(data):
    #    return MODE_GB18030_2
    #elif is_gb18030_4(data):
    #    return MODE_GB18030_4
    return MODE_BINARY

TEXT2=' !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

class HXData:

    def __init__(self, data, mode=None, check_data=True):
        if check_data:
            data = to_bytestring(data)

        if mode is None:
            self.mode = optimal_mode(data)
        else:
            self.mode = mode
            if mode not in (MODE_NUMBER, MODE_TEXT, MODE_BINARY,MODE_CHINESE1,MODE_CHINESE2,MODE_GB18030_2,MODE_GB18030_4):
                raise TypeError("Invalid mode (%s)" % mode)
            if check_data and mode < optimal_mode(data):
                raise ValueError(
                    "Provided data can not be represented in mode "
                    "{0}".format(mode))

        self.data = data

    def __len__(self):
        return len(self.data)

    def write(self, buffer):
        if self.mode == MODE_NUMBER:
            for i in xrange(0, len(self.data), 3):
                chars = self.data[i:i + 3]
                buffer.put(int(chars), 10)
            tn=[ 0x3ff,0x3fe,0x3fd ]
            buffer.put(tn[len(self.data)%3],10)
        elif self.mode == MODE_TEXT:
            cp=False
            for c in self.data:
              if c>='0' and c<='9':
                if cp:
                  buffer.put(0x3e,6)
                  cp=False
                b=ord(c)-48
              elif c>='A' and c<='Z':
                if cp:
                  buffer.put(0x3e,6)
                  cp=False
                b=ord(c)-ord('A')+10
              elif c>='a' and c<='z':
                if cp:
                  buffer.put(0x3e,6)
                  cp=False
                b=ord(c)-ord('a')+0x24
              elif ord(c)>=0 and ord(c)<=0x1b:
                if not cp:
                  buffer.put(0x3e,6)
                  cp=True
                b=ord(c)
              elif ord(c)==127:
                if not cp:
                  buffer.put(0x3e,6)
                  cp=True
                b=0x3d
              else:
                if not cp:
                  buffer.put(0x3e,6)
                  cp=True
                b=TEXT2.find(c)+28
              buffer.put(b,6)
            buffer.put(0x3f,6)
        elif self.mode == MODE_CHINESE_1 or self.mode==MODE_CHINESE_2: # input are encoded in gb2312/gb18030
            data=unicode(self.data,'utf-8').encode('gb2312')
            i=0
            st=(self.mode==MODE_CHINESE_1)
            while i<len(data):
              c=ord(data[i])
              if c>=0x81 and c<=0xfe:
                c2=ord(data[i+1]) if i+1<len(data) else 0
                if c>=0xb0 and c<=0xd7 and c2>=0xa1 and c2<=0xfe:
                    if not st:
                      buffer.put(0xffe,12)
                      st=True
                    buffer.put((c-0xb0)*0x5e+(c2-0xa1),12)
                elif c>=0xa1 and c<=0xa3 and c2>=0xa1 and c2<=0xfe:
                    if not st:
                      buffer.put(0xffe,12)
                      st=True
                    buffer.put((c-0xa1)*0x5e+(c2-0xa1)+0xeb0,12)
                elif c==0xa8 and c2>=0xa1 and c2<=0xc0:
                    if not st:
                      buffer.put(0xffe,12)
                      st=True
                    buffer.put((c2-0xa1)+0xfca,12)
                elif c>=0xd8 and c<=0xf7 and c2>=0xa1 and c2<=0xfe:
                    if st:
                      buffer.put(0xffe,12)
                      st=False
                    buffer.put((c-0xd8)*0x5e+(c2-0xa1),12)
                i+=2
              else:
                i+=1
            buffer.put(0xfff,12)
        elif self.mode == MODE_GB18030_2: # input are gb18030
            data=unicode(self.data,'utf-8').encode('gb18030')
            i=0
            while i<len(data):
              c=ord(data[i])
              if c>=0x81 and c<=0xfe:
                c2=ord(data[i+1]) if i+1<len(data) else 0
                if c2>=0x30 and c2<=0x39:
                  i+=4
                else:
                  if c2>=0x40 and c2<=0x7e:
                    buffer.put((c-0x81)*0xbe+(c2-0x40),15)
                  elif c2>=0x80 and c2<=0xfe:
                    buffer.put((c-0x81)*0xbe+(c2-0x41),15)
                  i+=2
              else:
                i+=1
            buffer.put(0x7fff,15)
        elif self.mode == MODE_GB18030_4: # one gb18030 char
            data=unicode(self.data,'utf-8').encode('gb18030')
            i=0
            if i<len(data):
              c=ord(data[i])
              if c>=0x81 and c<=0xfe:
                c2=ord(data[i+1]) if i+1<len(data) else 0
                if c2>=0x30 and c2<=0x39:
                  c3=ord(data[i+2]) if i+2<len(data) else 0
                  c4=ord(data[i+3]) if i+3<len(data) else 0
                  if c3>=0x81 and c3<=0xfe and c4>=0x30 and c4<=0x39:
                        if i>0:
                          buffer.put(MODE_GB18030_4,4)
                        buffer.put((c4-0x30)+(c3-0x81)*0xa+(c2-0x30)*0x4ec+(c-0x81)*0x3138,21)
                  i+=4
                else:
                  i+=2
              else:
                i+=1
        elif self.mode == MODE_ECI: # input is a ECI string like '000009'
            ec=int(self.data)
            if ec<=127:
              buffer.put(ec,8)
            elif ec<=16383:
              buffer.put(ec|0x8000,16)
            elif ec<=999999:
              buffer.put(ec|0xc00000,24)
        else: # MODE_BINARY
            buffer.put(len(self.data),13)
            data = [ord(c) for c in self.data]
            for c in data:
                buffer.put(c, 8)

    def __repr__(self):
        return repr(self.data)

class BitBuffer:

    def __init__(self):
        self.buffer = []
        self.length = 0

    def __repr__(self):
        return ".".join([str(n) for n in self.buffer])

    def get(self, index):
        buf_index = math.floor(index / 8)
        return ((self.buffer[buf_index] >> (7 - index % 8)) & 1) == 1

    def put(self, num, length):
        for i in xrange(length):
            self.put_bit(((num >> (length - i - 1)) & 1) == 1)

    def __len__(self):
        return self.length

    def put_bit(self, bit):
        buf_index = self.length // 8
        if len(self.buffer) <= buf_index:
            self.buffer.append(0)
        if bit:
            self.buffer[buf_index] |= (0x80 >> (self.length % 8))
        self.length += 1

def create_bytes(buffer, rs_blocks):
    offset = 0

    data=[]
    
    rsm=rs.RS(8,0x63,1)

    for r in xrange(len(rs_blocks)):
     
        dcCount = rs_blocks[r].data_count
        ecCount = rs_blocks[r].total_count - dcCount

        dcdata = [0] * dcCount

        for i in xrange(len(dcdata)):
            dcdata[i] = 0xff & buffer.buffer[i + offset]
        offset += dcCount
        
        ecdata=rsm.encode(dcdata,dcCount,ecCount)
                
        data+=dcdata
        data+=ecdata

    return data

def generate_data(buffer,data_list):
    for data in data_list:
        buffer.put(data.mode, 4)
        data.write(buffer)

def create_data(version, error_correction, buffer):
    
    # Calculate the maximum number of bits for the given version.
    rbs = rs_blocks(version, error_correction)
    bit_limit = 0
    for block in rbs:
        bit_limit += block.data_count * 8

    if len(buffer) > bit_limit:
        raise OverflowError(
            "Code length overflow. Data size (%s) > size available (%s)" %
            (len(buffer), bit_limit))

    # Delimit the string into 8-bit words, padding with 0s if necessary.
    delimit = len(buffer) % 8
    if delimit:
        for i in xrange(8 - delimit):
            buffer.put_bit(False)

    # Add special alternating padding bitstrings until buffer is full.
    bytes_to_fill = (bit_limit - len(buffer)) // 8
    for i in xrange(bytes_to_fill):
      buffer.put(PAD0, 8)

    return create_bytes(buffer, rbs)
