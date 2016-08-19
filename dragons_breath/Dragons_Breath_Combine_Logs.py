#!/usr/bin/env python

from __future__ import print_function, division

import glob

"""This module combines all of the log files output by the bey viewer
(found in /grp/hst/wfc3t/sasp/code) and combines them into one file,
master_log.txt.

Authors
-------
    Larissa Markwardt

Use
---
    This program is intended to be executed via the command line as
    such:

    >>> python Dragons_Breath_Combine_Logs.py

Output
-------
    This module writes the master_log.txt file to
    /grp/hst/wfc3t/sasp/code.
"""

class LogProcessor:
    """This class handles combining the log files.

    Attributes
    ----------
    _master_log_list: list of strings
        List which contains all of the lines in the previous logs.

    Methods
    -------
    read_log(log_path)
        Opens the log at the specified path and adds its contents to
        the master list.
    write_master_log(out_file)
        Writes the contents of the _master_log_list to out_file.
    """

    def __init__(self):
        """"Initializes the log processor."""
        self._master_log_list = list()

    def read_log(self, log_path):
        """Reads in all of the lines in a single log file at log_path
        and adds them to the master_log_list.

        Parameters
        ----------
        log_path : string
            The full path of the single log file.
        """
        with open(log_path, 'r') as f:
            for line in f:
                if line not in self._master_log_list and 'None' not in line:
                    self._master_log_list.append(line)

    def write_master_log(self, out_file):
        """Writes the contents of the _master_log_list to out_file

            Parameters
            ----------
                out_file : string
                    The name of the file to write the master log to.
        """
        with open(out_file, 'w') as f:
            for line in self._master_log_list:
                f.write(line)

def main():
    """Main function which feeds all of the log files in the code
    directory to the log processor and then tells it to write the
    results to master_log.txt.
    """
    lp = LogProcessor()

    logs = glob.glob('/grp/hst/wfc3t/sasp/code/bey_viewer*.log')
    for log in logs:
        lp.read_log(log)

    lp.write_master_log('/grp/hst/wfc3t/sasp/code/master_log.txt')


if __name__ == "__main__":
    main()
