from qrcode import constants, util
#from qrcode.image.base import BaseImage

#import six
from bisect import bisect_left


def make(data=None, **kwargs):
    qr = QRCode(**kwargs)
    qr.add_data(data)
    return #qr.make_image()

def _check_version(version):
    if version < 1 or version > 40:
        raise ValueError(
            "Invalid version (was %s, expected 1 to 40)" % version)

class QRCode:

    def __init__(self, version=None,
                 error_correction=constants.ERROR_CORRECT_M,
                 box_size=10, border=4,
                 image_factory=None):
        self.version = version and int(version)
        self.error_correction = int(error_correction)
        self.box_size = int(box_size)
        # Spec says border should be at least four boxes wide, but allow for
        # any (e.g. for producing printable QR codes).
        self.border = int(border)
        self.image_factory = image_factory
        if image_factory is not None:
            assert issubclass(image_factory, BaseImage)
        self.clear()

    def clear(self):
        """
        Reset the internal data.
        """
        self.modules = None
        self.modules_count = 0
        self.data_cache = None
        self.data_list = []

    def add_data(self, data, optimize=20):
        """
        Add data to this QR Code.

        :param optimize: Data will be split into multiple chunks to optimize
            the QR size by finding to more compressed modes of at least this
            length. Set to ``0`` to avoid optimizing at all.
        """
        if isinstance(data, util.QRData):
            self.data_list.append(data)
        else:
            #if optimize:
            #    self.data_list.extend(util.optimal_data_chunks(data,optimize))
            #else:
                self.data_list.append(util.QRData(data))
        self.data_cache = None

    def make(self, fit=True):
        """
        Compile the data into a QR Code array.

        :param fit: If ``True`` (or if a size has not been provided), find the
            best fit for the data to avoid data overflow errors.
        """
        self.buffer=util.BitBuffer()
        util.generate_data(self.buffer,self.data_list,self.version)
        
        if fit or (self.version is None):
            self.best_fit(start=self.version)
        self.makeImpl(False, self.best_mask_pattern())

    def makeImpl(self, test, mask_pattern):
        _check_version(self.version)
        self.modules_count = self.version * 4 + 17
        self.modules = [None] * self.modules_count

        for row in range(self.modules_count):

            self.modules[row] = [None] * self.modules_count

            for col in range(self.modules_count):
                self.modules[row][col] = None   # (col + row) % 3

        self.setup_position_probe_pattern(0, 0)
        self.setup_position_probe_pattern(self.modules_count - 7, 0)
        self.setup_position_probe_pattern(0, self.modules_count - 7)
        self.setup_position_adjust_pattern()
        self.setup_timing_pattern()
        self.setup_type_info(test, mask_pattern)

        if self.version >= 7:
            self.setup_type_number(test)

        if self.data_cache is None:
            self.data_cache = util.create_data(
                self.version, self.error_correction, self.buffer)
        self.map_data(self.data_cache, mask_pattern)

    def setup_position_probe_pattern(self, row, col):
        for r in range(-1, 8):

            if row + r <= -1 or self.modules_count <= row + r:
                continue

            for c in range(-1, 8):

                if col + c <= -1 or self.modules_count <= col + c:
                    continue

                if (0 <= r and r <= 6 and (c == 0 or c == 6)
                        or (0 <= c and c <= 6 and (r == 0 or r == 6))
                        or (2 <= r and r <= 4 and 2 <= c and c <= 4)):
                    self.modules[row + r][col + c] = True
                else:
                    self.modules[row + r][col + c] = False

    def best_fit(self, start=None):
        """
        Find the minimum size required to fit in the data.
        """
        if start is None:
            start = 1
        _check_version(start)

        # Corresponds to the code in util.create_data, except we don't yet know
        # version, so optimistically assume start and check later
        mode_sizes = util.mode_sizes_for_version(start)

        needed_bits = len(self.buffer)
        self.version = bisect_left(util.BIT_LIMIT_TABLE[self.error_correction],
                                   needed_bits, start)
        if self.version >= 41:
            raise OverflowError('Too many characters')

        # Now check whether we need more bits for the mode sizes, recursing if
        # our guess was too low
        if mode_sizes is not util.mode_sizes_for_version(self.version):
            self.buffer=util.BitBuffer()
            util.generate_data(self.buffer,self.data_list,self.version)
            self.best_fit(start=self.version)
        return self.version

    def best_mask_pattern(self):
        """
        Find the most efficient mask pattern.
        """
        min_lost_point = 0
        pattern = 0

        for i in range(8):
            self.makeImpl(True, i)

            lost_point = util.lost_point(self.modules)

            if i == 0 or min_lost_point > lost_point:
                min_lost_point = lost_point
                pattern = i

        return pattern

    def setup_timing_pattern(self):
        for r in range(8, self.modules_count - 8):
            if self.modules[r][6] is not None:
                continue
            self.modules[r][6] = (r % 2 == 0)

        for c in range(8, self.modules_count - 8):
            if self.modules[6][c] is not None:
                continue
            self.modules[6][c] = (c % 2 == 0)

    def setup_position_adjust_pattern(self):
        pos = util.pattern_position(self.version)

        for i in range(len(pos)):

            for j in range(len(pos)):

                row = pos[i]
                col = pos[j]

                if self.modules[row][col] is not None:
                    continue

                for r in range(-2, 3):

                    for c in range(-2, 3):

                        if (r == -2 or r == 2 or c == -2 or c == 2 or
                                (r == 0 and c == 0)):
                            self.modules[row + r][col + c] = True
                        else:
                            self.modules[row + r][col + c] = False

    def setup_type_number(self, test):
        bits = util.BCH_type_number(self.version)

        for i in range(18):
            mod = (not test and ((bits >> i) & 1) == 1)
            self.modules[i // 3][i % 3 + self.modules_count - 8 - 3] = mod

        for i in range(18):
            mod = (not test and ((bits >> i) & 1) == 1)
            self.modules[i % 3 + self.modules_count - 8 - 3][i // 3] = mod

    def setup_type_info(self, test, mask_pattern):
        data = (self.error_correction << 3) | mask_pattern
        bits = util.BCH_type_info(data)

        # vertical
        for i in range(15):

            mod = (not test and ((bits >> i) & 1) == 1)

            if i < 6:
                self.modules[i][8] = mod
            elif i < 8:
                self.modules[i + 1][8] = mod
            else:
                self.modules[self.modules_count - 15 + i][8] = mod

        # horizontal
        for i in range(15):

            mod = (not test and ((bits >> i) & 1) == 1)

            if i < 8:
                self.modules[8][self.modules_count - i - 1] = mod
            elif i < 9:
                self.modules[8][15 - i - 1 + 1] = mod
            else:
                self.modules[8][15 - i - 1] = mod

        # fixed module
        self.modules[self.modules_count - 8][8] = (not test)

    def map_data(self, data, mask_pattern):
        inc = -1
        row = self.modules_count - 1
        bitIndex = 7
        byteIndex = 0

        mask_func = util.mask_func(mask_pattern)

        data_len = len(data)

        for col in xrange(self.modules_count - 1, 0, -2):

            if col <= 6:
                col -= 1

            col_range = (col, col-1)

            while True:

                for c in col_range:

                    if self.modules[row][c] is None:

                        dark = False

                        if byteIndex < data_len:
                            dark = (((data[byteIndex] >> bitIndex) & 1) == 1)

                        if mask_func(row, c):
                            dark = not dark

                        self.modules[row][c] = dark
                        bitIndex -= 1

                        if bitIndex == -1:
                            byteIndex += 1
                            bitIndex = 7

                row += inc

                if row < 0 or self.modules_count <= row:
                    row -= inc
                    inc = -inc
                    break

    def get_matrix(self):
        """
        Return the QR Code as a multidimensonal array, including the border.

        To return the array without a border, set ``self.border`` to 0 first.
        """
        if self.data_cache is None:
            self.make()

        if not self.border:
            return self.modules

        width = len(self.modules) + self.border*2
        code = [[False]*width] * self.border
        x_border = [False]*self.border
        for module in self.modules:
            code.append(x_border + module + x_border)
        code += [[False]*width] * self.border

        return code
