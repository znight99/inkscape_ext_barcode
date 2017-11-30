from hanxin.main import Hanxin, make

def run_example(data="http://www.imu.edu.cn", *args, **kwargs):
    """
    Build an example Hanxin and display it.

    There's an even easier way than the code here though: just use the ``make``
    shortcut.
    """
    hx = Hanxin(*args, **kwargs)
    hx.add_data(data)

    im = hx.make_image()
    im.show()


if __name__ == '__main__':
    import sys
    run_example(*sys.argv[1:])
