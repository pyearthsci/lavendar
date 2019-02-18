The Land Variational Ensemble Data Assimilation fRamework (LaVEnDAR)
====================================================================

The Land Variational Ensemble Data Assimilation fRamework (LaVEnDAR) implements the method of Four-Dimensional
Ensemble Variational data assimilation for land surface models. In this README we show an example of implementing
4DEnVar with the JULES land surface model to perform a twin experiment.

Project overview
----------------

The data assimilation routines and minimization are included in :code:`fourdenvar.py`. For the example included in this
project you will require an installation of the JULES land surface model (more information on JULES can be found here:
https://jules.jchmr.org/ ). Model specific routines for running JULES are found in :code:`jules.py` and
:code:`run_jules.py`. The data assimilation experiment is setup in :code:`experiment_setup.py` with variables set for
output directories, model parameters, ensemble size and functions to extract observations for assimilation. The module
:code:`run_experiment.py` runs the ensemble of model runs and exectures the experiment as defined by
:code:`experiment_setup.py`. Some experiment specific plotting routines are also included in :code:`plot.py`.

Data for running the JULES model can be found in the :code:`data/` directory, including driving data for the Mead maize
FLUXNET site, a JULES dump file and a JULES land fraction file. There are 2 JULES namelist file directories
:code:`example_nml` and :code:`williams_nml`. :code:`example_nml` is used as the directory for JULES runs in the example
experiment included in the tutorial. :code:`williams_nml` was used to produce a "model truth" JULES run used for
sampling psuedo observations in the tutorial example.

experiment_setup.py
^^^^^^^^^^^^^^^^^^^

Description of options in here

Tutorial
--------

In this tutorial we run a twin experiment to recover 7 JULES model parameters from a known model truth.

Running data assimilation
^^^^^^^^^^^^^^^^^^^^^^^^^

We set the following variables in :code:`experiment_setup.py`

Plotting
^^^^^^^^

We have included some commands to plot output from this tutorial found in plot.py

.. image:: output/plot/lai.png

.. image:: output/plot/gpp.png

.. image:: output/plot/canht.png

.. image:: output/plot/harvc.png

.. image:: output/plot/distributions.png

Support
-------

In the case of any issues please contact: e.pinnington@reading.ac.uk