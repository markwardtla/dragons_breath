#!/usr/bin/env python

from __future__ import print_function, division

from datetime import datetime
import glob
from matplotlib import use

use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil

from astropy.io import fits

"""This module opens the *_bey.fits files output from
Dragons_Breath_Wrapper.py in matplotlib to record the positions of the
stars causing dragon's breath.

To record these positions the user will manually click on the offending
star which records the coordinates in a .log file. The following are the
rest of the user commands:
'n' to go on to the next image
'b' to mark images images with bad_dat
'v' to mark an images that user is unsure about
'q' to quit the program
'w' to write out the current log
'z' to undo a click (ie if the user clicked but did not mean to record
    that position)

Authors
-------
    Larissa Markwardt

Use
---
    This program is intended to be executed via the command line as
    such:

    >>> python Dragons_Breath_View_Bey.py

Output
-------
    The only output of this module is the .log file with coordinates.
    Note: this file will be located in the /grp/hst/wfc3t/sasp/code
    folder (ie NOT the data folder).

Dependencies
------------
    This module depends on astropy.
"""


class Logger:
    """This class handles writing the coordinates of offending stars to
    a log file.

    It is meant to be used as a file writing tool by the BeyViewer.

    Attributes
    ----------
    coords_list: list of strings
        List which contains strings of the form 'id xpos ypos'
        which represent the recorded star positions.

    Methods
    -------
    add_coord(self, identifier, x, y)
       Adds a single position to the end of the coords_list.
    undo(self):
        Removes the last item in the coords_list.
    write_out(self)
       Writes the current coords_list out to a time stamped log.
    """

    def __init__(self):
        """"Initializes the logger."""
        self.coords_list = []

    def add_coord(self, identifier, x, y):
        """"Adds a single position to the coords_list.

        Parameters
        ----------
        identifier: string
            The HST identifier that corresponds to the current image.
        x: float
            The x position of the star.
        y: float
            The y position of the star.
        """
        self.coords_list.append(
            '{} {} {}\n'.format(identifier, str(x), str(y)))

    def undo(self):
        """Removes the last item in the coords_list.

        In other words, should the user want to remove the last mouse click
        they can utilize this method to erase the last position added to the
        log.
        """
        self.coords_list.pop()

    def write_out(self):
        """Writes the current coords_list out to a time stamped log."""
        now = datetime.now()
        out_file = '/grp/hst/wfc3t/sasp/code/bey_viewer_{}_{}_{:02d}:{:02d}.log'. \
            format(now.month, now.day, now.hour, now.minute)

        with open(out_file, 'w') as f:
            for coord in self.coords_list:
                f.write(coord)


class BeyViewer:
    """This class handles actually displaying the bey images using
    matplotlib.

    Primarily, this class is able to loop through and plot all of the
    images in its list as well as controlling the event handlers.

    Parameters
    ----------
    path_list: list of strings
        List which contains the full paths of all of the images
        needing to be displayed.

    Attributes
    ----------
    _path_list: list of strings
        List which contains the full paths of all of the images needing
        to be displayed.
    _fig: matplotlib figure
        Figure object which is used to display the images.
    _log: Logger
        Logger object which is used to record mouse clicks.
    _should_run: bool
        Boolean which specifies whether or not the bey viewer should
        keep running.
    _is_bad: bool
        Boolean which determines whether or not the current image
        should be moved to the 'bad_data' folder.
    _question: bool
        Boolean that marks whether or not the current image should be
        put in the 'questionable' folder.

    Methods
    -------
    _on_click(event, rootname)
        Handles the mouse clicks in matplotlib.
    _on_key_press(event)
        Handles the keys pressed in matplotlib.
    _open_image(path)
        Opens one image (path) in matplotlib.
    run()
        Loops through showing all the images.
    """

    def __init__(self, path_list):
        """"Initializes the bey viewer.

        Parameters
        ----------
        path_list: list of strings
            List which contains the full paths of all of the images
            needing to be displayed.
        """
        self._path_list = path_list

        self._fig = None
        self._log = Logger()
        self._should_run = True
        self._is_bad = False
        self._question = False

    def _on_click(self, event, rootname):
        """Handles the mouse clicks in matplotlib.

        The x and y position of the mouse click is given to the logger
        so that they can be recorded in the log file.

        Parameters
        ----------
        event: button press event
            The button press event
        rootname: string
            The HST identifier for the image that was clicked.
        """
        if self._fig.canvas.manager.toolbar._active is None:
            clickx, clicky = event.xdata, event.ydata
            print('Clicked: {}, {}'.format(clickx, clicky))
            self._log.add_coord(rootname, clickx, clicky)

    def _on_key_press(self, event):
        """Handles the keys pressed in matplotlib.

        The following are accepted key presses:
        'n' to go on to the next image
        'b' to mark images with bad data
        'v' to mark an images that user is unsure about
        'q' to quit the program
        'w' to write out the current log
        'z' to undo a click (ie if the user clicked but did not mean to
            record that position)

        Parameters
        ----------
        event: key press event
            The key press event
        """
        if event.key == 'n':
            plt.close('all')

        if event.key == 'q':
            plt.close('all')
            self._should_run = False

        if event.key == 'w':
            self._log.write_out()

        if event.key == 'z':
            self._log.undo()

        if event.key == 'b':
            plt.close('all')
            self._is_bad = True

        if event.key == 'v':
            plt.close('all')
            self._question = True

    def _open_image(self, path):
        """Opens one image located at path in matplotlib.

        The program also automatically moves the matplotlib window and
        resizes it to look nice on Larissa's computer.

        Parameters
        ----------
        path: string
            Full path to the file to be displayed
        """
        # this is the unique HST identifier
        rootname = os.path.basename(path).replace('_bey.fits', '')
        print(rootname)

        self._fig = plt.figure()
        self._fig.suptitle(rootname)

        # This is to put the image on the left monitor, adjust the size,
        # and automatically make it the active window.
        plt.get_current_fig_manager().window.setGeometry(-2550, 0, 1250, 2000)
        plt.get_current_fig_manager().window.raise_()

        image_data = fits.getdata(path)
        mean = np.mean(image_data)

        plt.imshow(image_data, cmap='gray', vmin=0, vmax=4 * mean)
        plt.gca().invert_yaxis()
        plt.tight_layout()

        self._fig.canvas.mpl_connect('button_press_event',
                                     lambda event: self._on_click(event,
                                                                  rootname))
        self._fig.canvas.mpl_connect('key_press_event', self._on_key_press)

        plt.show()

    def run(self):
        """Loops through showing all the images.

        The loop terminates if should_run is flagged as False. It also
        moves the image to the appropriate folder once the user is done
        with it.
        """
        for path in self._path_list:
            self._open_image(path)

            if self._should_run:
                if self._is_bad:
                    shutil.move(path, '/grp/hst/wfc3t/sasp/data/bad_data')
                    self._is_bad = False
                    print('to bad data')
                elif self._question:
                    shutil.move(path, '/grp/hst/wfc3t/sasp/data/questionable')
                    self._question = False
                    print('to questionable')
                else:
                    shutil.move(path, '/grp/hst/wfc3t/sasp/data/completed')
                    print('to completed')

            else:
                break

        self._log.write_out()


def main():
    """Main function which at this time creates a bey viewer to run on
    all of the images currently in the /grp/hst/wfc3t/sasp/data folder
    (this should be all of the images that have not been looked at
    already).
    """
    print('Welcome to the bey viewer!')
    print('Valid commands are as follows:')
    print('n to go on to the next image')
    print("b to mark an image with bad data")
    print('v to mark an images that user is unsure about')
    print('q to quit the program')
    print('w to write out the current log')
    print('z to undo a click (ie if the user clicked but did not mean to record that position)')

    image_paths = sorted(glob.glob('/grp/hst/wfc3t/sasp/data/*_bey.fits'))

    viewer = BeyViewer(image_paths)
    viewer.run()


if __name__ == "__main__":
    main()
