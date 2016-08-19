#!/usr/bin/env python

from __future__ import print_function, division

from matplotlib import gridspec
import matplotlib.pyplot as plt

from Dragons_Breath_Graph_Data import OneMagHeatMap, PieChartData, \
    DragonsBreathHist, FullHeatMap

"""This module implements the classes in Dragons_Breath_Graph_Data to
create the plots used in Larissa's final presentation.

Authors
-------
    Larissa Markwardt

Use
---
    This program is intended to be executed via the command line as
    such:

    >>> python Dragons_Breath_Make_Graphs.py

Output
-------
    Several of the functions within this module have the option to save
    the graphs to a specific file, but currently plots are simply
    displayed on the screen.

Dependencies
------------
    This module depends on the Dragons_Breath_Graph_Data module.
"""

def main_full_heatmap(save_file=''):
    """Handles creating and then labeling the full heatmap.

    Parameters
    ----------
    fig: figure object
        The figure object the pie chart should be graphed to.
    ax: axis object
        The axis object corresponding to the figure.
    save_file: string
        The path to which the heatmap should be saved.
    """
    fig = plt.figure()
    ax = plt.gca()
    fhmd = FullHeatMap('/grp/hst/wfc3t/sasp/code/master_table.csv')

    fhm_cax = fhmd.plot_heatmap(fig, ax, True, True)
    cbar = fig.colorbar(fhm_cax, ticks=[-1, 0, 1])
    cbar.ax.set_yticklabels(
        ['100% No DB stars', 'Equilibrium', '100% DB stars'])

    plt.title('Dragon\'s Breath Map for All Stars', fontsize='x-large')

    if save_file == '':
        plt.show()
    else:
        plt.savefig(save_file)


def make_heatmap_and_hist(mag, hist, show_plot):
    """Handles creating and then labeling the one magnitude heatmap and
    corresponding histogram.

    Parameters
    ----------
    mag: int
        The magnitude that should be plotted int he heatmpa.
    fig: figure object
        The figure object the pie chart should be graphed to.
    ax: axis object
        The axis object corresponding to the figure.
    show_plot: bool
        A boolean representing whether to the plot should be saved to
        a file of simply displayed on the screen.
    """
    fig = plt.figure(mag, figsize=(15, 11.25))
    gs = gridspec.GridSpec(9, 3)

    mag_map = OneMagHeatMap('/grp/hst/wfc3t/sasp/code/master_table.csv', mag)
    plt.subplot(gs[:, :-1])
    ax_2 = plt.gca()
    mag_map.plot_heatmap(fig, ax_2, False)
    plt.title('Map of Dragon\'s Breath for Magnitude {} stars'.format(mag),
              fontsize='xx-large')

    plt.subplot(gs[1:-1, -1])
    hist.plot_hist(mag)

    fig.tight_layout()

    if show_plot:
        plt.show()
    else:
        plt.savefig('db_map_mag_{}.jpg'.format(mag))


def main():
    """Main function which calls the plotting methods for all of the
    pie charts, histograms, and heatmaps.
    """
    main_full_heatmap()

    pie = PieChartData('go')
    pie.make_full_pie_chart(320)
    plt.tight_layout()
    plt.show()

    pie.make_anomaly_pie_chart()
    plt.show()

    pie = PieChartData('cal')
    pie.make_full_pie_chart(260)
    plt.show()

    pie.make_anomaly_pie_chart(305)
    plt.show()

    pie = PieChartData('all')
    pie.make_full_pie_chart(260)
    plt.show()

    pie.make_anomaly_pie_chart()
    plt.show()

    hist = DragonsBreathHist('/grp/hst/wfc3t/sasp/code/master_table.csv')

    for i in range(20):
        make_heatmap_and_hist(i, hist, True)


if __name__ == "__main__":
    main()
