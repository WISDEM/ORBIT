Scour Protection Installation Methodology
=========================================

For details of the code implementation, please see
:doc:`Scour Protection Installation API <api_ScourProtectionInstall>`.

Overview
--------

The ``ScourProtectionInstallation`` modules simulates the installation of scour
protection around the base of a offshore substructure. In many offshore site
conditions, scour protection is a necessary step to reduce the effects of
hydrodynamic scour development around the substructure. ORBIT models the
installation of a rock layer installed at a diameter surrounding the
substructure base. This process is not typically a significant cost driver for
the project, but the installation time and associated costs are significant
enough that they should not be ignored when computing BOS costs.

Configuration
-------------

This module is simple to configure, as the main parameter considered is the
``tons_per_substructure`` to install. Currently ORBIT models the simplest
installation method, involving "Side Stone Installation Vessels" that dump
loads of rocks next to the substructure without much ability to ensure that
their payload is distributed evenly. A future version of ORBIT may expand this
module to include more modern installation approaches using a "Fall Pipe
Vessel" that allow for an even distrubution of scour protection material.

Example
~~~~~~~

.. code-block::

   {
       'scour_protection_install_vessel': 'example_vessel'
       'site': {'distance': 20},

       ...

       'scour_protection': {
           'tons_per_substructure': 1200
           }
       }
   }

Processes
---------

The scour protection installation vessel loads rock at port, transits to site
and installs the required amount at each substructure until empty. At this
point, it will return to port to load additional rock and repeat the above
steps until all substructures have had scour protection installed. The process
times for this operation are outlined below.

+-----------------+--------------------------------------+------------+
|     Process     |                Inputs                |  Default   |
+=================+======================================+============+
| Load Rocks      | ``load_rocks_time``                  | 4h         |
+-----------------+--------------------------------------+------------+
| Transit to Site | ``site_distance``, ``transit_speed`` | calculated |
+-----------------+--------------------------------------+------------+
| Drop Rocks      | ``drop_rocks_time``                  | 10h        |
+-----------------+--------------------------------------+------------+

.. Process Diagrams
.. ----------------

.. Coming soon!
