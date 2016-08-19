#!/usr/bin/env python

from __future__ import print_function, division

import glob
from multiprocessing import Pool
import time
import subprocess

"""This module implements Jay Anderson's flt2mass.F code in order to
run it on many images in parallel.

Authors
-------
    Larissa Markwardt

Use
---
    This program is intended to be executed via the command line as
    such:

    >>> python Dragons_Breath_Wrapper.py

Output
-------
    The only things this module outputs are those which are created in
    Jay Anderson's code.

Dependencies
------------
    The user should also have flt2mass.e file in their directory.
"""


def flt2mass_one_image(file_path):
    """This function simply runs the flt2mass code on one image
    (whichever is specified in the input).

    Parameters
    ----------
    file_path: string
        The unique identifier which corresponds to an image with
        dragon's breath. (This is the first part of the flt file
        names).

    """
    subprocess.call('./flt2mass.e {}'.format(file_path), shell=True)


def main():
    """Main function which runs the flt2mass_one_image function on
    multiple images in parallel.

    Currently, this runs on all of the images in the data directory.
    """

    begin = time.time()
    p = Pool(20)  # for linux server
    paths = glob.glob('/grp/hst/wfc3t/sasp/data/*_flt.fits')

    p.map(flt2mass_one_image, paths)

    end = time.time()
    print(end-begin)

if __name__ == "__main__":
    main()

