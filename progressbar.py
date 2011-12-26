import sys


def progressbar(it, prefix="", size=60):
    count = len(it)

    if not count:
        return

    def _show(_i):
        x = int(size * _i / count)
        sys.stderr.write("%s[%s%s] %i/%i\r" % (prefix,
            "#" * x, "." * (size - x), _i, count))
        sys.stderr.flush()

    _show(0)
    for i, item in enumerate(it):
        yield item
        _show(i + 1)
    sys.stderr.write('\n')
