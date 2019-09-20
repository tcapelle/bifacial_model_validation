import argparse, sys
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# import function to run simulations in parallel
import pvlib
from pvfactors.geometry import OrderedPVArray
from pvfactors.run import run_parallel_engine
from pvfactors.engine import PVEngine
from utils import ifnone

def _get_cut(cut):
    cut_array = np.array([cut[i]['back'] for i in range(len(cut))])
    return cut_array.argmax(), cut_array.max()

def pvfactors_engine_run(data, pvarray_parameters, parallel=0, mode='full'):
    """My wrapper function to launch the pvfactors engine in parallel. It is mostly for Windows use.
    In Linux you can directly call run_parallel_engine. It uses MyReportBuilder to generate the output.
    
    Args:
        data (pandas DataFrame): The data to fit the model.
        pvarray_parameters (dict): The pvfactors dict describing the simulation.
        parallel (int, optional): Number of threads to launch. Defaults to 0 (just calls PVEngine.run_all_timesteps)
    
    Returns:
        pandas DataFrame: The results of the simulation, as desired in MyReportBuilder.
    """
    n, row = _get_cut(pvarray_parameters['cut'])
    if parallel>0:
        report = run_parallel_engine(Report(n, row), pvarray_parameters, data.index, 
                                data.dni, data.dhi, 
                                data.zenith, data.azimuth, 
                                data.surface_tilt, data.surface_azimuth, 
                                data.albedo, n_processes=parallel)
    else:
        rb = Report(n, row)
        pvarray = OrderedPVArray.init_from_dict(pvarray_parameters)
        engine = PVEngine(pvarray)
        engine.fit(data.index, 
                    data.dni, 
                    data.dhi, 
                    data.zenith, 
                    data.azimuth, 
                    data.surface_tilt, 
                    data.surface_azimuth,
                    data.albedo,
                    data.ghi)
        if mode == 'full': report = engine.run_full_mode(rb.build)
        else: report = engine.run_fast_mode(rb.build, pvrow_index=0)
    df_report = pd.DataFrame(report, index=data.index).fillna(0)
    return df_report


class Report(object):
    """A class is required to build reports when running calculations with
    multiprocessing because of python constraints"""
    def __init__(self, row=0, n=7):
        self.n = n
        self.row = row

    def build(self, report, pvarray):
        # Initialize the report as a dictionary
        if report is None:
            list_keys = ['qinc_front', 'qinc_back_mean']+[ f'qinc_back_{i}'for i in range(self.n)]
            report = {key: [] for key in list_keys}
            
        def _get_irradiance_all(pvrow, param='qinc'):
            return np.array([pvrow.back.all_surfaces[i].params[param] for i in range(self.n)])

        if pvarray is not None:
            pvrow = pvarray.pvrows[self.row]  # use center pvrow
            report['qinc_front'].append(
                pvrow.front.get_param_weighted('qinc'))
            report['qinc_back_mean'].append(
                pvrow.back.get_param_weighted('qinc'))
            back_irrad = _get_irradiance_all(pvrow)
            for i in range(self.n):
                report[f'qinc_back_{i}'].append(back_irrad[i])    
        else:
            # No calculation was performed, because sun was down
            report['qinc_front'].append(np.nan)
            report['qinc_back_mean'].append(np.nan)
            for i in range(self.n):
                report[f'qinc_back_{i}'].append(np.nan)    
        return report

    @staticmethod
    def merge(reports):
        """Works for dictionary reports"""
        report = reports[0]
        # Merge only if more than 1 report
        if len(reports) > 1:
            keys_report = list(reports[0].keys())
            for other_report in reports[1:]:
                for key in keys_report:
                    report[key] += other_report[key]
        return report