
from Base import Barcode

START_END_CHARS = ['A', 'B', 'C', 'D'];
ALT_START_END_CHARS = ['T', 'N', '*', 'E'];
CHARS_WHICH_ARE_TEN_LENGTH_EACH_AFTER_DECODED = [ '/', ':', '+', '.' ];
encoding = {
   '0':'0000011',
   '1':'0000110',
   '2':'0001001',
   '3':'1100000',
   '4':'0010010',
   '5':'1000010',
   '6':'0100001',
   '7':'0100100',
   '8':'0110000',
   '9':'1001000',
   '-':'0001100',
   '$':'0011000',
   ':':'1000101',
   '/':'1010001',
   '.':'1010100',
   '+':'0010101',
   'A':'0011010',
   'B':'0101001',
   'C':'0001011',
   'D':'0001110',
    }

class Coda(Barcode):
  # Convert a text into string binary of black and white markers
  def encode(self, text):
    text       = text.upper()
    self.label = text
    text       = 'A' + text + 'B'
    result     = ''
    # It isposible for us to encode code39
    # into full ascii, but this feature is
    # not enabled here
    for char in text:
      char=char.upper()
      if char=='T':
        char='A'
      if char=='N':
        char='B'
      if char=='*':
        char='C'
      if char=='E':
        char='D'
      if not encoding.has_key(char):
        char = '-';

      result = result + encoding[char]+'0';

    # Now we need to encode the code39, best read
    # the code to understand what it's up to:
    encoded = '';
    colour   = '1'; # 1 = Black, 0 = White
    for data in result:
      if data == '2':
        encoded = encoded + colour + colour+colour
      elif data == '1':
        encoded = encoded + colour + colour
      else:
        encoded = encoded + colour
      if colour == '1':
        colour = '0'
      else:
        colour = '1'

    self.inclabel = text
    return '0'*10+encoded+'0'*10;

