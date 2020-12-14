__author__ = ["Jake Nunemaker"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]


from copy import deepcopy
from itertools import product

import numpy as np
import pandas as pd
from benedict import benedict

from ORBIT import ProjectManager


class ParametricManager:
    """Class for configuring parametric ORBIT runs."""

    def __init__(self, base, params, results, weather=None, **kwargs):
        """
        Creates an instance of `ParametricRun`.

        Parameters
        ----------
        base : dict
            Base ORBIT configuration.
        params : dict
            Parameters and their values.
            Format: "subdict.param": [num1, num2, num3]
        results : dict
            List of results to save.
            Format: "name": lambda project: project.attr
        weather : DataFrame

        """

        self.base = benedict(base)
        self.params = params
        self.results = results
        self.weather = weather

    def run(self, **kwargs):
        """Run the configured parametric runs and save any results in
        `self.results`."""

        outputs = []
        for run in self.run_list:

            config = deepcopy(self.base)
            config.merge(run)

            project = ProjectManager(config, weather=self.weather, **kwargs)
            project.run_project()

            results = self.map_funcs(project, self.results)
            data = {**run, **results}
            outputs.append(data)

        return outputs

    @property
    def run_list(self):
        """Returns list of configured parametric runs."""

        runs = list(product(*self.params.values()))
        return [dict(zip(self.params.keys(), run)) for run in runs]

    @staticmethod
    def map_funcs(obj, funcs):
        """
        Map `obj` to list of `funcs`.

        Parameters
        ----------
        obj : ProjectManager
            Project instance to run through functions.
        funcs : list
            Functions used to pull results from obj.
        """

        results = {}
        for k, f in funcs.items():
            try:
                res = f(obj)

            except AttributeError:
                res = np.NaN

            results[k] = res

        return results
