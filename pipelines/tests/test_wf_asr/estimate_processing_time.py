#!/usr/bin/env python3
"""
Script to estimtae a model for processing time
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"



#config
from pathlib import Path

filename = 'report-batch_files'
config = {
    'WORKING_DIR': Path('./tmp/')
}


#imports
import numpy as np
import pandas as pd
from plotnine import (
    ggplot,
    aes,
    geom_point,
    theme_matplotlib,
    theme_set,
)
from sklearn.linear_model import QuantileRegressor
import pickle

import datetime
import json



class ProcessTimeQrModel():

    def __init__(self):
        self.config = {}
        self.config['WORKING_DIR'] = Path('./tests/tmp/')
        self.models_file = './tests/estimate/models.pkl'
        self.quantiles = [.5, .75, .95]
        self.solver = "highs"
        self.df = None
        self.models = None
    
    #workflow
    def estimate_model(self):
        self.df = self.find_and_load_recent_report()
        self.models = self.run_quantile_regression(self.df, ['time_asr'], ['file_size_mb'])
        return self.models
    
    def predict_processing_time(self, file_size_bytes):
        self.models = self.load_models()
        time = self.predict(file_size_bytes)
        return time

    def save_models(self):
        with open(self.models_file, 'wb') as f:
            pickle.dump(self.models, f)
        return True
    
    def load_models(self):
        with open(self.models_file, 'rb') as f:
            self.models = pickle.load(f)
        return self.models
    
    def run_plots(self):
        plt1 = (ggplot(self.df, aes("file_size_mb", "time_asr")) + geom_point())
        plt2 = (ggplot(self.df, aes("file_size_mb", "time_textmdl")) + geom_point() )
        plt1.save(filename = './estimate/plot-1.png', height=5, width=8, units='in', dpi=100)
        plt2.save(filename = './estimate/plot-1.png', height=5, width=8, units='in', dpi=100)
        return True

    #support
    def find_and_load_recent_report(self):
        """find most-recent report"""
        dirpath = self.config['WORKING_DIR'] / 'Reports'
        if not dirpath.is_dir():
            raise Exception(f'no directory: {dirpath}')
        mx = (None, 0)
        for file in dirpath.glob('**/*'):
            if file.is_file() and file.suffix=='.csv':
                filename_part = file.stem.split(filename)[1]
                dt_str = filename_part.split('_')[0] 
                tm_str = f"T{filename_part.split('_')[1].replace('-',':')}"
                dt = int( datetime.datetime.fromisoformat(dt_str+tm_str).timestamp() )
                if mx[1] < dt:
                    mx = (file, dt)
        df = pd.read_csv(mx[0])
        return df
    
    def run_quantile_regression(self, df, Xcols, Ycol):
        """Run quantile regression on multiple quantiles."""
        X = np.log10( df[Xcols].to_numpy(copy="deep") )
        y = np.log10( df[Ycol].to_numpy(copy="deep") )
        coefs = {}
        scores = {}
        models = {}
        for quantile in self.quantiles:
            #fit
            qr = QuantileRegressor(quantile=quantile, alpha=0, solver=self.solver)
            f = qr.fit(X, y)
            coef_dict = dict(zip(Xcols, f.coef_.tolist()))
            coefs[str(quantile)] = coef_dict
            models[str(quantile)] = f
            #score
            y_pred = f.predict(X)
            MAD = np.mean( np.abs(np.exp(y_pred) - np.exp(y)) )    #apply exp to get interpretable result
            scores[str(quantile)] = MAD.tolist()
        self.model = f
        results = {
            'coefs': coefs,
            'scores': scores,
            'models': models
            }
        return results
    
    def predict(self, file_size_bytes_lst):
        """Predict from bytes"""
        X = np.log10( np.array([file_size_bytes_lst]))
        preds = {}
        for quantile in self.quantiles:
            f = self.models['models'][str(quantile)]
            y_pred = f.predict(X)
            y_seconds = np.exp(y_pred)
            preds[str(quantile)] = y_seconds
        return preds
