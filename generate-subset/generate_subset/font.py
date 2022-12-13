import os.path as path

import fontTools.subset as pyftsubset

from .subsets import Subsets
from .subset import Subset
from .util import *

__all__ = ['Font']


class Font(_Pathable):
    """
    Wraps a font file (a single weight, single face) and do something with it.
    """

    def __init__(self, fontname, filename):
        super().__init__('original', fontname, filename)
        # TODO: check file existence

        [self.name, self.weight] = self._parse_font_filename(filename)

        self._cached_points = None
        self._ffobject = None

    def _parse_font_filename(self, filename):
        """
         split file names into tokens, and resolve which part is name and is
        weight.

        TODO: fix errorneous behavior with exactly one (or no) dot in filename

        [:-2] name   [-2] weight
        v            v
        SomeFontName.Regular.otf <- [-1] ext
        """
        [*name, weight, ext] = filename.rsplit('.', 2)

        if not name:
            raise KeyError(f'invalid fontfile name {filename}')

        return ['.'.join(name), weight]

    def _get_destpath(self, subset_name):
        """
        create a file path to save a subset.
        """
        return path.join(self.fontname, 'subset', self.weight, subset_name)

    def _ffopen(self, force_reopen=False):
        """
        opens self._ffobject using FontForge.

        TODO: remove fontforge
        """
        import fontforge # optional dependency

        if self._ffobject is None or force_reopen:
            if force_reopen:
                self._ffclose()

            self._ffobject = fontforge.open(self.path)

        return self._ffobject

    def _ffclose(self):
        """
        closes self._ffobject.
        """
        try:
            self._ffobject.close()
        finally:
            self._ffobject = None

    def points(self, force_reopen=False):
        """
        get list of Unicode codepoint from whole glyphs, using FontForge.
        """
        if not force_reopen and self._cached_points:
            return self._cached_points

        ff = self._ffopen()
        points = set()

        for glyph in ff.glyphs():
            points.add(glyph.unicode)
            # empty glyph were checked here, but now dont since fonttools do it
            points |= set(alt[0] for alt in glyph.altuni or [])

        self._cached_points = points
        return points

    def subset(self, subset):
        """
        subset font by defined subsets using pyftsubset.
        """
        opt = pyftsubset.Options()
        font = pyftsubset.load_font(self.path, opt)

        outbase = self._get_destpath(subset.name)

        subsetter = pyftsubset.Subsetter()

        subsetter.populate(unicodes=subset)
        subsetter.subset(font)

        for ext in FORMATS_TO_EXPORT.keys():
            pyftsubset.save_font(font, outbase + ext, opt)

        font.close()

    def css(self, subsets):
        """
        generate CSS @font-face rules using all they know.

        TODO: add font/local name resolution
        """
        assert isinstance(subsets, Subsets)

        rules = []

        for subset in subsets.sets:
            dest = self._get_destpath(subset.name)
            srcset = [
                f"    url('{dest}{ext}') format('{type}'),"
                for (ext, type) in FORMATS_TO_EXPORT.items()
            ]
            srcset[-1] = srcset[-1].rstrip(',') + ';'

            rule = [
                '@font-face {',
                f"  font-family: '{self.fontname}';",
                f"  font-weight: {self.weight.lower()};",
                f"  unicode-range: {subset.range()};",
                f"  src: local('{self.fontname}'),",
                *srcset,
                '}'
            ]
            rules.append('\n'.join(rule))

        return '\n\n'.join(rules)
