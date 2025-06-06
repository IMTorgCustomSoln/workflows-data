#!/usr/bin/env python3
"""
WorkflowExportWorkspace


UseCase-1: use this for exporting email records to a VDI Workspace file
* load record files
* xform into presentation document
* export to workspace file
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Workflow import WorkflowNew
from src.Files import File, Files

from src.TaskImport import ImportFromLocalFileCustomFormatTask  
from src.TaskTransform import CreateSingleFileRecordTask
from src.TaskExport import ExportToVdiWorkspaceTask, ExportBatchToVdiWorkspaceTask

from src.io import load
#TODO: from tests.estimate_processing_time import ProcessTimeQrModel

from config._constants import (
    logging_dir,
    logger
)

from pathlib import Path
import time
import sys



config = {
    'INPUT_DIR': Path('./tests/test_wf_export_workspace/data/'),
    'WORKING_DIR': Path('./tests/test_wf_export_workspace/tmp/'),
    'TRAINING_DATA_DIR': {},
    'TASKS':[
        {
            'class': ImportFromLocalFileCustomFormatTask,
            'name': 'input',
            'extension_patterns': ['.json'],
         },
        {
            'class': CreateSingleFileRecordTask,
            'name': 'presentation',
            'extension_patterns': ['.pickle'],
         },
         {
             'class': ExportToVdiWorkspaceTask,
             'name': 'xform',
             'extension_patterns': ['.pickle'],
             'vdi_schema': ''
         }
    ]
}

class WorkflowExportWorkspace(WorkflowNew):

    def _prepare_scheme(self):
        filepath = Path('./tests/data/VDI_ApplicationStateData_v0.2.1.gz')
        if filepath.is_file():
            workspace_schema = load.get_schema_from_workspace(filepath)
        self.config['WORKSPACE_SCHEMA'] = workspace_schema
        schema = self.config['WORKING_DIR'] / 'workspace_schema_v0.2.1.json'
        schema_file = File(schema, 'json')
        schema_file.load_file(return_content=False)
        schema_file.content = workspace_schema
        check1 = schema_file.export_to_file()
        return check1
    
    def prepare_workspace(self):
        check1 = self._prepare_scheme()
        check2 = super().prepare_workspace()
        return all([check1, check2])
        



workflow_export_workspace = WorkflowExportWorkspace(config)