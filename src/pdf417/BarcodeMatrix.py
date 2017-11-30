
import BarcodeRow


#
#/**
# * Holds all of the information for a barcode in a format where it can be easily accessable
# *
# * @author Jacob Haynes
# */
class BarcodeMatrix :
#
#  private final BarcodeRow[] matrix;
#  private int currentRow;
#  private final int height;
#  private final int width;
#
#  /**
#   * @param height the height of the matrix (Rows)
#   * @param width  the width of the matrix (Cols)
#   */
  def __init__(self, height,  width) :
    self.matrix = [ None ]*height
#    //Initializes the array to the correct width
    for i in range(0, len(self.matrix)) :
      self.matrix[i] = BarcodeRow.BarcodeRow((width + 4) * 17 + 1)

    self.width = width * 17
    self.height = height
    self.currentRow = -1
#
  def set(self, x,  y, value) :
    self.matrix[y].set(x, value)
#
#  /*
#  void setMatrix(int x, int y, boolean black) {
#    set(x, y, (byte) (black ? 1 : 0));
#  }
#   */
#
  def startRow(self):
    self.currentRow+=1

#
  def getCurrentRow(self) :
    return self.matrix[self.currentRow]

#
  def getMatrix(self) :
    return self.getScaledMatrix(1, 1)
#
#  /*
#  public byte[][] getScaledMatrix(int scale) {
#    return getScaledMatrix(scale, scale);
#  }
#   */
#
  def getScaledMatrix(self, xScale,  yScale):
    matrixOut = [[]*(self.width * xScale)]*(self.height * yScale)
    yMax = self.height * yScale
    for i in range (0, yMax):
      matrixOut[yMax - i - 1] = self.matrix[i / yScale].getScaledRow(xScale)
    return matrixOut;

