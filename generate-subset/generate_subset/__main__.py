import os
import os.path as path
import sys
import argparse
import logging

from .font import Font
from .subset import Subset
from .subsets import Subsets
from .util import *


parser = argparse.ArgumentParser(
    description='Process font assets by subsetting and conversion.'
)

parser.add_argument(
    'font',
    nargs='+',
    help='a font directory, correctly structured under ' +
         'v2/assets/fonts.'
)
# functionals
parser.add_argument(
    '-v', '--verbose',
    dest='verbose',
    action='count',
    default=0,
    help='lower log level by 1 (internally 10).'
)
parser.add_argument(
    '-q', '--quiet',
    dest='quiet',
    action='count',
    default=0,
    help='raise log level by 1 (internally 10).'
)
# parser.add_argument('-j')
# flags
parser.add_argument(
    '-r', '--autorest',
    dest='autorest',
    action='store_const',
    const=1,
    default=0,
    help="calculate '10000.rest' subset target automatically."
)
parser.add_argument(
    '-R', '--save-autorest',
    dest='autorest',
    action='store_const',
    const=10,
    default=0,
    help="(over)write '10000.rest.lst' subset as calculated. implies -r."
)
parser.add_argument(
    '--version',
    action='version',
    version='%(prog)s 0.1.0'
)

arg = parser.parse_args()

error_level = logging.WARNING + 10 * (arg.quiet - arg.verbose)

log_handler = logging.StreamHandler()
log_handler.setLevel(level=error_level)
log_handler.setFormatter(logging.Formatter(fmt=logging.BASIC_FORMAT))

for fontname in arg.font:
    logger = logging.getLogger('generate-subset.' + fontname)
    logger.setLevel(level=error_level)
    logger.addHandler(log_handler)

    fontfiles = _ls(fontname, 'original')
    cssfile = open(path.join(fontname, 'style.css'), 'wt')

    ss = Subsets(fontname)
    logger.info('%d subset definition(s) found.', len(ss.sets))

    for fontpath in fontfiles:
        filename = path.basename(fontpath)

        try:
            logger.info('grabbing font face: %s', fontpath)
            font = Font(fontname, filename)
        except KeyError as e:
            logger.warning('skipping %s by KeyError: %s', fontpath, e)
            continue

        omitted = ss.omits(font.points())
        leftovers = ss.leftovers(font.points())
        logger.info('%d glyphs, %d in subset only, %d in font only.',
                    len(font.points()),
                    len(omitted),
                    len(leftovers))

        os.makedirs(
            path.join(ss.path, font.weight),
            exist_ok=True
        )

        if arg.autorest > 0 and len(leftovers) > 2 and ss.has_rest_subset:
            logger.info(f'calculating 10000.rest...')
            ss_rest = Subset(fontname)
            ss_rest |= set(i for i in leftovers if i > 0)
            ss.sets.append(ss_rest)

            if arg.autorest >= 10:  # save option
                logger.info(f'writing 10000.rest.lst...')
                ss_rest.save()

        for subset in sorted(ss.sets, key=lambda s: s.name):
            logger.info('processing subset %s (%d glyphs)...',
                        subset.name, len(subset))
            font.subset(subset)

        logger.info(f'creating CSS...')
        cssfile.write(font.css(ss) + '\n\n')

    logger.info(f'complete')
    cssfile.close()
