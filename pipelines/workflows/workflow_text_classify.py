#!/usr/bin/env python3
"""
WorkflowTemplate


UseCase: use this interactively with notebook when fewer records are applied
* load .txt files
* classify and create intermediary .json records
* ~~output as table .csv~~
* ~~basic reporting~~
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Workflow import WorkflowNew
from src.TaskImport import ImportFromLocalFileTask
from src.TaskTransform import CreateSingleFileRecordTask
from src.TaskModel import ApplyTextModelsTask
from src.TaskExport import ExportRecordsToFileTask   #ExportRecordsToReplTask

from pathlib import Path


config = {
    'INPUT_DIR': Path('./tests/test_wf_text_classify/data/'),
    'WORKING_DIR': Path('./tests/test_wf_text_classify/tmp/'),
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
         }
    ]
}

"""TODO:individual files, such as .pdfs, may be useful.
        {
            'class': ExportRecordsToFileTask,
            'name': 'export',
            'extension_patterns': ['.pickle'],
         }
         """

class WorkflowTextClassify(WorkflowNew):
    pass
workflow_text_classify = WorkflowTextClassify(config)