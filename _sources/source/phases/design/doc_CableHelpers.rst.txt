Cabling Design Helpers
======================

For details of the code implementation, please see the
:doc:`Cabling Helpers API <api_CableHelpers>`.

Overview
--------

This overview provides the :class:`Cable` class, :class:`Plant` class, and
:class:`CableSystem` parent class.

Cable
-----

The cable class calculates a provided cable's power rating for determining the
maximum number of turbines that can be supported by a string of cable.

Character Impedance (:math:`\Omega`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math:: Z_0 = \sqrt{\frac{R + 2 \pi f L}{G + j 2 \pi f C}}

| :math:`R=` :py:attr:`ac_resistance`
| :math:`j=` the imaginary unit
| :math:`f=` :py:attr:`line_frequency`
| :math:`L=` :py:attr:`inductance`
| :math:`G = \frac{1}{R} =` :py:attr:`conductance`
| :math:`C=` :py:attr:`capacitance`

Power Factor
~~~~~~~~~~~~

.. math::
   |P| &= \cos(\theta) \\
       &= \cos(\arctan(\frac{j Z_0}{Z_0}))

| :math:`\theta=` the phase angle
| :math:`jZ_0=` the imaginary portion of :py:attr:`character_impedance`
| :math:`Z_0=` the real portion of :py:attr:`character_impedance`

Cable Power (:math:`MW`)
~~~~~~~~~~~~~~~~~~~~~~~~

.. math::
   P = \sqrt{3} * V * I * |P|

| :math:`V=` :py:attr:`rated_voltage`
| :math:`I=` :py:attr:`current_capacity`
| :math:`|P|=` :py:attr:`power_factor`

Plant
-----

Calculates the wind farm specifications to be used for
:doc:`array cable design phase <doc_ArraySystemDesign>`. The "data class"
accepts either set distances between turbines and rows or calculates them
based off of the number of rotor diameters specified, for example:

.. code-block:: python

    # First see if there is a distance defined
    self.turbine_distance = config["plant"].get("turbine_distance", None)

    # If not, then multiply the rotor diameter by the turbine spacing,
    # an integer representation of the number of rotor diameters and covert
    # to kilometers
    if self.turbine_distance is None:
        self.turbine_distance = (
            rotor_diameter * config["plant"]["turbine_spacing"] / 1000.0
            )

    # Repeat the same process for row distance.
    self.row_distance = config["plant"].get("row_distance", None)
        if self.row_distance is None:
            self.row_distance = (
                rotor_diameter * config["plant"]["row_spacing"] / 1000.0
            )

where :py:attr:`config` is the configuration dictionary passed to the
:doc:`array cable design phase <api_ArraySystemDesign>`

The cable section length for the first turbine in each string is calculated as
the distance to the substation, ``substation_distance``.

CableSystem
-----------

:py:class:`CableSystem` acts as the parent class for both
:py:class:`ArrayDesignSystem` and :py:class:`ExportDesignSystem`. As such, it
is not intended to be invoked on its own, however it provides the shared
frameworks for both cabling system.

.. note::

   :py:class:`CableSystem` offers the cabling initialization and most of
   the output properties such as :py:attr:`cable_lengths_by_type`,
   :py:attr:`total_cable_lengths_by_type`, :py:attr:`cost_by_type`,
   :py:attr:`total_phase_cost`, :py:attr:`total_phase_time`,
   :py:attr:`detailed_output`, and most importantly :py:attr:`design_result`.
