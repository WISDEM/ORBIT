.. _coststoc:

Common Costs
=============

Establishing cost values for each installation process, component design, and project
parameter is essential to ORBIT's ability to calculate CapEx. Common costs and cost rates
were specified as default values in each module and thus spread out across multiple files.
Further, as modules were added or updated over time, these common costs were either updated
or were simply left as an older value. As of v1.2 (see :doc:`changelog`), all the common costs in the design modules
were centralized under ``common_cost.yaml``. That way, users can access a single file and
update any number of costs they wish to change.


Cost by Procurement Year
~~~~~~~~~~~~~~~~~~~~~~~~
Several users and industries partners have noted that some costs are out of date and
therefore may not fully represent a project. We applied method to adjust to account for
commodity, consumer, and labor indices as well as inflation to update the common cost of
certain components. The following figure is a snapshot from the spreadsheet `defaults/cost_by_procurement.png`,
and it shows the `Class`, `attribute_name`, `units`, and the cost value in 2024 USD. In
future releases, these costs will adjust based on the market indices so any user
can be sure that the common costs in their model is not outdated.

.. figure:: images/cost_by_procurement.png
   :align: center

   Cost by Procurement Year. Note that values are inflated from the procurement year USD to 2024 USD using CPI


The spreadsheet above is for tracking purposes, and the common cost values are added to the
files shown below. Costs for all the ``DesignPhases`` are stored in ``common_cost.yaml``; cable costs
are stored in each cable file in the ``library/cables`` folder; vessel costs are stored
in each vessel file in the ``library/vessels`` folder; and project costs are stored in ``manager.py``.

.. code-block::

   /path/to/orbit/ORBIT/core/defaults/common_cost.yaml
   /path/to/orbit/library/cables/*.yaml
   /path/to/orbit/library/vessels/*.yaml
   /path/to/orbit/ORBIT/manager.py


Questions regarding the methodology or organization of the common costs? Reach out to the :doc:`team`

.. note::

   This page is under construction and may receive an example in future releases.
