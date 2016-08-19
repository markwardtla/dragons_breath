.. dragons_breath documentation master file, created by
   sphinx-quickstart on Wed Aug 17 10:12:40 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Dragons_Breath Documentation
============================

Welcome to the HST/WFC3 Dragon's Breath project!

This project was developed by Larissa Markwardt as part of the 2016 SASP
program at STScI. This project was actually 2 distinct subprojects. In the
first project WFC3 images and the areas beyond the detector were analyzed
to ultimately create a heatmap around the WFC3 detector where showing stars
trigger dragon's breath. For the second project, many archival WFC3 images were
flagged for anomalies revealing some statistics about how often anomalies occur
and which are most prevalent. There were a variety of modules developed
for this project but to follow the methods of this project they should be
run in the following order:

**1. Dragons_Breath_Query.py**

This module allows the user to query the Quicklook database to move all of the
images they want to include in their study to one directory.

Note: this step could be optional if the user already has access to the images
they want to do dragon's breath analysis on.

**2. Dragons_Breath_Wrapper.py**

This module should then be run for all images in the study. It will run Jay
Anderson's flt2mass.F code and produce a .bey file for each image.

**3. Dragons_Breath_View_Bey.py**

This module allows a user to interact with the .bey files produced in step 2 by
opening each .bey file in matplotlib so that the user can visually inspect
them. If there's dragon's breath and a clear offending star, then the user can
click on the corresponding circle in the .bey file which will send the position
to a time-stamped log. If not, the user should not click on anything (although
they will be able to use the pan and zoom functionality of the matplotlib
window without their clicks being saved). Then, the users will have a few
options:

1. The user can press 'n' to go onto the next image (the current image will be
   put in the completed folder).
2. The user can press 'b' to put the current image into the bad folder and
   move onto the next one.
3. The user can press 'v' to put the current image into the questionable
   folder and move onto the next one.

This will continue until the user quits or there are no more iamges.

**4. Dragons_Breath_Combine_Logs.py**

This module takes all of the log files produced in step 3 and combines them
into one master_log file.

**5. Dragons_Breath_Log_To_Table.py**

This module takes the master_log produced in step 4, the  \*_2PH.uvrd
files produced by Jay's code in step 2, and information from the Quicklook
database and combines them into one master_table.csv. In other words, it
produces a table that stores the following information for all of the stars
in all of the images in the study:

* rootname
* x_measured (image coordinates of a click, -1 if no associated db)
* y_measured (image coordinates of a click, -1 if no associated db)
* x_physical (physical coordinates of a click, -1 if no associated db)
* y_physical (physical coordinates of a click, -1 if no associated db)
* x_2mass (2mass coordinates of a star, matched to previous data if db)
* y_2mass (2mass coordinates of a star, matched to previous data if db)
* magnitude
* filter
* exposure time

**6. Update Done_Cals and Done_GOs**

At this point there is not a script for this task, but it is critical that
the Done_Cals and Done_GOs text files be updated before the final step if
one wants the pie charts for anomalies to be produced correctly. These files
are simply a list of all of the proposal ids that have already been analyzed.

**7a. Dragons_Breath_Make_Graphs.py**

This module creates several graphs from the data obtained in all of the
previous steps. Of note, this module creates all of the graphs used in
Larissa Markwardt's final presentation. These include:

* a heatmap of all of the stars in the study normalized to the number of
  stars in a bin
* pie charts representing how many anomalies occur in GO and Cal images as
  as well as both combined
* pie charts depicting what percent of the total anomalies each type
  constitues in GO and Cal image as well as both combined
* heatmap and matching histogram plots for one magnitude at a time which
  can be used to create a gif

**7b. Dragons_Breath_Graph_Data.py**

This module is not intended to be run like the previous ones, but someone
wants to create graphs different from those in Dragons_Breath_Make_Graphs.py
they could import this module to access all of the classes that store data
pertinent to this project.

*To see the results of this analysis from the SASP 2016 project, see the
presentation* `here <http://bit.ly/2b7oSkZ>`_

.. toctree::
   :maxdepth: 2

   modules.rst