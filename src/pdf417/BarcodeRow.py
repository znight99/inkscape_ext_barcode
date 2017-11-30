
#/**
# * @author Jacob Haynes
# */
class BarcodeRow :
#
#  private final byte[] row;
#  //A tacker for position in the bar
#  private int currentLocation;
#
#  /**
#   * Creates a Barcode row of the width
#   */
  def __init__(self,width) :
    self.row = [0]*width
    self.currentLocation = 0

#
#  /**
#   * Sets a specific location in the bar
#   *
#   * @param x The location in the bar
#   * @param value Black if true, white if false;
#   */
  def set(self, x, value) :
    self.row[x] = value
#
#  /**
#   * Sets a specific location in the bar
#   *
#   * @param x The location in the bar
#   * @param black Black if true, white if false;
#   */
  def set(self, x,  black) :
    self.row[x] =  (1 if black else 0)

#
#  /**
#   * @param black A boolean which is true if the bar black false if it is white
#   * @param width How many spots wide the bar is.
#   */
  def addBar(self, black,  width) :
    for ii in range( 0, width) :
      self.set(self.currentLocation, black)
      self.currentLocation+=1
#
#  /*
  def getRow(self) :
    return row

#   */
#
#  /**
#   * This function scales the row
#   *
#   * @param scale How much you want the image to be scaled, must be greater than or equal to 1.
#   * @return the scaled row
#   */
  def getScaledRow(self,scale) :
    output = [0]*(len(self.row) * scale)
    for i in range(0,len(output)):
      output[i] = self.row[i / scale]
    return output
