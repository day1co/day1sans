import os.path as path
import itertools

from .util import *

__all__ = ['Subset']


class Subset(_Pathable, set):
    """
    Simple wrapper class to internal class, set, to provide load() / save(),
    unicode-range generation, and __repr__ wrap.
    """

    def __init__(self, fontname, filename='10000.rest.lst'):
        super().__init__('def', fontname, filename)

        self.fontname = fontname
        self.filename = filename
        self.loaded = False

    @property
    def name(self):
        """
        removes file extension from filename.
        """
        return self.filename.rpartition('.')[0]

    def load(self, force_reload=False):
        """
        loads subset file by current path.
        """
        if self.loaded and not force_reload:
            return
        if not self.filename:
            raise NameError('this subset is not related to actual file!')

        text = open(self.path, 'rt').read()
        points = set(ord(c) for c in text)

        self.clear()
        self |= points
        self.loaded = True

    def save(self):
        """
        save current subset to current path.
        """
        f = open(self.path, 'w')
        f.write(''.join(sorted(chr(c) for c in self)))
        f.close()

    def range(self):
        """
        generate CSS `unicode-range`-compatible list from current subset.
        """
        def to_hex(f, t=None):
            r = 'u+' + hex(f)[2:]
            if t is not None and f != t:
                r += '-' + hex(t)[2:]

            return r

        l = sorted(self)
        count = itertools.count()

        return ','.join(
            to_hex(_head, _tail[-1] if _tail else _head)
            for (k, (_head, *_tail))
            in itertools.groupby(l, lambda i: i - next(count))
        )

    def __repr__(self):
        prefix = ['not loaded', 'loaded'][self.loaded]
        orig = super().__repr__()
        return f'{self.fontname}/def/{self.filename} - {prefix} {orig}'
