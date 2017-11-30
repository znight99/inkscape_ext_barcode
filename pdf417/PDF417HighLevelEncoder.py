
import Compaction

TEXT_COMPACTION = 0
BYTE_COMPACTION = 1
NUMERIC_COMPACTION = 2
SUBMODE_ALPHA = 0
SUBMODE_LOWER = 1
SUBMODE_MIXED = 2
SUBMODE_PUNCTUATION = 3
LATCH_TO_TEXT = 900
LATCH_TO_BYTE_PADDED = 901
LATCH_TO_NUMERIC = 902
SHIFT_TO_BYTE = 913
LATCH_TO_BYTE = 924
ECI_USER_DEFINED = 925
ECI_GENERAL_PURPOSE = 926
ECI_CHARSET = 927

TEXT_MIXED_RAW = [
      48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 38, 13, 9, 44, 58,
      35, 45, 46, 36, 47, 43, 37, 42, 61, 94, 0, 32, 0, 0, 0]

TEXT_PUNCTUATION_RAW = [
      59, 60, 62, 64, 91, 92, 93, 95, 96, 126, 33, 13, 9, 44, 58,
      10, 45, 46, 36, 47, 34, 124, 42, 40, 41, 63, 123, 125, 39, 0]

MIXED = [-1] *128
PUNCTUATION =[-1]*128

#  private static final List<String> DEFAULT_ENCODING_NAMES = Arrays.asList("Cp437", "IBM437");


for i in range (0, len(TEXT_MIXED_RAW)):
  b = TEXT_MIXED_RAW[i]
  if (b > 0) :
    MIXED[b] = i
for i in range(0, len(TEXT_PUNCTUATION_RAW)):
  b = TEXT_PUNCTUATION_RAW[i]
  if (b > 0) :
    PUNCTUATION[b] = i

#  /**
#   * Performs high-level encoding of a PDF417 message using the algorithm described in annex P
#   * of ISO/IEC 15438:2001(E). If byte compaction has been selected, then only byte compaction
#   * is used.
#   *
#   * @param msg the message
#   * @param compaction compaction mode to use
#   * @param encoding character encoding used to encode in default or byte compaction
#   *  or {@code null} for default / not applicable
#   * @return the encoded message (the char values range from 0 to 928)
#   */
def encodeHighLevel(msg, compaction, encoding):
#  //the codewords 0..928 are encoded as Unicode characters
  sb = []

#    if (encoding != null && !DEFAULT_ENCODING_NAMES.contains(encoding.name())) {
#      CharacterSetECI eci = CharacterSetECI.getCharacterSetECIByName(encoding.name());
#      if (eci != null) {
#        encodingECI(eci.getValue(), sb);
#      }
#    }

  xlen = len(msg)
  p = 0
  textSubMode = SUBMODE_ALPHA

#    // User selected encoding mode
  bytes = [] #//Fill later and only if needed
  if (compaction == Compaction.TEXT):
    encodeText(msg, p, xlen, sb, textSubMode)
  elif (compaction == Compaction.BYTE):
    bytes = toBytes(msg, encoding)
    encodeBinary(bytes, p, len(bytes), BYTE_COMPACTION, sb)
  elif (compaction == Compaction.NUMERIC):
    sb+=[ LATCH_TO_NUMERIC ]
    encodeNumeric(msg, p, xlen, sb)
  else:
    encodingMode = TEXT_COMPACTION; #//Default mode, see 4.4.2.1
    while (p < xlen) :
      n = determineConsecutiveDigitCount(msg, p)
      if (n >= 13):
        sb+=[ LATCH_TO_NUMERIC ]
        encodingMode = NUMERIC_COMPACTION
        textSubMode = SUBMODE_ALPHA #//Reset after latch
        encodeNumeric(msg, p, n, sb)
        p += n
      else:
        t = determineConsecutiveTextCount(msg, p)
        if (t >= 5 or n == xlen) :
          if (encodingMode != TEXT_COMPACTION):
            sb+=[ LATCH_TO_TEXT ]
            encodingMode = TEXT_COMPACTION
            textSubMode = SUBMODE_ALPHA #//start with submode alpha after latch
          textSubMode = encodeText(msg, p, t, sb, textSubMode)
          p += t
        else :
          if (bytes == []):
            bytes = toBytes(msg, encoding)
          b = determineConsecutiveBinaryCount(msg, bytes, p)
          if (b == 0) :
            b = 1
          if (b == 1 and encodingMode == TEXT_COMPACTION):
#            //Switch for one byte (instead of latch)
            encodeBinary(bytes, p, 1, TEXT_COMPACTION, sb)
          else :
#            //Mode latch performed by encodeBinary()
            encodeBinary(bytes, p, b, encodingMode, sb)
            encodingMode = BYTE_COMPACTION
            textSubMode = SUBMODE_ALPHA #//Reset after latch
          p += b
  return sb


def toBytes(msg, encoding) :
#    // Defer instantiating default Charset until needed, since it may be for an unsupported
#    // encoding. For example the default of Cp437 doesn't seem to exist on Android.
#  if (encoding == null):
#      for (String encodingName : DEFAULT_ENCODING_NAMES) {
#        try {
#          encoding = Charset.forName(encodingName);
#        } catch (UnsupportedCharsetException uce) {
#          // continue
#        }
#      }
#      if (encoding == null) {
#        throw new WriterException("No support for any encoding: " + DEFAULT_ENCODING_NAMES);
#      }
#    }
  b=[]
  for c in msg:
    b+=[ ord(c) ]
  return b #.getBytes(encoding)

#
#  /**
#   * Encode parts of the message using Text Compaction as described in ISO/IEC 15438:2001(E),
#   * chapter 4.4.2.
#   *
#   * @param msg            the message
#   * @param startpos       the start position within the message
#   * @param count          the number of characters to encode
#   * @param sb             receives the encoded codewords
#   * @param initialSubmode should normally be SUBMODE_ALPHA
#   * @return the text submode in which this method ends
#   */
def encodeText(msg, startpos, count, sb, initialSubmode):
  tmp = []
  submode = initialSubmode
  idx = 0
  while 1:
    ch = msg[startpos + idx]
    if submode==SUBMODE_ALPHA:
      if isAlphaUpper(ch):
        if (ch == ' ') :
          tmp+=[26] # //space
        else:
          tmp+=[ord(ch) - 65]
      elif isAlphaLower(ch):
        submode = SUBMODE_LOWER
        tmp+=[27] # //ll
        continue
      elif (isMixed(ch)):
        submode = SUBMODE_MIXED
        tmp+=[28] #//ml
        continue
      else:
        tmp+=[29] # //ps
        tmp+=PUNCTUATION[ch];
    if submode==SUBMODE_LOWER:
      if (isAlphaLower(ch)) :
        if (ch == ' '):
          tmp+=[26] # //space
        else :
          tmp+=[ord(ch) - 97]
      else:
        if (isAlphaUpper(ch)) :
          tmp+=[ 27] #//as
          tmp+=  (ord(ch) - 65)
#              //space cannot happen here, it is also in "Lower"
        elif (isMixed(ch)):
          submode = SUBMODE_MIXED
          tmp+=[28] #//ml
          continue
        else :
          tmp+=[29] # //ps
          tmp+=PUNCTUATION[ord(ch)];
    if submode==SUBMODE_MIXED:
      if (isMixed(ch)) :
        tmp+=[ MIXED[ord(ch)] ]
      else :
        if (isAlphaUpper(ch)) :
          submode = SUBMODE_ALPHA
          tmp+=[28] # //al
          continue
        elif (isAlphaLower(ch)) :
          submode = SUBMODE_LOWER
          tmp+=[ 27] # //ll
          continue
        else :
          if (startpos + idx + 1 < count):
            next = msg[startpos + idx + 1]
            if (isPunctuation(next)) :
              submode = SUBMODE_PUNCTUATION
              tmp+[ 25] # //pl
              continue
          tmp+=[29] # //ps
          tmp+=[ PUNCTUATION[ord(ch)]] 
    else:  #SUBMODE_PUNCTUATION
      if (isPunctuation(ch)) :
        tmp+=[ PUNCTUATION[ord(ch)] ]
      else :
        submode = SUBMODE_ALPHA
        tmp+=[ 29 ] #//al
        continue
    idx+=1
    if (idx >= count) :
      break;
  h = 0;
  xlen = len(tmp)
  
  for i in range(0, xlen):
    odd = (i % 2) != 0
    if (odd) :
      h =  (h * 30) + tmp[i]
      sb += [ h ]
    else :
      h = tmp[i]
  if ((xlen % 2) != 0) :
    sb+=[ ((h * 30) + 29)] # //ps
  return submode

#
#  /**
#   * Encode parts of the message using Byte Compaction as described in ISO/IEC 15438:2001(E),
#   * chapter 4.4.3. The Unicode characters will be converted to binary using the cp437
#   * codepage.
#   *
#   * @param bytes     the message converted to a byte array
#   * @param startpos  the start position within the message
#   * @param count     the number of bytes to encode
#   * @param startmode the mode from which this method starts
#   * @param sb        receives the encoded codewords
#   */
def encodeBinary( bytes, startpos, count, startmode,sb):
  if (count == 1 and startmode == TEXT_COMPACTION) :
    sb+=[ SHIFT_TO_BYTE ]
  else:
    sixpack = ((count % 6) == 0)
    if (sixpack) :
      sb+=[LATCH_TO_BYTE]
    else:
     sb+=[LATCH_TO_BYTE_PADDED]
#
  idx = startpos;
#    // Encode sixpacks
  if (count >= 6) :
    chars = [0 ]*5
    while ((startpos + count - idx) >= 6) :
      t = 0
      for i in range( 0,6):
        t <<= 8;
        t += bytes[idx + i] & 0xff
      for i in range(0, 5):
        chars[i] = (t % 900);
        t /= 900;
      for i in range(len(chars) - 1,-1,-1):
        sb+=[chars[i]]
      idx += 6
#    //Encode rest (remaining n<5 bytes if any)
  
  for i in range(idx,startpos + count):
    ch = bytes[i] & 0xff
    sb+=[ch]
#
def encodeNumeric( msg,  startpos,  count, sb) :
  idx = 0
  tmp = []
  num900 = 900
  num0 = 0
  while (idx < count - 1) :
    tmp=[]
    xlen = min(44, count - idx);
    part = '1' + msg[startpos + idx:startpos + idx + xlen];
    bigint =int(part);
    while True:
      tmp+=[ bigint%num900];
      bigint = bigint/num900;
      if (bigint==0):
        break
#
#      //Reverse temporary string
    for i in range(len(tmp) - 1,-1,-1) :
      sb+=[tmp[i]]
    idx += xlen
#
#
def isDigit( ch):
  return ch >= '0' and ch <= '9'

#
def isAlphaUpper( ch):
  return ch == ' ' or (ch >= 'A' and ch <= 'Z')
#
def isAlphaLower( ch):
  return ch == ' ' or (ch >= 'a' and ch <= 'z')
#
def isMixed(ch):
  return MIXED[ord(ch)] != -1

#
def isPunctuation( ch) :
  return PUNCTUATION[ord(ch)] != -1
#
def isText(ch) :
  return ch == '\t' or ch == '\n' or ch == '\r' or (ch >= 32 and ch <= 126)

#
#  /**
#   * Determines the number of consecutive characters that are encodable using numeric compaction.
#   *
#   * @param msg      the message
#   * @param startpos the start position within the message
#   * @return the requested character count
#   */
def determineConsecutiveDigitCount( msg, startpos):
  count = 0
  xlen = len(msg)
  idx = startpos
  if (idx < xlen) :
    ch = msg[idx]
    while (isDigit(ch) and idx < xlen) :
      count+=1
      idx+=1
      if (idx < xlen) :
        ch = msg[idx]
  return count
#
#  /**
#   * Determines the number of consecutive characters that are encodable using text compaction.
#   *
#   * @param msg      the message
#   * @param startpos the start position within the message
#   * @return the requested character count
#   */
def determineConsecutiveTextCount( msg, startpos) :
  xlen = len(msg)
  idx = startpos
  while (idx < xlen) :
    ch = msg[idx]
    numericCount = 0
    while (numericCount < 13 and isDigit(ch) and idx < xlen) :
      numericCount+=1
      idx+=1
      if (idx < xlen) :
        ch = msg[idx]
    if (numericCount >= 13) :
      return idx - startpos - numericCount
    if (numericCount > 0) :
#      //Heuristic: All text-encodable chars or digits are binary encodable
       continue
    ch = msg[idx]
#      //Check if character is encodable
    if (not isText(ch)):
      break
    idx+=1
  return idx - startpos
#
#  /**
#   * Determines the number of consecutive characters that are encodable using binary compaction.
#   *
#   * @param msg      the message
#   * @param bytes    the message converted to a byte array
#   * @param startpos the start position within the message
#   * @return the requested character count
#   */
def determineConsecutiveBinaryCount( msg, bytes,  startpos):
#      throws WriterException {
  xlen = len(msg)
  idx = startpos
  while (idx < xlen) :
    ch = msg[idx]
    numericCount = 0
    while (numericCount < 13 and isDigit(ch)) :
      numericCount+=1
#        //textCount++;
      i = idx + numericCount
      if (i >= xlen) :
        break
      ch = [i];
    if (numericCount >= 13) :
      return idx - startpos
    textCount = 0;
    while (textCount < 5 and isText(ch)) :
      textCount+=1
      i = idx + textCount
      if (i >= xlen) :
        break
      ch = msg[i]
    if (textCount >= 5) :
      return idx - startpos
    ch = msg[idx]
#
#      //Check if character is encodable
#      //Sun returns a ASCII 63 (?) for a character that cannot be mapped. Let's hope all
#      //other VMs do the same
    if (bytes[idx] == 63 and ch != '?') :
      raise WriterException("Non-encodable character detected: " + ch + " (Unicode: " + ord(ch) + ')')
    idx+=1
  return idx - startpos;
#
#  private static void encodingECI(int eci, StringBuilder sb) throws WriterException {
#    if (eci >= 0 && eci < 900) {
#      sb.append((char) ECI_CHARSET);
#      sb.append((char) eci);
#    } else if (eci < 810900) {
#      sb.append((char) ECI_GENERAL_PURPOSE);
#      sb.append((char) (eci / 900 - 1));
#      sb.append((char) (eci % 900));
#    } else if (eci < 811800) {
#      sb.append((char) ECI_USER_DEFINED);
#      sb.append((char) (810900 - eci));
#    } else {
#      throw new WriterException("ECI number not in valid range from 0..811799, but was " + eci);
#    }
#  }
#
#}
