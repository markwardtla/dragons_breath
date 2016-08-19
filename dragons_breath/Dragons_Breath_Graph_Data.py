#!/usr/bin/env python

from __future__ import print_function, division

import glob
import math

from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from pyql.database.ql_database_interface import Master
from pyql.database.ql_database_interface import session
from pyql.database.ql_database_interface import Anomalies

"""This module contains everything needed to create all of the graphs
for Dragons' Breath analysis.

Three main types of graphs can be created: a histogram which plots the
number of stars that did and did not cause dragons breath, pie charts
showing the amount of anomalies, and heatmaps showing the location of
stars that triggered Dragon's Breath with respect to the detector.

Authors
-------
    Larissa Markwardt

Use
---
    This module is intended to be imported by a graphing script.


Dependencies
------------
    This module depends on sqlalchemy and pyql. The user should also
    have access to the Done_Cals.txt and Done_GOs.txt files.
"""

class DragonsBreathHist:
    """This class stores all of the information needed for the
    histogram as well as providing a function to plot it.

    Attributes
    ----------
    min_mag: int
        The minimum magnitude that should be plotted on the histogram.
    max_mag: int
        The maximum magnitude that should be plotted on the histogram.
    mags_db: list of floats
        List of the magnitudes of stars that caused Dragon's Breath.
    mags_no_db: list of floats
        List of the magnitudes of stars that did not cause Dragon's
        Breath.

    Methods
    -------
    _read_csv(self, data_file)
       Opens the data_file, extracts the magnitude information, and
       adds it to the magnitude lists.
    plot_hist(self, highlight=-1)
        Creates a histogram using both the mags_db and mags_no_db data.
    """

    def __init__(self, data_file):
        """Intializes the DragonsBreathHist."""
        self.min_mag = 0
        self.max_mag = 20
        self.mags_db = list()
        self.mags_no_db = list()

        self._read_csv(data_file)

    def _read_csv(self, data_file):
        """"Opens the data_file, extracts the magnitude information,
        and adds it to the magnitude lists.

        Note: the data_file should have the same format as the
        master_table.csv.

        Parameters
        ----------
        data_file: string
            Path to the file that contains the information (in
            particular magnitudes) for all the stars.
        """
        with open(data_file, 'r') as f:
            for line in f:
                row = line.split(',')

                measured_x = float(row[1])
                mag = float(row[7])

                if measured_x == -1:
                    self.mags_no_db.append(mag)
                else:
                    self.mags_db.append(mag)

    def plot_hist(self, highlight=-1):
        """"Plots the information stord in self.mags_db and
        self.mags_no_db as a histogram.

        One magnitude bar (indicated by the highlight parameter) may
        also be highlighted for emphasis.

        Parameters
        ----------
        highlight: int
            An integer that can equal -1 or range form self.min_mag to
            self.max_mag. If highlight equals -1 no bar will be
            highlighted. Otherwise the magnitude bar equal to highlight
            will be highlighted.
        """
        bins = np.arange(self.min_mag, self.max_mag + 1, 1)

        N, bins, no_db_patches = plt.hist(self.mags_no_db, bins,
                                          label="No Dragon's Breath",
                                          color='green')
        N, bins, db_patches = plt.hist(self.mags_db, bins,
                                       label="Dragon's Breath", color='blue')

        plt.legend(loc='upper left')

        if highlight != -1:
            try:
                db_patches[highlight].set_facecolor('red')
                no_db_patches[highlight].set_facecolor('orange')
            except IndexError:
                print('Error: the {} bin does not exist!'.format(highlight))

        plt.yscale('log')
        plt.ylabel('Log of Number of Stars', fontsize='x-large')
        plt.xlabel('Magnitude', fontsize='x-large')


class HeatMapData:
    """This class stores all of the information needed for heatmpas as well
    as providing a function to generically plot it.

    Attributes
    ----------
    x_max: int
        The maximum x coordinate for the image.
    y_max: int
        The maximum y coordinate for the image.
    db_data: 2-D numpy array of ints
        A 2-D array which stores how many stars did and did not cause
        Dragon's Breath at that x,y position.
    num_stars: 2-D numpy array of ints
        A 2-D array which stores how many stars were at that x,y
        position.

    Methods
    -------
    _image_to_physical(ix, iy)
        Converts the image coordinates (ix, iy) to Jay's physical
        coordinates.
    _physical_to_image(px, py)
        Converts Jay's physical coordinates (px, py) to image
        coordinates.
    _plot_detector(ax, bin_size)
        Adds two rectangles that represent the detector to the figure
        associated with ax.
    plot_heatmap(self, in_fig, in_ax, normalized, dark_background=False, bin_size=15)
        Plots the data stored in db_data as a heatmap.
    """

    def __init__(self):
        """Initializes the HeatMapData."""
        self.x_max = 2370   # Based on the size of Jay's Bey files.
        self.y_max = 2370
        self.db_data = np.zeros((self.y_max, self.x_max))
        self.num_stars = np.zeros((self.y_max, self.x_max))

    def _image_to_physical(self, ix, iy):
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

    def _physical_to_image(self, px, py):
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
        ix = (px - 1) / 3 + 500
        iy = (py - 1) / 3 + 478

        return ix, iy

    def _plot_detector(self, ax, bin_size):
        """Adds two rectangles that represent the detector to the
        figure associated with ax.

        Parameters
        ----------
            ax: axis object
                The axis object associated with a heatmap figure.
            bin_size: (int, int)
                The size of the pixel bins in the heatmap.
        """
        lower_left_2 = [502, 502]
        lower_right_2 = [1870, 585]
        upper_left_2 = [506, 1180]
        upper_right_2 = [1866, 1270]

        lower_left_1 = [506, 1193]
        lower_right_1 = [1865, 1285]
        upper_left_1 = [509, 1863]
        upper_right_1 = [1861, 1962]

        points_1 = [np.divide(lower_left_1, bin_size),
                    np.divide(upper_left_1, bin_size),
                    np.divide(upper_right_1, bin_size),
                    np.divide(lower_right_1, bin_size)]

        points_2 = [np.divide(lower_left_2, bin_size),
                    np.divide(upper_left_2, bin_size),
                    np.divide(upper_right_2, bin_size),
                    np.divide(lower_right_2, bin_size)]

        chip_1 = patches.Polygon(points_1, facecolor='white')
        chip_1.set_hatch('/')
        ax.add_patch(chip_1)

        chip_2 = patches.Polygon(points_2, facecolor='white')
        chip_2.set_hatch('/')
        ax.add_patch(chip_2)


    def plot_heatmap(self, in_fig, in_ax, normalized, dark_background=False, bin_size=15):
        """Plots the data in db_data and num_stars as a heatmap.

        If normalized is True then the value for each bin will be
        divided by the number of stars in the bin. Also of note, this
        plot will not label the colorbar on its own, so it returns the
        colorbar axis to be modified independently by the user.

        Parameters
        ----------
        in_fig: matplotlib figure object
            The figure the heatmap should be plotted on.
        in_ax: matplotlib axis object
            The axis associated with the heatmap figure.
        normalized: bool
            Determines whether or not the db_data should be normalized
            for the heatmap.
        dark_background: bool
            Switches the scale line to white if the background is going
            to be dark.
        bin_size: int
            The size of the bins for the heatmap.

        Returns
        -------
        cax: colorbar axis object
            Colorbar axis.
        """
        fig = in_fig
        ax = in_ax

        # This is bin the db_data and num_stars data to the larger pixel size.
        want = (bin_size, bin_size)
        self.db_data = self.db_data.reshape(self.y_max // want[0], want[0],
                                            self.x_max // want[1],
                                            want[1]).sum(3).sum(1)

        self.num_stars = self.num_stars.reshape(self.y_max // want[0], want[0],
                                                self.x_max // want[1],
                                                want[1]).sum(3).sum(1)

        if normalized:
            # This keeps the code from dividing by 0 (ie. if there were 0 stars
            # in that bin). If that is the case that bin is set to -1.
            with np.errstate(divide='ignore', invalid='ignore'):
                normalized = np.true_divide(self.db_data, self.num_stars)
                normalized[normalized == np.inf] = -1
                normalized[np.isnan(normalized) == True] = -1

            cax = ax.imshow(normalized, interpolation='none', cmap='bwr',
                            vmin=-1, vmax=1)

        else:
            cax = ax.imshow(self.db_data, interpolation='none', cmap='bwr',
                            vmin=-1, vmax=1)

        plt.gca().invert_yaxis()

        plt.axis('off')

        self._plot_detector(ax, want)

        if dark_background:
            color = 'white'
        else:
            color = 'black'
        ax.add_line(Line2D([10.5, 20.5], [10, 10], linewidth=2, color=color))
        ax.text(15.5, 8.5, '150 pixels', horizontalalignment='center',
                verticalalignment='top', fontsize='large', color=color)

        ax.set_adjustable("box-forced")  # to force pixels to be square

        return cax


class FullHeatMap(HeatMapData):
    """This class is a subclass of HeatMapData which specifies how the
    data should be read in from master_table.csv for a heatmap
    including all magnitudes of stars.

    Methods
    -------
    _read_csv(data_file)
       Reads in the pertinent data from data_file.
    """

    def __init__(self, data_file):
        """Initializes the FullHeatMap."""
        HeatMapData.__init__(self)
        self._read_csv(data_file)

    def _read_csv(self, data_file):
        """Reads in the pertinent data from data_file.

        This includes the physical x,y positions of all of the stars in the
        file. Note: this file should have the same format as master_table.csv.
        """
        with open(data_file, 'r') as f:
            for line in f:
                row = line.split(',')

                measured_x = float(row[1])
                phys_x = round(float(row[5]))
                phys_y = round(float(row[6]))

                im_x, im_y = self._physical_to_image(phys_x, phys_y)
                if 0 <= im_x < self.x_max and 0 <= im_y < self.y_max:
                    if measured_x == -1:
                        self.db_data[im_y][im_x] -= 1
                        self.num_stars[im_y][im_x] += 1
                    else:
                        self.db_data[im_y][im_x] += 1
                        self.num_stars[im_y][im_x] += 1


class OneMagHeatMap(HeatMapData):
    """This class is a subclass of HeatMapData which specifies how the
    data should be read in from master_table.csv for a heatmap
    including only the stars of a specified magnitude

    Attributes
    ----------
    _magnitude: int
        The magnitude of stars to be included in the heatmap.

    Methods
    -------
    _read_csv(data_file)
       Reads in the pertinent data from data_file.
    """
    def __init__(self, data_file, magnitude):
        """Initializes the OneMagHeatMap."""
        HeatMapData.__init__(self)
        self._magnitude = magnitude
        self._read_csv(data_file)

    def _read_csv(self, data_file):
        """Reads in the pertinent data from data_file.

        In this case, it would be the physical coordinates and
        magnitude of each star. Then, only the stars that match the
        specified magnitude will be added to db_data. Note: the
        data_file should have the same form as master_table.csv.
        """
        with open(data_file, 'r') as f:
            for line in f:
                row = line.split(',')

                measured_x = float(row[1])
                phys_x = round(float(row[5]))
                phys_y = round(float(row[6]))
                in_mag = math.floor(float(row[7]))

                im_x, im_y = self._physical_to_image(phys_x, phys_y)
                if 0 <= im_x < self.x_max and 0 <= im_y < self.y_max:
                    if measured_x == -1:
                        self.num_stars[im_y][im_x] += 1
                    else:
                        if in_mag == self._magnitude:
                            self.db_data[im_y][im_x] += 1
                            self.num_stars[im_y][im_x] += 1
                        else:
                            self.num_stars[im_y][im_x] += 1


class PieChartData:
    """This class stores information required to make the pie charts on
    anomolies.

    Note: using this class will require Done_Cals.txt and Done_GOs.txt
    to be in the same directory as the program. These files should
    simply include a list of proposal ids which have been flagged for
    anomalies.

    Attributes
    ----------
    go_or_cal: string
        String that specifies if the pie chart is just for the GO or
        Cal proposals or both. Valid stings are 'go', 'cal', or 'all'.
    _cal_ids: list of strings
        List of all the Cal proposal ids that were in Don_Cals.txt.
    _go_ids: list of strings
        List of all the GO proposal ids that were in Don_GO.txt.
    total_images: int
        Number of all the images in all of the proposals.
    num_anomalies: dict
        Dictionary with names of anomalies as keys and the value being
        how many there were in all the proposals.
    num_known_features: dict
        Dictionary with names of known features as keys and the value
        being how many there were in all the proposals.
    num_with_anomalies: int
        Number of images that had some kind of anomaly.

    Methods
    -------
    _get_id_lists()
        Reads in the proposal ids from Done_Cals.txt and Done_GOs.txt.
    get_total_images()
        Gets the total number of images in all of the proposals.
    get_one_type_anomaly(anomaly, present=1)
        Gets all of the images that contain the specified anomaly.
    get_num_anomalies()
        Gets the total number of anomalies and know features that
        occurred in all of the proposals.
    get_num_images_with_anomalies()
        Gets the number of images that had some sort of anomaly or
        known feature in them.
    make_full_pie_chart(start_angle=45)
        Makes a pie chart depicting what percentage of images had
        anomalies or known features.
    make_anomaly_pie_chart(start_angle=220)
        Makes a pie chart that shows the percentage of each type of
        anomaly out of the total number of anomalies.

    """

    def __init__(self, go_or_cal):
        """Initializes the PieChartData."""
        self._go_or_cal = go_or_cal
        self._cal_ids, self._go_ids = self._get_id_lists()

        self.total_images = self.get_total_images()

        self.num_anomalies = {'cr_shower': 0,
                              'data_transfer_error': 0,
                              'diamond': 0,
                              'dragons_breath': 0,
                              'earth_limb': 0,
                              'prominent_blobs': 0,
                              'scattered_light': 0,
                              'other': 0}
        self.num_known_features = {'calwf3_sub_error': 0,
                                   'crosstalk': 0,
                                   'cte_correction_error': 0,
                                   'detector_filter_ghost': 0,
                                   'diffraction_spike': 0,
                                   'figure8_ghost': 0,
                                   'fringing': 0,
                                   'ir_banding': 0,
                                   'persistence': 0,
                                   'excessive_saturation': 0,
                                   'guidestar_failure': 0,
                                   'satellite_trail': 0,
                                   'filter_ghost': 0}

        self.get_num_anomalies()
        self.num_with_anomalies = self.get_num_images_with_anomalies()

    def _get_id_lists(self):
        """Reads in the proposal ids from Done_Cals.txt and
        Done_GOs.txt.

        Note: it will actually only read in the files that are
        pertinent based on self.go_or_cal.

        Returns
        -------
        cal_list: list of strings
            List of the finished Cal proposals.
        go_list: list of strings
            List of the finshed GO proposals.
        """
        cal_list = list()
        go_list = list()

        if self._go_or_cal == 'cal' or self._go_or_cal == 'all':
            with open('Done_Cals.txt', 'r') as f:
                for line in f:
                    cal_list.append(line.strip())

        if self._go_or_cal == 'go' or self._go_or_cal == 'all':
            with open('Done_GOs.txt', 'r') as f:
                for line in f:
                    go_list.append(line.strip())

        return cal_list, go_list

    def get_total_images(self):
        """Gets the total number of images in all of the proposals.

        Returns
        -------
        sum(num_images) : int
            Num_images is a list of all the numbers of images in each
            proposal so it's sum is the total number of images.
        """
        num_images = list()

        for one_id in self._cal_ids:
            path = '/grp/hst/wfc3a/*_Links/{}/Visit*/*flt.fits'.format(one_id)
            num = len(glob.glob(path))
            num_images.append(num)

        for one_id in self._go_ids:
            path = '/grp/hst/wfc3a/*_Links/{}/Visit*/*flt.fits'.format(one_id)
            num = len(glob.glob(path))
            num_images.append(num)

        return sum(num_images)

    def get_one_type_anomaly(self, anomaly, present=1):
        """Gets all of the images that contain the specified anomaly.

        Parameters
        ----------
        present: int (either 0 or 1)
            If present = 1 then this function counts the number of images
            that contain that anomaly. If present = 0 then instead it
            counts the number of images that did not include that anomaly.

        Returns
        -------
        looked_at_with_anomaly: list of tuples of strings
            List of (link, rootname) for each image that contains the
            specified anomaly.
        """
        rootnames_with_anomaly = session.query(Anomalies.rootname). \
            filter(getattr(Anomalies, anomaly) == present).all()
        rootnames_with_anomaly = [rootname[0][0:8] for rootname in
                                  rootnames_with_anomaly]

        results = session.query(Master.link, Master.ql_root). \
            filter(Master.ql_root.in_(rootnames_with_anomaly)).all()
        links = [item.link[-5:] for item in results]
        rootnames = [item.ql_root for item in results]

        looked_at_with_anomaly = [(link, rootname) for link, rootname in
                                  zip(links, rootnames) if
                                  link in self._cal_ids or link in self._go_ids]
        return looked_at_with_anomaly

    def get_num_anomalies(self):
        """Gets the total number of anomalies and know features that occurred
        in all of the proposals.

        Returns
        -------
        num: int
            Total number of anomalies and known features.
        """
        num = 0
        for anomaly in self.num_anomalies:
            num_of_one_type = len(self.get_one_type_anomaly(anomaly))
            self.num_anomalies[anomaly] = num_of_one_type
            num += num_of_one_type
        for feature in self.num_known_features:
            num_of_one_type = len(self.get_one_type_anomaly(feature))
            self.num_known_features[feature] = num_of_one_type
            num += num_of_one_type

        return num

    def get_num_images_with_anomalies(self):
        """Gets the number of images that had some sort of anomaly or
        known feature in them.

        Note: an image that contains more than one anomaly should not
        be counted twice.

        Returns
        -------
        len(with_anomalies): int
            Length of with_anomalies which is a list of all the
            rootnames that have an anomaly in them.
        """
        with_anomalies = set()

        for anomaly in self.num_anomalies:
            anomalies = self.get_one_type_anomaly(anomaly)
            if len(anomalies) != 0:
                rootnames = set(zip(*anomalies)[1])
                with_anomalies.update(rootnames)

        for feature in self.num_known_features:
            features = self.get_one_type_anomaly(feature)
            if len(features) != 0:
                rootnames = set(zip(*features)[1])
                with_anomalies.update(rootnames)

        return len(with_anomalies)

    def make_full_pie_chart(self, start_angle=45):
        """Makes a pie chart depicting what percentage of images had
        anomalies or known features.

        Parameters
        ----------
        start_angle: int
            The start angle of the pie chart (set to 45 degrees by
            default).
        """
        labels = 'No Anomalies', 'Anomalies and Known Features'

        num_without_anomalies = self.total_images - self.num_with_anomalies

        percents = [num_without_anomalies / self.total_images,
                    self.num_with_anomalies / self.total_images]
        colors = ['lightsage', 'lightcoral']
        explode = (0, 0.2)

        plt.title('{} Images Affected by Anomolies'.
                  format(self._go_or_cal.capitalize()), fontsize=20)
        patches, texts, autotexts = plt.pie(percents, explode=explode,
                                        labels=labels, colors=colors,
                                        autopct='%1.1f%%', shadow=True,
                                        startangle=start_angle)
        texts[0].set_fontsize('large')

    def make_anomaly_pie_chart(self, start_angle=220):
        """Makes a pie chart that shows the percentage of each type of
        anomaly out of the total number of anomalies.

        Parameters
        ----------
        start_angle: int
            The start angle of the pie chart (set to 220 degrees by
            default).
        """
        labels = list()
        percents = list()
        total_anomalies = self.get_num_anomalies()
        adjust_anomaly_color = 0
        adjust_feature_color = 0

        for anomaly in sorted(self.num_anomalies):
            if self.num_anomalies[anomaly] > 1:
                percent = self.num_anomalies[anomaly] / total_anomalies * 100
                percents.append(percent)
                labels.append('{0} - {1:.2f}%'.format(anomaly, percent))
            else:
                adjust_anomaly_color += 1

        for feature in sorted(self.num_known_features):
            if self.num_known_features[feature] > 1:
                percent = self.num_known_features[
                              feature] / total_anomalies * 100
                percents.append(percent)
                labels.append('{0} - {1:.2f}%'.format(feature, percent))
            else:
                adjust_feature_color += 1

        colors = list()

        reds = plt.get_cmap('Reds')
        num_anomalies_in_chart = len(self.num_anomalies) - adjust_anomaly_color
        for i in np.linspace(0.2, 1, num_anomalies_in_chart):
            colors.append(reds(i))

        blues = plt.get_cmap('Blues')
        num_anomalies_in_chart = len(self.num_known_features) - adjust_feature_color
        for i in np.linspace(0.2, 1, num_anomalies_in_chart):
            colors.append(blues(i))

        plt.title('Prevalence of Detected Anomalies and Known Features in {}'.
                  format(self._go_or_cal.capitalize()))
        plt.pie(percents, labels=labels, colors=colors, startangle=start_angle,
                labeldistance=1.06)
