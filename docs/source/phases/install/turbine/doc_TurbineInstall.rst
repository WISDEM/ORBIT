Turbine Installation Methodology
================================

For details of the code implementation, please see
:doc:`Turbine Installation API <api_TurbineInstallation>`.

Overview
--------

The ``TurbineInstallation`` module simulates the installation of turbines at
site. For the purpose of this module, the turbine is discretized into five
different components: a tower, nacelle and three turbine blades. The module can
be configured such that a single wind turbine installation vessel (WTIV)
transports and installs all of the turbine components or it can be configured
to include feeder barges that transport the components to site.
:ref:`process-diagrams` detailing the vessel logistics for these two installation
can be seen below.

.. note::

   For both installation strategies the WTIV performs all of the on site
   operations with its onboard crane, either picking components from its own
   deck or a neighboring feeder barge.

Configuration
-------------

To configure ``TurbineInstallation`` to utilize feeder barges to transit the
turbine components from port, add the following configuration to the project
configuration.

.. code-block:: python

   config = {
       ...

       "feeder": "example_feeder",  # name of vessel configuration file without extension
       "num_feeders": 2,

       ...
   }

Processes
---------

Port Operations
~~~~~~~~~~~~~~~

Vessels load items and fasten them on their deck at port using the port crane.
Ports are configured with one crane by default, which limits multiple vessels
from accessing port resources at a time. This can be overridden by configuring
a port with additional cranes in a project configuration:

.. code-block:: python

   "port": {
       "num_cranes": 2  # Two vessels can access port resource simultaneously.
   }

The default times for fastening each component to deck are listed below.

+-----------+-------------------------+---------+
| Component |         Inputs          | Default |
+===========+=========================+=========+
| Tower     | ``tower_fasten_time``   | 4h      |
+-----------+-------------------------+---------+
| Nacelle   | ``nacelle_fasten_time`` | 4h      |
+-----------+-------------------------+---------+
| Blade     | ``blade_fasten_time``   | 1.5h    |
+-----------+-------------------------+---------+

Currently, all vessels are only able to load multiples of complete sets of
components (tower, nacelle and three blades).

Site Preperation
~~~~~~~~~~~~~~~~

Once the WTIV and a set of components are at site (either on the WTIV or a
feeder barge), the WTIV positions itself onsite and jacks up. The following
table outlines the inputs and default times for these tasks.

+-----------------+--------------------------+------------+
| Action          | Inputs                   | Default    |
+=================+==========================+============+
| Position Onsite | ``site_position_time``   | 2h         |
+-----------------+--------------------------+------------+
| Jack-up         | | ``depth, extension``   | calculated |
|                 | | ``speed_above_depth``  |            |
|                 | | ``speed_below_depth``  |            |
+-----------------+--------------------------+------------+

Turbine Installation
~~~~~~~~~~~~~~~~~~~~

After site preperation is complete, the WTIV begins installation by releasing a
turbine from its fastening (either on its own deck or neighboring feeder
barge). The tower is then lifted into place using the WTIV crane and attached
to the substructure. The nacelle is then released from its fastenings, lifted
into place and attached to the tower. The same process is repeated for each of
the three turbine blades. Inputs and process times are summarized in the
following table.

+------------------+--------------------------+------------+
| Action           | Inputs                   | Default    |
+==================+==========================+============+
| Reequip Crane    | ``crane_reequip_time``   | 1h         |
+------------------+--------------------------+------------+
| Release Tower    | ``tower_release_time``   | 3h         |
+------------------+--------------------------+------------+
| Lift Tower       | | ``turbine.hub_height`` | calculated |
|                  | | ``wtiv.crane_rate``    |            |
|                  | | ``wave_height``        |            |
+------------------+--------------------------+------------+
| Attach Tower     | ``tower_attach_time``    | 6h         |
+------------------+--------------------------+------------+
| Release Nacelle  | ``nacelle_release_time`` | 3h         |
+------------------+--------------------------+------------+
| Lift Nacelle     | | ``turbine.hub_height`` | calculated |
|                  | | ``wtiv.crane_rate``    |            |
|                  | | ``wave_height``        |            |
+------------------+--------------------------+------------+
| Attach Nacelle   | ``nacelle_attach_time``  | 6h         |
+------------------+--------------------------+------------+
| Release Blade    | ``blade_release_time``   | 1h         |
+------------------+--------------------------+------------+
| Lift Blade       | | ``turbine.hub_height`` | calculated |
|                  | | ``wtiv.crane_rate``    |            |
|                  | | ``wave_height``        |            |
+------------------+--------------------------+------------+
| Attach Blade     | ``blade_attach_time``    | 3.5h       |
+------------------+--------------------------+------------+

.. _process-diagrams:

Process Diagrams
----------------

Single WTIV Installation
~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: ../../../images/process_diagrams/turbine_single_wtiv.png

WTIV with Feeder Barges Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: ../../../images/process_diagrams/turbine_wtiv_with_feeders.png

Component Installation
~~~~~~~~~~~~~~~~~~~~~~

.. image:: ../../../images/process_diagrams/turbine_install.png
