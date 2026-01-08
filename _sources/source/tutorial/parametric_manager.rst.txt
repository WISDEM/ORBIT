.. _parametric:

ParametricManager
=================

``ParametricManager`` is used to run simple parametric studies in ORBIT
by defining a subset of the inputs as a list. A basic parametric study where
the site depth and distance to shore is varied is shown below.

.. code-block:: python

   from ORBIT import ParametricManager

   # Any inputs that aren't parameterized are passed in using a
   # typical ORBIT configuration
   base = {
       "turbine": "15MW_generic",
       "wtiv": "example_wtiv",

       ...
   }

   # Parameterized inputs are passed in as a list. The product of all
   # scenarios will be ran.
   params = {
      "site.depth": [10, 30, 50],
      "site.distance": [20, 40, 60],
   }

   # Desired results are saved using lambda functions. These functions
   # can be used to save any output normally available in ProjectManager.
   # In this example, the installation and system CapEx results are saved.
   results = {
      "Installation": lambda project: project.installation_capex,
      "System": lambda project: project.system_capex
   }

   # A weather profile to use in all scenarios can also be passed in.
   scenarios = ParametricManager(base, params, results, weather=weather)
   scenarios.run()

The results are saved as a pandas DataFrame at ``scenarios.results`` where each
row represents a different scenario run and includes the parameterized inputs
and any results the user configured.

.. note::

   The parameterized inputs were passed in using "dot-notation". In this
   notation, each "." tells ParametricManager to go a level deeper in the ORBIT
   configuration. For example, "site.depth" is the "site" subdict, and the
   "depth" input. This can used at any depth within an ORBIT configuration.

Plotting
--------

The outputs can be easily visualized using
`matplotlib <https://matplotlib.org/>`_ or
`seaborn <https://seaborn.pydata.org/>`_.

.. code-block:: python

   import matplotlib.pyplot as plt
   import seaborn as sns

   # Scatter Plot
   plt.scatter(scenarios.results["site.depth"], scenarios.results["Installation"])

   # Box Plot
   sns.boxplot(data=scenarios.results, x='site.depth', y='System')

   # Box Plot with Hue
   sns.boxplot(data=scenarios.results, x='site.depth', y='System', hue='site.distance')

Parametric Weather
------------------

Coming soon!
