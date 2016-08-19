#!/usr/bin/env python

from __future__ import print_function, division

from collections import defaultdict
import os
import glob

from pyql.database.ql_database_interface import Master
from pyql.database.ql_database_interface import session
from pyql.database.ql_database_interface import UVIS_flt_0

"""This module combines information stored in the master_log.txt, *_2PH.uvrd
files, and Quicklook database to create master_table.csv which contains
information pertinent to creating a Dragons Breath analysis plot.

Authors
-------
    Larissa Markwardt

Use
---
    This program is intended to be executed via the command line as such:

    >>> python Dragons_Breath_Log_To_Table.py

Output
-------
    This module outputs master_table.csv which contains the following
    information, in order, for every star in all of the bey files:
    rootname
    x_measured (image coordinates of a click, -1 if no associated db)
    y_measured (image coordinates of a click, -1 if no associated db)
    x_physical (physical coordinates of a click, -1 if no associated db)
    y_physical (physical coordinates of a click, -1 if no associated db)
    x_2mass (2mass coordinates of a star, matched to previous data if db)
    y_2mass (2mass coordinates of a star, matched to previous data if db)
    magnitude
    filter
    exposure time

Dependencies
------------
    This module depends on sqlalchemy and pyql.
"""

class DictData:
    """This class is the superclass for all of the other data classes
    in this module.

    Note that an instance of DictData is a dictionary (with the keys
    being rootnames) of lists of dictionaries. So an example DictData
    might look like {id1:(), id2:({key:value, key:value}), id3:
    ({key:value, key:value}, {key:value, key:value})}

    Attributes
    ----------
    rootname: list of strings
        List which contains all of the rootnames for the DataDict.
        Note: these will eventually be the keys for the main_dict.
    main_dict: a dictionary of lists
        This structure stores all of the data for the DataDict.
        Ultimately, it is a dictionary of lists of dictionaries.

    Methods
    -------
    _add_single(rootname, dict)
        Appends a dictionary to the list associated with rootname.
    """

    def __init__(self):
        """"Initializes the DictData."""
        self.rootnames = [os.path.basename(x).replace('_bey.fits', '') for x in
                          glob.glob(
                              '/grp/hst/wfc3t/sasp/data/completed/*_bey.fits')]

        self.main_dict = defaultdict(list)

    def _add_single(self, rootname, dict):
        """Appends a single dictionary entry to the list associated with
        rootname.

        Parameters
        ----------
        rootname: string
            The HST id associated with the data being appended.
        dict: dictionary
            The dictionary needing to be added to the main_dict.
        """
        self.main_dict[rootname].append(dict)


class DataBaseData(DictData):
    """This class implements DictData to store the data found in the
    Quicklook database.

    It's lower level dictionary entries will be of the form:
    {'filter': string, 'exptime': float}
    Note: since each image will only have one filter and exposure time
    associated with it, accessing data from this structure will always
    look like the folowing:
    self.main_dict['some id'][0]['filter or exptime']
    (ie. the second set of brackets will always be a 0).

    Methods
    -------
    add_all_database_values()
        Goes through all of the rootnames and adds their respective
        filter and exposure time to the main_dict.
    """

    def __init__(self):
        """Initializes the DataBaseData"""
        DictData.__init__(self)

    def add_all_database_values(self):
        """Goes through all of the rootnames and adds their respective
        filter and exposure time to the main_dict.
        """
        for name in self.rootnames:
            result = session.query(UVIS_flt_0.filter, UVIS_flt_0.exptime). \
                join(Master). \
                filter(Master.rootname == name).all()

            filt = result[0].filter
            exptime = float(result[0].exptime)

            self._add_single(name, {'filter': filt, 'exptime': exptime})


class ClickData(DictData):
    """This class implements DictData to store the data found in the
    master_log.txt (ie the data representing all of the mouse clicks
    for db).

    It's lower level dictionary entries will be of the form:
    {'x': float, 'y': float}.

    Attributes
    ----------
    rootnames: list of strings
        This is different from most DictData rootnames as it always
        gets all of the rootnames stored in completed even if the
        program is only being run on a subset.

    Methods
    -------
    add_all_clicks()
        Goes through all of the lines in master_log.txt and adds the
        x and y values of clicks to the main_dict.
    """

    def __init__(self):
        """Initializes the DataBaseData

        Note: it initializes the rootnames to a different set than the
        other DictData classes; it always gets all of the rootnames
        stored in completed even if the program is only being run on a
        subset.
        """
        DictData.__init__(self)

        self.rootnames = [os.path.basename(x).replace('_bey.fits', '') for x in
                          glob.glob(
                              '/grp/hst/wfc3t/sasp/data/completed/*_bey.fits')]

    def add_all_clicks(self):
        """Goes through all of the lines in master_log.txt and adds the
        x and y values of clicks to the main_dict.
        """
        with open('/grp/hst/wfc3t/sasp/code/master_log.txt') as f:
            for line in f:
                id, x, y = line.split()
                click_dict = {'x': x, 'y': y}

                self._add_single(id, click_dict)


class AllStarsData(DictData):
    """This class implements DictData to store the data found in the
    *_2PH.uvrd files (ie the data representing all of the stars
    associated with each rootname).

    It's lower level dictionary entries will be of the form:
    {'x_2mass': float, 'y_2mass': float, 'mag': string}.

    Methods
    -------
    add_all_stars()
        Goes through all of the *_2PH.uvrd files and adds the x_2mass,
        y_2mass, and magnitude values for all of the stars associated
        with the rootnames.
    """

    def __init__(self):
        """Initializes the AllStarsData"""
        DictData.__init__(self)

    def add_all_stars(self):
        """Goes through all of the *_2PH.uvrd files and adds the x_2mass,
        y_2mass, and magnitude values for all of the stars associated with the
        rootnames.
        """
        basename = '/grp/hst/wfc3t/sasp/data/completed/'
        for name in self.rootnames:
            with open('{}{}_2PH.uvrd'.format(basename, name)) as f:
                for line in f:
                    row = line.split()

                    x_2mass = float(row[0])
                    y_2mass = float(row[1])
                    magnitude = row[6]
                    star_dict = {'x_2mass': x_2mass,
                                 'y_2mass': y_2mass,
                                 'mag': magnitude}

                    self._add_single(name, star_dict)


class DragonsBreathTable:
    """This class combines all of the information stored in the
    previous classes and writes them out to master_table.csv.

    Attributes
    ----------
    _star_data: AllStarsData
        Stores the information associated with the *_2PH.uvrd files.
    _click_data: ClickData
        Stores the information associated with the master_log.txt.
    _database_data: DataBaseData
        Stores the pertinent information that is in the database.
    _all_data: list
        A list which contians all of the rows of the master table. The
        rows are simply comma separated strings with all of the info.

    Methods
    -------
    create_table()
       Combines all of the information stored in the DictData variables
    find_2_mass(rootname, image_x, image_y)
        Goes through all of the stars associated with rootname to find
        one that matches where the user clicked (image_x and image_y).
    image_to_physical(ix, iy)
        Converts the image coordinates (ix, iy) to Jay's physical
        coordinates.
    write_table(filename)
        Writes the information in _all_data to filename.
    """

    def __init__(self):
        """ Initializes the DragonsBreathTable.

        This primarily involves creating all of the DictData objects and
        getting the infomation associated with them.
        """
        self._star_data = AllStarsData()
        self._star_data.add_all_stars()

        self._click_data = ClickData()
        self._click_data.add_all_clicks()

        self._database_data = DataBaseData()
        self._database_data.add_all_database_values()

        self._all_data = list()

    def create_table(self):
        """Handles the combining of all the DictData.

        This method loops through all of the clicks associated with a
        rootname and marks matching stars first. Then it loops through
        all the stars in the rootname and aggregates the info. If it
        was not marked as a match the x_image, y_image, x_physical,
        and y_physical are set to -1 which indicates there was no db
        caused by that star.
        """
        for rootname in self._star_data.main_dict:
            matches = list()
            clicks = list()

            dragons_breath_clicks = self._click_data.main_dict[rootname]
            for click in dragons_breath_clicks:
                click_x, click_y = float(click['x']), float(click['y'])
                match = self.find_2_mass(rootname, click_x, click_y)

                if match is not None:
                    matches.append(match)
                    clicks.append((click_x, click_y))

            for star in self._star_data.main_dict[rootname]:
                x_2mass = star['x_2mass']
                y_2mass = star['y_2mass']
                magnitude = star['mag']

                if (x_2mass, y_2mass) in matches:
                    index = matches.index((x_2mass, y_2mass))
                    x_image, y_image = clicks[index]

                    x_physical, y_physical = self.image_to_physical(
                        x_image, y_image)
                else:
                    x_image = y_image = x_physical = y_physical = -1

                filt = self._database_data.main_dict[rootname][0]['filter']
                exposure_time = self._database_data.main_dict[rootname][0]['exptime']

                data = (rootname, str(x_image), str(y_image), str(x_physical),
                        str(y_physical), str(x_2mass), str(y_2mass), magnitude,
                        filt, str(exposure_time))
                row = ','.join(data)
                self._all_data.append(row)

    def find_2_mass(self, rootname, image_x, image_y):
        """Goes through all of the stars associated with rootname to
        find one that matches where the user clicked (image_x and
        image_y).

        Note: at this time, a match must be within 100 pixels of the
        click.

        Parameters
        ----------
        rootname: string
            The HST id associated with the click.
        image_x: float
            Image x coordinate of click.
        image_y: float
            Image y coordinate of click.

        Returns
        -------
        match: (float, float)
            The 2mass coordinates of the matching star. If no match is
            found, then None will be returned instead.
        """
        physical_x, physical_y = self.image_to_physical(image_x, image_y)

        min_dist = 100 ** 2  # Searching for stars within 100 pixels
        match = (-1, -1)

        for star in self._star_data.main_dict[rootname]:
            x_2mass = float(star['x_2mass'])
            y_2mass = float(star['y_2mass'])

            dist_squared = (physical_x - x_2mass) ** 2 + (physical_y - y_2mass) ** 2

            if dist_squared < min_dist:
                min_dist = dist_squared
                match = (x_2mass, y_2mass)

        if match == (-1, -1):
            print("No matching 2mass star was found!")
            with open('/grp/hst/wfc3t/sasp/code/mismatched.txt', 'a') as f:
                f.write(rootname + '\n')
            return None
        else:
            return match

    def image_to_physical(self, ix, iy):
        """Converts the image coordinates (ix, iy) to Jay's physical
        coordinates.

        Parameters
        ----------
        ix: float
            Image x coordinate.
        iy: float
            Image y coordinate.

        Returns
        -------
        px: float
            Physical x coordinate.
        py: float
            Physical y coordinate.
        """
        px = 1 + (ix - 500) * 3
        py = 1 + (iy - 478) * 3

        return px, py

    def write_table(self, filename):
        """ Writes all of the information in _all_data to filename.

        Parameters
        ----------
        filename: string
            The output file name.
        """
        with open(filename, 'w') as f:
            for row in self._all_data:
                f.write(row + '\n')


def main():
    """Main function which runs the DragonBreathTable and currently writes the
    result to master_table.csv.
    """
    table = DragonsBreathTable()
    table.create_table()
    table.write_table('/grp/hst/wfc3t/sasp/code/master_table.csv')


if __name__ == "__main__":
    main()
