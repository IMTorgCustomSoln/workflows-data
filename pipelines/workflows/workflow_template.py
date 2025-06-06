#!/usr/bin/env python3
"""
WorkflowTemplate


UseCase-1: use this as a template for building-out new workflows
* load .txt files
* classify and create intermediary .json records
* output as table .csv
* basic reporting
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Workflow import WorkflowNew
from src.Files import File, Files

from src.TaskImport import ImportFromLocalFileTask, ImportBatchDocsFromLocalFileTask 
from src.TaskTransform import CreateSingleFileRecordTask
from src.TaskModel import ApplyTextModelsTask
from src.TaskExport import ExportToVdiWorkspaceTask
"""TODO
from src.Report import (
    TaskStatusReport,
    MapBatchFilesReport,
    ProcessTimeAnalysisReport
)
"""
#TODO: from tests.estimate_processing_time import ProcessTimeQrModel

from src.io import load

from pathlib import Path



config = {
    'INPUT_DIR': Path('./tests/test_wf_template/data/'),
    'WORKING_DIR': Path('./tests/test_wf_template/tmp/'),
    'TRAINING_DATA_DIR': {
        'template': Path('./models_data/template1/'),
        'account': Path('./models_data/account/'),
        },
    'TASKS':[
        {
            'class': ImportFromLocalFileTask,
            'name': 'input',
            'extension_patterns': ['.md','.txt'],
         },
        {
            'class': CreateSingleFileRecordTask,
            'name': 'record',
            'extension_patterns': ['.pickle'],
         },
        {
            'class': ApplyTextModelsTask,
            'name': 'model',
            'extension_patterns': ['.pickle'],
         },
         {
             'class': ExportToVdiWorkspaceTask,
             'name': 'pre_export',
             'extension_patterns': ['.pickle'],
             'vdi_schema': ''
         }
    ]
}

class WorkflowTemplate(WorkflowNew):

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
        



workflow_template = WorkflowTemplate(config)