#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
'''
Modified by znight@yeah.net
from zint

'''

import inkex, simplestyle

#import qrcode

import codecs
import sys

import gettext
_ = gettext.gettext
    

#RENDERING ROUTINES ==================================================
#   Take the array of 1's and 0's and render as a series of black
#   squares. A binary 1 is a filled square
#=====================================================================


#SVG element generation routine
def draw_SVG_hexagon(x,y,size, parent):
    sc=1;
    pp= [
        (x,y-size*1.1547005*sc),
        (x+size*sc,y-size*0.57735025*sc),
        (x+size*sc,y+size*0.57735025*sc),
        (x,y+size*1.1547005*sc),
        (x-size*sc,y+size*0.57735025*sc),
        (x-size*sc,y-size*0.57735025*sc),
    ]
    ss=""
    for xy in pp:
      ss+="%f,%f "%xy

    style = {   'stroke'        : 'none',
                'stroke-width'  : '0',
                'fill'          : '#000000'
            }
                
    attribs = {
        'style'     :simplestyle.formatStyle(style),
          'points': ss
            }
    circ = inkex.etree.SubElement(parent, inkex.addNS('polygon','svg'), attribs )
    
#turn a 2D array of 1's and 0's into a set of black squares
def render_maxicode( q, size, parent):
     '''
     for i in range(3):     
       style = {   'stroke'        : 'black',
                'stroke-width'  : str(size*0.87),
                'fill'          : 'none'
            }
                
       attribs = {
        'style'     :simplestyle.formatStyle(style),
          'cx': str(14.5*size),
            'cy': str(size*16.5*0.8660254),
              'r':str(size*0.82*(i*2+1)),
            }
       circ = inkex.etree.SubElement(parent, inkex.addNS('circle','svg'), attribs )
   
     '''
     bs=0.78
     for i in range(3):
       style = {   'stroke'        : 'none',
                'fill'          : 'black'
            }
                
       attribs = {
        'style'     :simplestyle.formatStyle(style),
          'd': 'M '+str(size*(14.5-bs*(i*2)-0.57735))+','+str(size*16.5*0.866)+' a '+str(size*(bs*(i*2)+0.57735))+','+str(size*(bs*(i*2)+0.57735))+',0,0,1,'+str(size*(bs*(i*2)*2+0.57735*2))+','+str(0)
            +' a '+str(size*(bs*(i*2)+0.57735))+','+str(size*(bs*(i*2)+0.57735))+',0,0,1,'+str(-size*(bs*(i*2)*2+0.57735*2))+','+str(0)+' z'
            +' m '+str(size*(-bs))+','+str(0)+' a '+str(size*(bs*(i*2+1)+0.57735))+','+str(size*(bs*(i*2+1)+0.57735))+',0,1,0,'+str(size*(bs*(i*2+1)*2+0.57735*2))+','+str(0)
            +' a '+str(size*(bs*(i*2+1)+0.57735))+','+str(size*(bs*(i*2+1)+0.57735))+',0,1,0,'+str(-size*(bs*(i*2+1)*2+0.57735*2))+','+str(0)+' z',
            }
       circ = inkex.etree.SubElement(parent, inkex.addNS('path','svg'), attribs )
     
     for y in range(len(q)):     #loop over all the modules in the datamatrix
       for x in range(len(q[y])-(y%2)):
          if y>=11 and y<16 and x>11-(y-11)*0.5-(y%2) and x<18+(y-12)*0.5-(y%2)-(1 if y==11 else 0):
            continue
          if y>=16 and y<22 and x>11-(21-y)*0.5-(y%2) and x<18+(20-y)*0.5-(y%2):
            continue
          if q[y][x] == 1: #A binary 1 is a filled square
              draw_SVG_hexagon(size*0.5+x*size+(size*0.5)*(y%2),size*0.4330127+y*size*0.8660254,size*0.40, parent)



MaxiGrid = [ #/* ISO/IEC 16023 Figure 5 - MaxiCode Module Sequence */ /* 30 x 33 data grid */
	122, 121, 128, 127, 134, 133, 140, 139, 146, 145, 152, 151, 158, 157, 164, 163, 170, 169, 176, 175, 182, 181, 188, 187, 194, 193, 200, 199, 0, 0,
	124, 123, 130, 129, 136, 135, 142, 141, 148, 147, 154, 153, 160, 159, 166, 165, 172, 171, 178, 177, 184, 183, 190, 189, 196, 195, 202, 201, 817, 0,
	126, 125, 132, 131, 138, 137, 144, 143, 150, 149, 156, 155, 162, 161, 168, 167, 174, 173, 180, 179, 186, 185, 192, 191, 198, 197, 204, 203, 819, 818,
	284, 283, 278, 277, 272, 271, 266, 265, 260, 259, 254, 253, 248, 247, 242, 241, 236, 235, 230, 229, 224, 223, 218, 217, 212, 211, 206, 205, 820, 0,
	286, 285, 280, 279, 274, 273, 268, 267, 262, 261, 256, 255, 250, 249, 244, 243, 238, 237, 232, 231, 226, 225, 220, 219, 214, 213, 208, 207, 822, 821,
	288, 287, 282, 281, 276, 275, 270, 269, 264, 263, 258, 257, 252, 251, 246, 245, 240, 239, 234, 233, 228, 227, 222, 221, 216, 215, 210, 209, 823, 0,
	290, 289, 296, 295, 302, 301, 308, 307, 314, 313, 320, 319, 326, 325, 332, 331, 338, 337, 344, 343, 350, 349, 356, 355, 362, 361, 368, 367, 825, 824,
	292, 291, 298, 297, 304, 303, 310, 309, 316, 315, 322, 321, 328, 327, 334, 333, 340, 339, 346, 345, 352, 351, 358, 357, 364, 363, 370, 369, 826, 0,
	294, 293, 300, 299, 306, 305, 312, 311, 318, 317, 324, 323, 330, 329, 336, 335, 342, 341, 348, 347, 354, 353, 360, 359, 366, 365, 372, 371, 828, 827,
	410, 409, 404, 403, 398, 397, 392, 391, 80, 79, 0, 0, 14, 13, 38, 37, 3, 0, 45, 44, 110, 109, 386, 385, 380, 379, 374, 373, 829, 0,
	412, 411, 406, 405, 400, 399, 394, 393, 82, 81, 41, 0, 16, 15, 40, 39, 4, 0, 0, 46, 112, 111, 388, 387, 382, 381, 376, 375, 831, 830,
	414, 413, 408, 407, 402, 401, 396, 395, 84, 83, 42, 0, 0, 0, 0, 0, 6, 5, 48, 47, 114, 113, 390, 389, 384, 383, 378, 377, 832, 0,
	416, 415, 422, 421, 428, 427, 104, 103, 56, 55, 17, 0, 0, 0, 0, 0, 0, 0, 21, 20, 86, 85, 434, 433, 440, 439, 446, 445, 834, 833,
	418, 417, 424, 423, 430, 429, 106, 105, 58, 57, 0, 0, 0, 0, 0, 0, 0, 0, 23, 22, 88, 87, 436, 435, 442, 441, 448, 447, 835, 0,
	420, 419, 426, 425, 432, 431, 108, 107, 60, 59, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 90, 89, 438, 437, 444, 443, 450, 449, 837, 836,
	482, 481, 476, 475, 470, 469, 49, 0, 31, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 54, 53, 464, 463, 458, 457, 452, 451, 838, 0,
	484, 483, 478, 477, 472, 471, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 466, 465, 460, 459, 454, 453, 840, 839,
	486, 485, 480, 479, 474, 473, 52, 51, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 43, 468, 467, 462, 461, 456, 455, 841, 0,
	488, 487, 494, 493, 500, 499, 98, 97, 62, 61, 0, 0, 0, 0, 0, 0, 0, 0, 0, 27, 92, 91, 506, 505, 512, 511, 518, 517, 843, 842,
	490, 489, 496, 495, 502, 501, 100, 99, 64, 63, 0, 0, 0, 0, 0, 0, 0, 0, 29, 28, 94, 93, 508, 507, 514, 513, 520, 519, 844, 0,
	492, 491, 498, 497, 504, 503, 102, 101, 66, 65, 18, 0, 0, 0, 0, 0, 0, 0, 19, 30, 96, 95, 510, 509, 516, 515, 522, 521, 846, 845,
	560, 559, 554, 553, 548, 547, 542, 541, 74, 73, 33, 0, 0, 0, 0, 0, 0, 11, 68, 67, 116, 115, 536, 535, 530, 529, 524, 523, 847, 0,
	562, 561, 556, 555, 550, 549, 544, 543, 76, 75, 0, 0, 8, 7, 36, 35, 12, 0, 70, 69, 118, 117, 538, 537, 532, 531, 526, 525, 849, 848,
	564, 563, 558, 557, 552, 551, 546, 545, 78, 77, 0, 34, 10, 9, 26, 25, 0, 0, 72, 71, 120, 119, 540, 539, 534, 533, 528, 527, 850, 0,
	566, 565, 572, 571, 578, 577, 584, 583, 590, 589, 596, 595, 602, 601, 608, 607, 614, 613, 620, 619, 626, 625, 632, 631, 638, 637, 644, 643, 852, 851,
	568, 567, 574, 573, 580, 579, 586, 585, 592, 591, 598, 597, 604, 603, 610, 609, 616, 615, 622, 621, 628, 627, 634, 633, 640, 639, 646, 645, 853, 0,
	570, 569, 576, 575, 582, 581, 588, 587, 594, 593, 600, 599, 606, 605, 612, 611, 618, 617, 624, 623, 630, 629, 636, 635, 642, 641, 648, 647, 855, 854,
	728, 727, 722, 721, 716, 715, 710, 709, 704, 703, 698, 697, 692, 691, 686, 685, 680, 679, 674, 673, 668, 667, 662, 661, 656, 655, 650, 649, 856, 0,
	730, 729, 724, 723, 718, 717, 712, 711, 706, 705, 700, 699, 694, 693, 688, 687, 682, 681, 676, 675, 670, 669, 664, 663, 658, 657, 652, 651, 858, 857,
	732, 731, 726, 725, 720, 719, 714, 713, 708, 707, 702, 701, 696, 695, 690, 689, 684, 683, 678, 677, 672, 671, 666, 665, 660, 659, 654, 653, 859, 0,
	734, 733, 740, 739, 746, 745, 752, 751, 758, 757, 764, 763, 770, 769, 776, 775, 782, 781, 788, 787, 794, 793, 800, 799, 806, 805, 812, 811, 861, 860,
	736, 735, 742, 741, 748, 747, 754, 753, 760, 759, 766, 765, 772, 771, 778, 777, 784, 783, 790, 789, 796, 795, 802, 801, 808, 807, 814, 813, 862, 0,
	738, 737, 744, 743, 750, 749, 756, 755, 762, 761, 768, 767, 774, 773, 780, 779, 786, 785, 792, 791, 798, 797, 804, 803, 810, 809, 816, 815, 864, 863
]

maxiCodeSet = [ #/* from Appendix A - ASCII character to Code Set (e.g. 2 = Set B) */
	#/* set 0 refers to special characters that fit into more than one set (e.g. GS) */
	5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0, 5, 5, 5, 5, 5, 5,
	5, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 5, 0, 2, 1, 1, 1, 1, 1, 1,
	1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 2,
	2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
	1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2,
	2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
	2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4,
	4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
	5, 4, 5, 5, 5, 5, 5, 5, 4, 5, 3, 4, 3, 5, 5, 4, 4, 3, 3, 3,
	4, 3, 5, 4, 4, 3, 3, 4, 3, 3, 3, 4, 3, 3, 3, 3, 3, 3, 3, 3,
	3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
	3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
	4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4
]

maxiSymbolChar = [ #/* from Appendix A - ASCII character to symbol value */
	0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
	20, 21, 22, 23, 24, 25, 26, 30, 28, 29, 30, 35, 32, 53, 34, 35, 36, 37, 38, 39,
	40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 37,
	38, 39, 40, 41, 52, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
	16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 42, 43, 44, 45, 46, 0, 1, 2, 3,
	4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
	24, 25, 26, 32, 54, 34, 35, 36, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 47, 48,
	49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 36,
	37, 37, 38, 39, 40, 41, 42, 43, 38, 44, 37, 39, 38, 45, 46, 40, 41, 39, 40, 41,
	42, 42, 47, 43, 44, 43, 44, 45, 45, 46, 47, 46, 0, 1, 2, 3, 4, 5, 6, 7,
	8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 32,
	33, 34, 35, 36, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
	16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 32, 33, 34, 35, 36
]


maxi_codeword=[0]*144;
logt=None
alog=None
rspoly=None
gspoly=0
logmod=0
rlen=0
'''
// rs_init_gf(poly) initialises the parameters for the Galois Field.
// The symbol size is determined from the highest bit set in poly
// This implementation will support sizes up to 30 bits (though that
// will result in very large log/antilog tables) - bit sizes of
// 8 or 4 are typical
//
// The poly is the bit pattern representing the GF characteristic
// polynomial.  e.g. for ECC200 (8-bit symbols) the polynomial is
// a**8 + a**5 + a**3 + a**2 + 1, which translates to 0x12d.
'''
def rs_init_gf( poly):

  #// Find the top bit, and hence the symbol size
  global alog,logt,gspoly,rspoly,logmod,rlen
  b=1
  m=0
  while ( b <= poly):
    m+=1;
    b <<= 1
  b >>= 1;
  m-=1
  gfpoly = poly;
  symsize = m;

  #// Calculate the log/alog tables
  logmod = (1 << m) - 1;
  logt = [0]* (logmod + 1);
  alog = [0]* logmod;

  p=1
  v=0
  while ( v < logmod) :
    alog[v] = p;
    logt[p] = v;
    p <<= 1;
    if (p & b):
      p ^= poly;
    v+=1

'''
// rs_init_code(nsym, index) initialises the Reed-Solomon encoder
// nsym is the number of symbols to be generated (to be appended
// to the input data).  index is usually 1 - it is the index of
// the constant in the first term (i) of the RS generator polynomial:
// (x + 2**i)*(x + 2**(i+1))*...   [nsym terms]
// For ECC200, index is 1.
'''
def rs_init_code( nsym,  index):

  global alog,logt,gspoly,rspoly,logmod,rlen
  rspoly = [0]*(nsym + 1);

  rlen = nsym;

  rspoly[0] = 1;
  for i in range( 1, nsym+1) :
    rspoly[i] = 1;
    for k in range( i - 1, 0,-1) :
      if (rspoly[k]):
        rspoly[k] = alog[(logt[rspoly[k]] + index) % logmod];
      rspoly[k] ^= rspoly[k - 1];
    rspoly[0] = alog[(logt[rspoly[0]] + index) % logmod];
    index+=1;
 
def rs_encode(len, data, res):
  global alog,logt,gspoly,rspoly,logmod,rlen
 
  for i in range(rlen):
    res[i] = 0;
  for i in range(len) :
    m = res[rlen - 1] ^ data[i];
    for k in range( rlen - 1,0,-1) :
      if (m and rspoly[k]):
        res[k] = res[k - 1] ^ alog[(logt[m] + logt[rspoly[k]]) % logmod];
      else:
        res[k] = res[k - 1];
    if (m and rspoly[0]):
      res[0] = alog[(logt[m] + logt[rspoly[0]]) % logmod];
    else:
      res[0] = 0;

def rs_encode_long( len, data, res):
  #/* The same as above but for larger bitlengths - Aztec code compatible */
  global alog,logt,gspoly,rspoly,logmod,rlen
  for i in range( rlen):
    res[i] = 0;
  for i in range(len) :
    m = res[rlen - 1] ^ data[i];
    for k in range( rlen - 1,0,-1) :
      if (m and rspoly[k]):
        res[k] = res[k - 1] ^ alog[(logt[m] + logt[rspoly[k]]) % logmod];
      else:
        res[k] = res[k - 1];
    if (m and rspoly[0]):
      res[0] = alog[(logt[m] + logt[rspoly[0]]) % logmod];
    else:
      res[0] = 0;

def maxi_do_primary_check(  ):
  #/* Handles error correction of primary message */
  global maxi_codeword
  data=[0]*15;
  results=[0]*15;
  datalen = 10;
  ecclen = 10;

  rs_init_gf(0x43);
  rs_init_code(ecclen, 1);

  for j in range(  datalen):
    data[j] = maxi_codeword[j];

  rs_encode(datalen, data, results);

  for j in range(ecclen):
    maxi_codeword[ datalen + j] = results[ecclen - 1 - j];


def maxi_do_secondary_chk_odd( ecclen ):
  #/* Handles error correction of odd characters in secondary */
  global maxi_codeword
  data=[0]*100;
  results=[0]*30;
  datalen = 68;

  rs_init_gf(0x43);
  rs_init_code(ecclen, 1);

  if (ecclen == 20):
    datalen = 84;

  for j in range( datalen):
    if (j & 1) : #// odd
      data[(j-1)/2] = maxi_codeword[j + 20];

  rs_encode(datalen/2, data, results);

  for  j in range(ecclen):
    maxi_codeword[ datalen + (2 *j) + 1 + 20 ] = results[ecclen - 1 - j];

def maxi_do_secondary_chk_even( ecclen ):
  #/* Handles error correction of even characters in secondary */
  global maxi_codeword
  data=[0]*100;
  results=[0]*30;
  datalen = 68;

  if (ecclen == 20):
    datalen = 84;

  rs_init_gf(0x43);
  rs_init_code(ecclen, 1);

  for  j in range( datalen + 1):
    if (not (j & 1)):# // even
      data[j/2] = maxi_codeword[j + 20];

  rs_encode(datalen/2, data, results);

  for j in range(ecclen):
    maxi_codeword[ datalen + (2 *j) + 20] = results[ecclen - 1 - j];

def maxi_bump(set, character,  bump_posn):
  #/* Moves everything up so that a shift or latch can be inserted */

  for i in range( 143, bump_posn,-1) :
    set[i] = set[i - 1];
    character[i] = character[i - 1];

def maxi_text_process( mode,  source,  length):
  #/* Format text according to Appendix A */

  ''' This code doesn't make use of [Lock in C], [Lock in D]
  and [Lock in E] and so is not always the most efficient at
  compressing data, but should suffice for most applications */
  '''
  global maxi_codeword

  set=[0]*144
  character=[0]*144

  if(length > 138) :
    return 0;

  for i in range( 144) :
    set[i] = -1;
    character[i] = 0;

  for i in range( length) :
    #/* Look up characters in table from Appendix A - this gives
    # value and code set for most characters */
    set[i] = maxiCodeSet[source[i]];
    character[i] = maxiSymbolChar[source[i]];

  #/* If a character can be represented in more than one code set,
  #pick which version to use */
  if(set[0] == 0) :
    if(character[0] == 13) :
      character[0] = 0;
    set[0] = 1;

  for i in range( 1, length) :
    if(set[i] == 0) :
      done = 0;
      #/* Special character */
      if(character[i] == 13) :
        #/* Carriage Return */
        if(set[i - 1] == 5) :
          character[i] = 13;
          set[i] = 5;
        else :
          if((i != length - 1) and (set[i + 1] == 5)) :
            character[i] = 13;
            set[i] = 5;
          else :
            character[i] = 0;
            set[i] = 1;
        done = 1;

      if((character[i] == 28) and (done == 0)) :
        #/* FS */
        if(set[i - 1] == 5) :
          character[i] = 32;
          set[i] = 5;
        else :
          set[i] = set[i - 1];
        done = 1;

      if((character[i] == 29) and (done == 0)) :
        #/* GS */
        if(set[i - 1] == 5) :
          character[i] = 33;
          set[i] = 5;
        else :
          set[i] = set[i - 1];
        done = 1;

      if((character[i] == 30) and (done == 0)) :
        #/* RS */
        if(set[i - 1] == 5) :
          character[i] = 34;
          set[i] = 5;
        else :
          set[i] = set[i - 1];
        done = 1;

      if((character[i] == 32) and (done == 0)) :
        #/* Space */
        if(set[i - 1] == 1) :
          character[i] = 32;
          set[i] = 1;
        if(set[i - 1] == 2) :
          character[i] = 47;
          set[i] = 2;
        if(set[i - 1] >= 3) :
          if(i != length - 1) :
            if(set[i + 1] == 1) :
              character[i] = 32;
              set[i] = 1;
            if(set[i + 1] == 2) :
              character[i] = 47;
              set[i] = 2;
            if(set[i + 1] >= 3) :
              character[i] = 59;
              set[i] = set[i - 1];
          else :
            character[i] = 59;
            set[i] = set[i - 1];
        done = 1;

      if((character[i] == 44) and (done == 0)) :
        #/* Comma */
        if(set[i - 1] == 2) :
          character[i] = 48;
          set[i] = 2;
        else :
          if((i != length - 1) and (set[i + 1] == 2)) :
            character[i] = 48;
            set[i] = 2;
          else :
            set[i] = 1;
        done = 1;

      if((character[i] == 46) and (done == 0)) :
        #/* Full Stop */
        if(set[i - 1] == 2) :
          character[i] = 49;
          set[i] = 2;
        else:
          if((i != length - 1) and (set[i + 1] == 2)) :
            character[i] = 49;
            set[i] = 2;
          else :
            set[i] = 1;
        done = 1;

      if((character[i] == 47) and (done == 0)) :
        #/* Slash */
        if(set[i - 1] == 2) :
          character[i] = 50;
          set[i] = 2;
        else :
          if((i != length - 1) and (set[i + 1] == 2)) :
            character[i] = 50;
            set[i] = 2;
          else :
            set[i] = 1;
        done = 1;

      if((character[i] == 58) and (done == 0)) :
        #/* Colon */
        if(set[i - 1] == 2) :
          character[i] = 51;
          set[i] = 2;
        else :
          if((i != length - 1) and (set[i + 1] == 2)) :
            character[i] = 51;
            set[i] = 2;
          else :
            set[i] = 1;
        done = 1;
        
  for i in range( length, 144) :
    #/* Add the padding */
    if(set[length - 1] == 2) :
      set[i] = 2;
    else :
      set[i] = 1;
    character[i] = 33;

  #/* Find candidates for number compression */
  if((mode == 2) and (mode ==3)) :
    j = 0; 
  else:
    j = 9; 
  #/* Number compression not allowed in primary message */
  count = 0;
  for i in range( j, 143) :
    if((set[i] == 1) and ((character[i] >= 48) and (character[i] <= 57))) :
      #/* Character is a number */
      count+=1;
    else :
      count = 0;
    if(count == 9) :
      #/* Nine digits in a row can be compressed */
      set[i] = 6;
      set[i - 1] = 6;
      set[i - 2] = 6;
      set[i - 3] = 6;
      set[i - 4] = 6;
      set[i - 5] = 6;
      set[i - 6] = 6;
      set[i - 7] = 6;
      set[i - 8] = 6;
      count = 0;
      
  #/* Add shift and latch characters */
  current_set = 1;
  i = 0;
  while (i<144) :
    if(set[i] != current_set) :
      if (set[i]==1):
          if(set[i + 1] == 1) :
            if(set[i + 2] == 1) :
              if(set[i + 3] == 1) :
                #/* Latch A */
                maxi_bump(set, character, i);
                character[i] = 63;
                current_set = 1;
                length+=1;
              else :
                #/* 3 Shift A */
                maxi_bump(set, character, i);
                character[i] = 57;
                length+=1;
                i += 2;
            else :
              #/* 2 Shift A */
              maxi_bump(set, character, i);
              character[i] = 56;
              length+=1;
              i+=1;
          else:
            #/* Shift A */
            maxi_bump(set, character, i);
            character[i] = 59;
            length+=1;
      elif (set[i]==2):
          if(set[i + 1] == 2) :
            #/* Latch B */
            maxi_bump(set, character, i);
            character[i] = 63;
            current_set = 2;
            length+=1;
          else :
            #/* Shift B */
            maxi_bump(set, character, i);
            character[i] = 59;
            length+=1;
      elif (set[i]==3):
          #/* Shift C */
          maxi_bump(set, character, i);
          character[i] = 60;
          length+=1;
      elif (set[i]==4):
          #/* Shift D */
          maxi_bump(set, character, i);
          character[i] = 61;
          length+=1;
      elif (set[i]==5):
          #/* Shift E */
          maxi_bump(set, character, i);
          character[i] = 62;
          length+=1;
      elif (set[i]==6):
          pass
          #/* Number Compressed */
          #/* Do nothing */
      i+=1;
    i+=1;

  #/* Number compression has not been forgotten! - It's handled below */
  i = 0;
  while i<=143 :
    if (set[i] == 6) :
      #/* Number compression */
      substring='';

      for j in range( 10) :
        substring += chr(character[i + j]);
      value = int(substring);

      character[i] = 31; #/* NS */
      character[i + 1] = (value & 0x3f000000) >> 24;
      character[i + 2] = (value & 0xfc0000) >> 18;
      character[i + 3] = (value & 0x3f000) >> 12;
      character[i + 4] = (value & 0xfc0) >> 6;
      character[i + 5] = (value & 0x3f);

      i += 6;
      for j in range( i, 140) :
        set[j] = set[j + 3];
        character[j] = character[j + 3];
      length -= 3;
    else :
      i+=1;

  if(((mode ==2) or (mode == 3)) and (length > 84)) :
    return 0

  if(((mode == 4) or (mode == 6)) and (length > 93)) :
    return 0;

  if((mode == 5) and (length > 77)) :
    return 0;


  #/* Copy the encoded text into the codeword array */
  if((mode == 2) or (mode == 3)) :
    for i in range(84) : #/* secondary only */
      maxi_codeword[i + 20] = character[i];

  if((mode == 4) or (mode == 6)) :
    for i in range( 9) : #/* primary */
      maxi_codeword[i + 1] = character[i];
    for i in range(84) : #/* secondary */
      maxi_codeword[i + 20] = character[i + 9];
  if(mode == 5) :
    for i in range( 9) : #/* primary */
      maxi_codeword[i + 1] = character[i];
    for i in range( 68) : #/* secondary */
      maxi_codeword[i + 20] = character[i + 9];

  return 1;


def maxicode( source,  mode=4):
  global maxi_codeword
  length=len(source)
  local_source=[0]*(length + 1);

  #/* The following to be replaced by ECI handling */
  for i in range(0,len(source)):
    local_source[i]=ord(source[i])
  local_source[len(source)]=0
  
  maxi_codeword=[0]*144

  if(mode < 4 or mode > 5) : #/* If mode is unspecified */
    return None
    

  maxi_codeword[0] = mode;

  #print maxi_codeword;
  i = maxi_text_process(mode, local_source, length);
  if(i ==0 ) :
    return None;
    

  #/* All the data is sorted - now do error correction */
  maxi_do_primary_check(); # /* always EEC */

  #print maxi_codeword
  if ( mode == 5 ):
    eclen = 56;   #// 68 data codewords , 56 error corrections
  else:
    eclen = 40; # // 84 data codewords,  40 error corrections

  maxi_do_secondary_chk_even(eclen/2);  #// do error correction of even
  maxi_do_secondary_chk_odd(eclen/2);   #// do error correction of odd

  #print maxi_codeword
  #/* Copy data into symbol grid */
  symbol=[[0 for i in range(30)] for i in range(33)]
  
  bit_pattern=[0]*7
  for i in range( 33) :
    for j in range(30) :
      block = (MaxiGrid[(i * 30) + j] + 5) / 6;
      bit = (MaxiGrid[(i * 30) + j] + 5) % 6;

      if(block != 0) :

        bit_pattern[0] =  (maxi_codeword[block - 1] & 0x20) >> 5;
        bit_pattern[1] =  (maxi_codeword[block - 1] & 0x10) >> 4;
        bit_pattern[2] =  (maxi_codeword[block - 1] & 0x8) >> 3;
        bit_pattern[3] =  (maxi_codeword[block - 1] & 0x4) >> 2;
        bit_pattern[4] =  (maxi_codeword[block - 1] & 0x2) >> 1;
        bit_pattern[5] =  (maxi_codeword[block - 1] & 0x1);

        if(bit_pattern[bit] != 0) :
          symbol[i][j]=1;

  #/* Add orientation markings */
  symbol[0][28]=1; #// Top right filler
  symbol[0][29]=1;
  symbol[9][10]=1; #// Top left marker
  symbol[9][11]=1;
  symbol[10][11]=1;
  symbol[15][7]=1; #// Left hand marker
  symbol[16][8]=1;
  symbol[16][20]=1; #// Right hand marker
  symbol[17][20]=1;
  symbol[22][10]=1; #// Bottom left marker
  symbol[23][10]=1;
  symbol[22][17]=1; #// Bottom right marker
  symbol[23][17]=1;
  return symbol


class MaxiCode(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        
        #PARSE OPTIONS
        self.OptionParser.add_option("--text",
            action="store", type="string",
            dest="TEXT", default='Inkscape')

        self.OptionParser.add_option("--MODE",
            action="store", type="string",
            dest="MODE", default='4')
 
        self.OptionParser.add_option("--size",
            action="store", type="int",
            dest="SIZE", default=1)
            
    def effect(self):
        
        so = self.options
        
        if so.TEXT == '':  #abort if converting blank text
            inkex.errormsg(_('Please enter an input string'))
        else:
            size=so.SIZE*self.unittouu('0.02in')/1.1547*2
            #INKSCAPE GROUP TO CONTAIN EVERYTHING
                       
            #q=[[1 for i in range(30)] for i in range(33)]
            q=maxicode(unicode(so.TEXT,'mbcs').encode('utf-8') if sys.getfilesystemencoding()=='mbcs' else so.TEXT,int(so.MODE))
            
            if (q!=None):
              (x,y) = self.view_center   #Put in in the centre of the current view
              
              y-=len(q)/2.0*size*0.8660254
              x-=len(q[0])/2.0*size
              centre=(x,y)
              grp_transform = 'translate' + str( centre )
              grp_name = 'MaxiCode'
              grp_attribs = {inkex.addNS('label','inkscape'):grp_name,
                             'transform':grp_transform }
              grp = inkex.etree.SubElement(self.current_layer, 'g', grp_attribs)#the group to put everything in
              render_maxicode( q,size, grp )    # generate the SVG elements
            
if __name__ == '__main__':
    e = MaxiCode()
    e.affect()

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
