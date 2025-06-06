#!/usr/bin/env python3
"""
Test workflow class

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Workflow import WorkflowNew
from src.TaskImport import ImportFromLocalFileTask
from src.TaskExport import ExportRecordsToFileTask, ExportRecordsToReplTask

import tempfile
from pathlib import Path, PosixPath
import copy
import pytest


config_partial = {
    'INPUT_DIR': Path('./tests/test_tasks_workflow/data/'),
    #'WORKING_DIR': Path('./tests/test_tasks_workflow/tmp/'),
    'TRAINING_DATA_DIR': {
        'model_topic': None,
    },
    'TASKS':[]
}



def test_workflow_configuration():
    config = copy.deepcopy(config_partial)
    config['TASKS'] = [
        {
            'class': ImportFromLocalFileTask,
            'name': 'input',    #'input','output' are inferred, all other parameters should be added
            'extension_patterns': [],
         },
        {
            'class': ExportRecordsToFileTask,
            'name': 'export',
            'extension_patterns': [],
            'additional_params_if_required': 'arg',     #add params that a Task may need
            'output': None      #remove params using None
         }
    ]
    with tempfile.TemporaryDirectory() as t_dir:
        config['WORKING_DIR'] = Path(t_dir)
        new_workflow = WorkflowNew(config)
        assert 'new_workflow' in locals()
        assert 'additional_params_if_required' in new_workflow.params[1].keys()
        assert 'output' not in new_workflow.params[1].keys()
        assert list(config['WORKING_DIR'].iterdir()) == [config['WORKING_DIR']/'1_EXPORT']

def test_workflow_initialization():
    config = copy.deepcopy(config_partial)
    config['TASKS'] = [
        {
            'class': ImportFromLocalFileTask,
            'name': 'input',    #'input','output' are inferred, all other parameters should be added
            'extension_patterns': [],
         },
        {
            'class': ExportRecordsToFileTask,
            'name': 'export',
            'extension_patterns': [],
            #'additional_params_if_required': 'arg',     #add params that a Task may need
            #'output': None      #remove params using None
         }
    ]
    with tempfile.TemporaryDirectory() as t_dir:
        config['WORKING_DIR'] = Path(t_dir)
        new_workflow = WorkflowNew(config)
        check = new_workflow.prepare_workspace()
        assert check == True
        assert list(config['WORKING_DIR'].iterdir()) == [config['WORKING_DIR'] / '1_EXPORT', config['WORKING_DIR'] / '2_EXPORT']

def test_workflow_run_files():
    config = config_partial
    config['TASKS'] = [
        {
            'class': ImportFromLocalFileTask,
            'name': 'input',    #'input','output' are inferred, all other parameters should be added
            'extension_patterns': ['.txt','.md'],
         },
        {
            'class': ExportRecordsToFileTask,
            'name': 'export',
            'extension_patterns': ['.pickle'],
            #'additional_params_if_required': 'arg',     #add params that a Task may need
            #'output': None      #remove params using None
         }
    ]
    with tempfile.TemporaryDirectory() as t_dir:
        config['WORKING_DIR'] = Path(t_dir)
        new_workflow = WorkflowNew(config)
        check1 = new_workflow.prepare_workspace()
        assert check1 == True
        check2 = new_workflow.run()
        assert check2 == True
    
@pytest.mark.skip(reason="Test is currently under development")
def test_workflow_run_list():
    #TODO: empower interactive use with running workflow as lists
    config = copy.deepcopy(config_partial)
    config['TASKS'] = [
        {
            'class': ImportFromLocalFileTask,
            'name': 'input',    #'input','output' are inferred, all other parameters should be added
            'extension_patterns': ['.txt','.md'],
         },
        {
            'class': ExportRecordsToReplTask,
            'name': 'export',
            'extension_patterns': ['.pickle'],
            #'additional_params_if_required': 'arg',     #add params that a Task may need
            'output': None      #remove params using None
         }
    ]
    with tempfile.TemporaryDirectory() as t_dir:
        config['WORKING_DIR'] = Path(t_dir)
        new_workflow = WorkflowNew(config)
        assert True == True
        #check1 = new_workflow.prepare_workspace()
        #assert check1 == True
        #result = new_workflow.run()
        #assert result == [] #TODO:get output

def test_workflow_report():
    """TODO"""
    assert True == True