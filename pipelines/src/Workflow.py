#!/usr/bin/env python3
"""
Workflow class
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Files import File, Files

"""TODO
from src.Report import (
    TaskStatusReport,
    MapBatchFilesReport,
    ProcessTimeAnalysisReport
)
"""
from src.models import prepare_models
from src.io import load
#TODO: from tests.estimate_processing_time import ProcessTimeQrModel

from config._constants import (
    logging_dir,
    logger
)

from pathlib import Path
import time
import sys




class Workflow:
    """..."""

    def __init__(self):
        pass
    
    def prepare(self):
        pass

    def run(self):
        pass

    def report(self):
        pass




#example: Workflow config
"""
config = {
    'INPUT_DIR': None,
    'WORKING_DIR': None,
    'TRAINING_DATA_DIR': {
        'model_topic': None,
    },
    'TASKS':[
        {
            'class': ImportFromLocalFileTask,
            'name': 'input',    #'input','output' are inferred, all other parameters should be added
            'extension_patterns': [],
         },
        {
            'class': 'ClassTask',
            'name': 'task2',
            'extension_patterns': [],
            'additional_params_if_required': 'arg',     #add params that a Task may need
            'output': None      #remove params using None
         }
    ]
}
"""

#supporing 
import inspect

def get_init_params(cls):
    """Introspection to get class parameters."""
    init_signature = inspect.signature(cls.__init__)
    return init_signature.parameters

def check_param_for_inclusion(current_task_attrs, key):
    """Check if the param should be included for provisioning Task."""
    if key in current_task_attrs.keys():
        if current_task_attrs[key] == None:
            return False
    return True



class WorkflowNew:
    """Workflow Parent Class"""

    def __init__(self, config):
        config_data = self._perform_config_checks(config)
        self.config = config_data
        self.params = self._configure_tasks()
        
    def _perform_config_checks(self, config):
        """Check that config data is correct."""
        #user input
        required_keys = [
            'INPUT_DIR',
            'WORKING_DIR',
            'TRAINING_DATA_DIR',
            'TASKS'
        ]
        check_config = all( [key in required_keys for key in config.keys()] )
        if not check_config:
            raise Exception(f"There was an error")
        config['WORKING_DIR'].mkdir(parents=True, exist_ok=True)
        #system input
        if 'START_TIME' not in config.keys(): config['START_TIME'] = None 
        if 'LOGGER' not in config.keys(): config['LOGGER'] = logger  
        if 'BATCH_RECORD_COUNT' not in config.keys(): config['BATCH_RECORD_COUNT'] = 50
        if 'WORKSPACE_SCHEMA' not in config.keys(): config['WORKSPACE_SCHEMA'] = None
        checked_config_data = config
        return checked_config_data
    
    def _configure_tasks(self):
        """Configure the Tasks with correct Files and other parameters."""
        preformatted_tasks = {
            '0': {'directory': self.config['INPUT_DIR']}
        }
        expected_keys = [
            'class',
            'name',
            'extension_patterns'
        ]
        params = []
        for idx, task_attrs in enumerate(self.config['TASKS']):
            #build files in
            files_in_dir = None
            if str(idx) in preformatted_tasks.keys():
                files_in_dir = preformatted_tasks[str(idx)]['directory']
            else:
                files_in_dir = self.config['WORKING_DIR'] /  f"{idx}_{task_attrs['name'].upper()}"
            if check_param_for_inclusion(task_attrs, 'input'):
                files_in = Files(
                    name=task_attrs['name'],
                    directory_or_list=files_in_dir,
                    extension_patterns=task_attrs['extension_patterns']
                )
            #build files out
            files_out_name = None
            files_out_dir = []
            files_out_extensions = None
            if idx+1 < len(self.config['TASKS']):
                next_task_attrs = self.config['TASKS'][idx+1]
                files_out_name = next_task_attrs['name']
                files_out_dir = self.config['WORKING_DIR'] / f"{idx+1}_{next_task_attrs['name'].upper()}"
                files_out_extensions = next_task_attrs['extension_patterns']
            else:
                files_out_name = 'export'
                files_out_dir = self.config['WORKING_DIR'] / f"{idx+1}_{files_out_name.upper()}"
                files_out_extensions = ['.pickle']
            if check_param_for_inclusion(task_attrs, 'output'):
                files_out = Files(
                    name=files_out_name,
                    directory_or_list=files_out_dir,
                    extension_patterns=files_out_extensions
                )
            #build task params
            preformatted_params = {
                'config': self.config,
                'input': files_in,
                'output': files_out
                }
            required_params = get_init_params(task_attrs['class'])
            required_params_keys = [k for k in required_params.keys()]
            provided_params = {k:v for k,v in preformatted_params.items() if k in required_params_keys}
            new_params = {k:v for k,v in task_attrs.items() if k not in expected_keys}
            provided_params.update(new_params)
            complete_params = {k:v for k,v in provided_params.items() if check_param_for_inclusion(task_attrs, k)}
            params.append(complete_params)
        return params
    
    def _initialize_tasks(self):
        """Initialize the Tasks with configured params and return Files with Tasks."""
        files = []
        tasks = []
        try:
            for idx, task_attrs in enumerate(self.config['TASKS']):
                new_task = task_attrs['class'](**self.params[idx])
                files.append(self.params[idx]['input'])
                tasks.append(new_task)
        except Exception as e:
            print(e)
            print(f'Task: {task_attrs}')
            sys.exit()
        result = {
            'files': files,
            'tasks': tasks,
        }
        return result

    def prepare_workspace(self):
        """Prepare workspace with Tasks and file paths"""
        init_tasks = self._initialize_tasks()
        self.files = init_tasks['files']
        self.tasks = init_tasks['tasks']
        return True
    
    def prepare_models(self):
        """Prepare by loading train,test data and refine models"""
        self.config['LOGGER'].info("Begin prepare_models")
        checks = []
        for model_topic in self.config['TRAINING_DATA_DIR']:
            check_prepare_keywords = prepare_models.validate_key_terms(self.config, model_topic)
            if not check_prepare_keywords: 
                self.config['LOGGER'].info(f"keywords failed to prepare for model_topic: {model_topic}")
                return False
            check_prepare_model = prepare_models.finetune_classification_model(self.config, model_topic)
            if not check_prepare_model: 
                self.config['LOGGER'].info(f"models failed to prepare for model_topic: {model_topic}")
                return False
        self.config['LOGGER'].info("End prepare_models")
        return True

    def run(self):
        """Run the workflow of tasks"""
        #TODO: add input / output with list for interactive work
        
        #self.config_tasks()
        self.config['LOGGER'].info('begin process')
        self.config['START_TIME'] = time.time()
        for task in self.tasks:
            result = task.run()
        self.config['LOGGER'].info(f"end process, execution took: {round(time.time() - self.config['START_TIME'], 3)}sec")
        return result


    def report(self):
        '''Run reports interactively or to export file.'''
        pass

    '''
    def report_task_status(self):
        """
        TODO:
        * typical size of files
        * outlier files that are very large
        * place code in a separate file
        
        TaskStatusReport(
            files=self.files,
            config=self.config
        ).run()"""
        return True
    
    def report_map_batch_to_files(self):
        """Create .csv of files in each batch output
        
        MapBatchFilesReport(
            files=self.files,
            config=self.config
        ).run()"""
        return True
    
    def report_process_time_analysis(self):
        """Analyze processing times of completed files
        
        MapBatchFilesReport(
            files=self.files,
            config=self.config
        ).run()
        ProcessTimeAnalysisReport(
            files=self.files,
            config=self.config
        ).run()"""
        return True

        '''