Offshore Substation Installation Methodology
============================================

For details of the code implementation, please see
:doc:`Offshore Substation Installation API <api_OffshoreSubstationInstall>`.

Overview
--------

The ``OffshoreSubstationInstallation`` module simulates the installation of
offshore substations and their associated substructures. ORBIT currently only
considers monopile substructures, though future release will extend this module
to include an option for jacket substructures. The installation of the
substructure and substation topside is completed with an installation vessel
while components are delivered to site using a feeder barge.

.. The :ref:`process-diagram` outlining the vessel logistics involved can be seen below.

Processes
---------

Port Operations
~~~~~~~~~~~~~~~

The feeder barge loads and fastens components on deck at port using the port
crane. The default times for fastening each component to deck are listed below.

+-----------+-------------------------+---------+
| Component |         Inputs          | Default |
+===========+=========================+=========+
| Monopile  | ``mono_fasten_time``    | 12h     |
+-----------+-------------------------+---------+
| Topside   | ``topside_fasten_time`` | 2h      |
+-----------+-------------------------+---------+

Currently, all vessels are only able to load multiples of complete sets of
components (monopile and topside).

Monopile Installation
~~~~~~~~~~~~~~~~~~~~~

Monopile substructures are installed using the installation processes outlined
in the ``MonopileInstallation`` module (process
:ref:`diagram <monopile_install_feeders>` with feeder barges).

Topside Installation
~~~~~~~~~~~~~~~~~~~~

Once the monopile is installed on-site, the topside can be released from deck
storage and attached to the substructure. The following processes outline the
code the processes the installation vessel takes to complete this task:

+-----------------+--------------------------+------------+
|     Action      |          Inputs          |  Default   |
+=================+==========================+============+
| Reequip Crane   | ``crane_reequip_time``   | 1h         |
+-----------------+--------------------------+------------+
| Release Topside | ``topside_release_time`` | 2h         |
+-----------------+--------------------------+------------+
| Lift Topside    | | ``wtiv.crane_rate``    | calculated |
|                 | | ``wave_height``        |            |
+-----------------+--------------------------+------------+
| Pump Grout      | ``grout_pump_time``      | 2h         |
+-----------------+--------------------------+------------+
| Cure Grout      | ``grout_cure_time``      | 24h        |
+-----------------+--------------------------+------------+
| Jack-down       | | ``depth, extension``   | calculated |
|                 | | ``speed_above_depth``  |            |
|                 | | ``speed_below_depth``  |            |
+-----------------+--------------------------+------------+

.. Process Diagram
.. ----------------

.. Offshore Substation Installation
.. ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. Coming soon!
