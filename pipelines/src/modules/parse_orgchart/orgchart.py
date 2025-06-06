#!/usr/bin/env python3
"""
Parse orgchart
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


import pandas as pd

from pathlib import Path
import json


class OrgChartParser:
    """..."""

    def __init__(self, file_path):
        """..."""
        self.file_path = Path(file_path)
        self.validate()
        self.primary_keys = ['Name', 'Role', 'ImmediateManager']
        self.data = None
    
    def validate(self):
        """..."""
        if not self.file_path.is_file():
            raise TypeError
        if not self.file_path.suffix in ['.csv', '.json']:
            raise TypeError
        return True

    def parse(self, office_fields=[], office_asc=True, manager_fields=[], manager_asc=True):
        """..."""
        data = None
        if self.file_path.suffix == '.csv':
            df = pd.read_csv(self.file_path)
        #elif self.file_path.suffix == '.json':
        #    data = json.load(self.file_path)
        if office_asc == True:
            office_asc.reverse()
        df['mod_title'] = df[office_fields].apply(lambda row: ' / '.join(row.values.astype(str)), axis=1)
        df['mod_title'] = df['mod_title'].str.replace(' / nan','')

        data = df[self.primary_keys]
        data['Title'] = df['mod_title']
        return data
        
