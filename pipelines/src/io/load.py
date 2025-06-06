#!/usr/bin/env python3
"""
Import functions

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Files import File

import copy
import datetime


def get_schema_from_workspace(filepath):
    """Get schema from example app workspace output"""

    #get schema
    filepath_workspace_gzip = File(filepath, 'workspace')             #Path('./tests/input/VDI_ApplicationStateData_v0.2.1.gz') 
    workspace_json = filepath_workspace_gzip.load_file(return_content=True)

    #create empty schema
    workspace_schema = copy.deepcopy(workspace_json)
    sample_item = workspace_schema['documentsIndex']['documents'][0]
    for k,v in sample_item.items():
        sample_item[k] = None
    documents_schema = copy.deepcopy(sample_item)
    workspace_schema['documentsIndex']['indices']['lunrIndex'] = {}
    workspace_schema['documentsIndex']['documents'] = documents_schema

    return workspace_schema