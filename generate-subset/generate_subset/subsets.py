import os.path as path

import fontTools.subset as pyftsubset

from .subset import Subset
from .util import *

__all__ = ['Subsets']


class Subsets(_Pathable):
    """
    Manages list of Subset.
    """

    def __init__(self, fontname):
        super().__init__('def', fontname)

        self.sets = [
            Subset(fontname, filename)
            for filename in _ls(self.path)
            if not filename.startswith('.')
            if filename.endswith('.lst')
        ]

    def _ensure_sets_are_loaded(self, force_reload=False):
        """
        load all child subset(s) if not loaded (or force_reload given).
        """
        for subset in self.sets:
            subset.load(force_reload)

    def points(self):
        """
        gather all codepoints from child subset(s).
        """
        self._ensure_sets_are_loaded()
        return set().union(*self.sets)

    def omits(self, points):
        """
        Unicode codepoints that only appears on subset list.

        appearantly, this is handled by fonttools itself.
        """
        return self.points() - points

    def leftovers(self, points):
        """
        Unicode codepoints that only appears on actual font.

        usually includes codepoint '1' and '-1', both are handled by fonttools.
        """
        return points - self.points()

    @property
    def has_rest_subset(self):
        return not any(set.name.startswith('10000.') for set in self.sets)
