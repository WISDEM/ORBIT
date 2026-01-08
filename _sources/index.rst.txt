.. sidebar:: Documentation

   :ref:`Introduction <intro>`
      A quick introduction to the project.

   :ref: `Installation and Contribution <installation>`
      How to install and contribute to ORBIT.

   :ref:`Tutorial <tutorial>`
      Basic tutorial for working with ORBIT.

   :ref:`Examples <examples>`
      Advanced examples and real world validation cases.

   :ref:`API Reference <api>`
      Detailed description of ORBIT's API.

   :ref:`Methodology <methods>`
      References and descriptions of the underlying engineering models.

   :ref:`Publications <publications>`
      Publications related to ORBIT.

   :ref:`Changelog <changelog>`
      ORBIT Changelog

   :ref:`Team <team>`
      List of authors and contributors.

ORBIT
=====

Overview
--------

The Offshore Renewables Balance of system and Installation Tool (ORBIT) is a
model developed by the National Renewable Energy Lab (NREL) to study
the cost and times associated with Offshore Wind Balance of System (BOS)
processes.

ORBIT includes many different modules that can be used to model phases within
the BOS process, split into :ref:`design <design_phases>` and
:ref:`installation <install>`. It is highly flexible and allows the user to
define which phases are needed to model their project or scenario using
:ref:`ProjectManager <manager>`.

ORBIT is written in Python 3.10 and utilizes
`SimPy <https://simpy.readthedocs.io/en/latest/>`_'s discrete event simulation
framework to model individual processes during the installation phases,
allowing for the effects of weather delays and vessel interactions to be
studied.

License
-------

Apache 2.0. Please see the
`repository <https://github.com/WISDEM/ORBIT/blob/master/LICENSE>`_ for
license information.
