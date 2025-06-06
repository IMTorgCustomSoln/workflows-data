#!/usr/bin/env python3
"""
WorkflowASR
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Workflow import WorkflowNew
from src.Files import File, Files
from src.TaskImport import ImportFromLocalFileTask, ImportBatchDocsFromLocalFileTask 
from src.TaskTransform import (
    UnzipTask,
    FlattenFileStructureTask,
    CreateMultiFileRecordTask
)
from src.TaskModel import (
    AsrTask,
    ApplyTextModelsTask,
    #TextClassificationTask,
    #ExportAsrToVdiWorkspaceTask
)
from src.TaskExport import ExportToVdiWorkspaceTask
from src.Report import (
    TaskStatusReport,
    MapBatchFilesReport,
    ProcessTimeAnalysisReport
)
from src.models import prepare_models
from src.io import load
from tests.test_wf_asr.estimate_processing_time import ProcessTimeQrModel

from pathlib import Path



'''
        {
            'class': ImportFromLocalFileTask,
            'name': 'input_audio',
            'extension_patterns': ['.wav','.mp3','.mp4'],
         },
         '''


config = {
    'INPUT_DIR': Path('./tests/test_wf_asr/data/'),
    'WORKING_DIR': Path('./tests/test_wf_asr/tmp/'),
    'TRAINING_DATA_DIR': {
        'template2': Path('./models_data/template2/'),
        },
    'TASKS':[
        {
            'class': UnzipTask,
            'name': 'unzipped',
            'extension_patterns': ['.zip'],
        },
        {
             'class': FlattenFileStructureTask,
             'name': 'flatten',
             'extension_patterns': ['.zip'],
         },
        {
             'class': AsrTask,
             'name': 'asr',
             'extension_patterns': ['.mp3','.wav'],
         },
        {
            'class': CreateMultiFileRecordTask,
            'name': 'record',
            'extension_patterns': ['.json'],
         },
        {
            'class': ApplyTextModelsTask,
            'name': 'model',
            'extension_patterns': ['.pickle'],
         },
         {
             #'class': ExportAsrToVdiWorkspaceTask,
             'class': ExportToVdiWorkspaceTask,
             'name': 'pre_export',
             'extension_patterns': ['.pickle'],
             'vdi_schema': ''
         }
    ]
}

class WorkflowASR(WorkflowNew):

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
        



workflow_asr = WorkflowASR(config)




'''
    def report_task_status(self):
        """
        TODO:
        * typical size of files
        * outlier files that are very large
        * place code in a separate file
        """
        TaskStatusReport(
            files=self.files,
            config=self.config
        ).run()
        return True
    
    def report_map_batch_to_files(self):
        """Create .csv of files in each batch output
        """
        MapBatchFilesReport(
            files=self.files,
            config=self.config
        ).run()
        return True
    
    def report_process_time_analysis(self):
        """Analyze processing times of completed files
        """
        MapBatchFilesReport(
            files=self.files,
            config=self.config
        ).run()
        ProcessTimeAnalysisReport(
            files=self.files,
            config=self.config
        ).run()
        return True'
    

        


workflow_asr = WorkflowASR()
'''