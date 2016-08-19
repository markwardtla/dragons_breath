#!/usr/bin/env python
from __future__ import print_function, division

from multiprocessing import Pool
import os
from shutil import copy
import glob

from sqlalchemy import or_

from pyql.database.ql_database_interface import Master
from pyql.database.ql_database_interface import session
from pyql.database.ql_database_interface import UVIS_flt_0


"""This script queries the Quicklook database for images potentially
   affected by dragons breath and copies them to
   /grp/hst/wfc3t/sasp/data.

Authors
-------
    Larissa Markwardt

Use
---
    This program is intended to be executed via the command line as
    such:

    >>> python Dragons_Breath_Query.py

Dependencies
------------
    This module depends on sqlalchemy and pyql.
"""


def copy_to_sasp(file_path):
    """This function copies the file located at file_path to
    /grp/hst/wfc3t/sasp/data/.

    Parameters
    ----------
    file_path: string
        Full path to the flt file.
    """
    files_in_dir = glob.glob('/grp/hst/wfc3t/sasp/data/*_flt.fits')
    basenames_in_dir = [os.path.basename(file) for file in files_in_dir]

    if os.path.basename(file_path) not in basenames_in_dir:
        try:
            print('Copying from ' + file_path)
            copy(file_path, '/grp/hst/wfc3t/sasp/data/')
            print(file_path + ' is done!')
        except IOError:
            print(file_path + ' does not exist!')

    else:
        print(file_path + ' is already in the directory.')


def main():
    """Main function which queries for all of the images that might be
    affected by Dragon's Breath and copies them to
    /grp/hst/wfc3t/sasp/data.

    The images that are to be included were taken with either the F606W
    or F814W filters and had an exposure time > 300 seconds.
    """

    results = session.query(Master.dir, Master.rootname).\
        join(UVIS_flt_0).filter(UVIS_flt_0.exptime > 300).\
        filter(or_(UVIS_flt_0.filter == 'F606W', UVIS_flt_0.filter == 'F814W')).\
        all()

    origin_paths = ['{}_flt.fits'.format(os.path.join(item.dir, item.rootname)) for item in results]

    print('Starting to copy images...')

    p = Pool(4)  # for linux server
    p.map(copy_to_sasp, origin_paths)

    print('Complete. All files copied over.')

if __name__ == "__main__":
    main()
