import os
import os.path as path

__all__= [
    'FORMATS_TO_EXPORT',
    '_ls',
    '_Pathable'
]

"""
Listing a font formats to export, in order of css `src` priority.
key is file extension, and value is css type().
"""
FORMATS_TO_EXPORT = {
    '.woff2': 'woff2',
    '.woff': 'woff',
    '.otf': 'opentype'
}

def _ls(*pathspec):
    """
    just a os.listdir() wrapper.
    """
    return os.listdir(path.join(*pathspec))


class _Pathable:
    """
    Simple utility class to reduce repeated variable pattern.
    """

    def __init__(self, related_subdir, fontname, filename=None):
        self.subdir = related_subdir
        self.fontname = fontname
        self.filename = filename

    @property
    def path(self):
        if self.filename:
            return path.join(self.fontname, self.subdir, self.filename)
        else:
            return path.join(self.fontname, self.subdir)

    def _path_for(self, *_for):
        return path.join(self.path, *_for)
