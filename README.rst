The Land Variational Ensemble Data Assimilation fRamework (LaVEnDAR)
====================================================================

The Land Variational Ensemble Data Assimilation fRamework (LaVEnDAR) implements the method of Four-Dimensional
Ensemble Variational data assimilation for land surface models. In this README we show an example of implementing
4DEnVar with the JULES land surface model to perform a twin experiment.

Project overview
----------------

The data assimilation routines and minimization are included in fourdenvar.py. For the example included in this project
you will require an installation of the JULES land surface model, more information on JULES can be found here
https://jules.jchmr.org/ model specific routines for running JULES are found in jules.py and run_jules.py. The data
assimilation experiment is setup in experiment_setup.py with variables set for output directories, model parameters to
be optimised, ensemble size and functions to extract observations for assimilation.

experiment_setup.py
*******************

Description of options in here

Tutorial
--------

In this tutorial we run a twin experiment to recover 7 JULES model parameters from a known model truth.

Running data assimilation
*************************

We set the following variables in experiment_setup.py

Plotting
********

We have included some commands to plot output from this tutorial found in plot.py

.. image:: output/plot/lai.png

.. image:: output/plot/gpp.png

.. image:: output/plot/canht.png

.. image:: output/plot/harvc.png

.. image:: output/plot/distributions.png