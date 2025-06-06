#!/usr/bin/env python3
"""
WorkflowEcomms


UseCase-1: create similar document representations from multiple ecommunication channels
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Workflow import Workflow
from src.Files import Files
from src.modules.parse_ediscovery.loadfile import (
    collect_workspace_files,
    copy_dat_file_with_fixed_format
)
from src.modules.parse_orgchart.orgchart import OrgChartParser
from src.TaskImport import ImportValidateCombineEcommsTask, ImportCombinedDatsEcommsTask
from src.TaskTransform import CreateSingleFileRecordTask
from src.TaskModel import ApplyTextModelsTask, ApplyTextModelsTask
from src.TaskExport import ExportToVdiWorkspaceTask
from src.models import prepare_models
from src.io import load
#from tests.estimate_processing_time import ProcessTimeQrModel

from config._constants import logger

from pathlib import Path
import json
import time
import sys


class WorkflowEcomms(Workflow):
    """..."""

    def __init__(self):
        CONFIG = {}
        try:
            #user input
            CONFIG['INPUT_DIR'] = Path('./tests/test_wf_ecomms/data_ediscovery/extended_layout')
            CONFIG['TRAINING_DATA_DIR'] = Path('./src/data/account/') 
            CONFIG['WORKING_DIR'] = Path('./tests/test_wf_ecomms/tmp/')
            CONFIG['OUTPUT_DIRS'] = [Path('./tests/test_wf_ecomms/tmp/OUTPUT')]

            #system input
            CONFIG['START_TIME'] = None
            CONFIG['LOGGER'] = logger
            CONFIG['BATCH_COUNT'] = 50
            CONFIG['WORKSPACE_SCHEMA'] = None
            #CONFIG['REGEX_INPUT_FILES_NAMES'] = '_Calls_'
            self.config = CONFIG

            #working dirs
            CONFIG['WORKING_DIR'].mkdir(parents=True, exist_ok=True)
            DIR_VALIDATED = CONFIG['WORKING_DIR'] / '1_VALIDATED'
            DIR_XFORM = CONFIG['WORKING_DIR'] / '2_XFORM'
            DIR_MODELS_APPLIED = CONFIG['WORKING_DIR'] / '3_MODELS_APPLIED'
            DIR_OUTPUT = CONFIG['WORKING_DIR'] / '3_OUTPUT'
            #DIR_ARCHIVE = CONFIG['WORKING_DIR'] / 'ARCHIVE'
            #CONFIG['DIR_ARCHIVE'] = DIR_ARCHIVE

            #files
            """
            input_files = Files(
                name='input',
                directory=CONFIG['INPUT_DIR'],
                extension_patterns=['.mdat','.txt','.eml','.msg']
                )
            """
            input_files = Files(
                name='input',
                directory_or_list=CONFIG['INPUT_DIR'],
                extension_patterns=['.pickle']
                )
            validated_files = Files(
                name='validated',
                directory_or_list=DIR_VALIDATED,
                extension_patterns=['.pickle']
                )
            xform_files = Files(
                name='xform',
                directory_or_list=DIR_XFORM,
                extension_patterns=['.pickle']
                )
            models_applied_files = Files(
                name='models_applied',
                directory_or_list=DIR_MODELS_APPLIED,
                extension_patterns=['.pickle']
                )
            
            output_files = Files(
                name='output',
                directory_or_list=DIR_OUTPUT,
                extension_patterns=['.gz']
                )
            self.files = {
                'input_files': input_files,
                'validated_files': validated_files,
                'xform_files': xform_files,
                'models_applied_files': models_applied_files,
                'output_files': output_files
            }
            #tasks
            """
            validate_task = ImportValidateCombineEcommsTask(
                config=CONFIG,
                input=input_files,
                output=validated_files
            )
            """
            validate_task = ImportCombinedDatsEcommsTask(
                config=CONFIG,
                input=input_files,
                output=validated_files
            )
            xform_task = CreateSingleFileRecordTask(
                config=CONFIG,
                input=validated_files,
                output=xform_files
            )
            apply_models_task = ApplyTextModelsTask(
                config=CONFIG,
                input=xform_files,
                output=models_applied_files
            )
            output_task = ExportToVdiWorkspaceTask(
                config=CONFIG,
                input=models_applied_files,
                output=output_files,
                vdi_schema=None
            )
            tasks = [
                validate_task,
                xform_task,
                apply_models_task,
                output_task,
                #output_files_task
                ]
            self.tasks = tasks
        except Exception as e:
            print(e)
            sys.exit()
        

    def prepare_models(self):
        """Prepare by loading train,test data and refine models"""
        self.config['LOGGER'].info("Begin prepare_models")
        check_prepare_keywords = prepare_models.validate_key_terms(self.config)
        check_prepare_model = True    #prepare_models.finetune_classification_model(self.config)
        if not (check_prepare_keywords | check_prepare_model): 
            self.config['LOGGER'].info(f"keywords or models failed to prepare")
            return False
        self.config['LOGGER'].info("End prepare_models")
        return True

    def prepare_workspace(self):
        """Prepare workspace, including: create .mdat files, create output schema, 
        and validate file paths.
        
        Note:
        The .mdat files are foundational to the process primarily because they ensure:
        i) consistent columns - mapped using `rename_fields`
        ii) TODO: validated path links - `'Extracted Text':'textLink', 'FILE_PATH':'nativeLink'`
        The .mdat files may need to be created manually, but should fit the directory
        structure to work with the `run()` method. 
        """
        #prepare schema
        filepath = Path('./tests/data/VDI_ApplicationStateData_v0.2.1.gz')
        if filepath.is_file():
            workspace_schema = load.get_schema_from_workspace(filepath)
        self.config['WORKSPACE_SCHEMA'] = workspace_schema
        schema = self.config['WORKING_DIR'] / 'workspace_schema_v0.2.1.json'
        with open(schema, 'w') as f:
            json.dump(workspace_schema, f)
        #prepare modified .dat file, .mdat, with consistent columns
        if not self.config['INPUT_DIR'].is_dir():
            raise Exception
        rename_fields = {
            'Control Number':'documentId', 'Custodian':'custodian',
            'Group Identifier': 'groupId', 'Parent Document ID': 'parentDocumentId',
            'number of attachments': 'numberOfAttachments',
            'Document Extension': 'documentExtension', 'Filename': 'fileName', 'Filesize':'fileSize',
            'Email Subject': 'emailSubject', 'Subject':'subject', 'Email From': 'from', 'Email To': 'to', 'Email CC': 'cc',
            'Extracted Text':'textLink', 'FILE_PATH':'nativeLink'
            }
        file_collection = collect_workspace_files(self.config['INPUT_DIR'])
        if False:
            for volume_key in file_collection.keys():
                if not file_collection[volume_key]['mdat']:
                    new_file = file_collection[volume_key]['dat'].parent / 'new_file.mdat'
                    SEP = '\x14'
                    check = copy_dat_file_with_fixed_format(
                        bom_file = file_collection[volume_key]['dat'], 
                        new_file = new_file, 
                        separator_str='|', 
                        remove_chars=[], 
                        new_separator=SEP,
                        rename_fields = rename_fields
                        )
                    if not check:
                        raise Exception
                    file_collection[volume_key]['mdat'] = new_file
        #validate input files, ie org chart
        file_path_csv = self.config['INPUT_DIR'] / 'org1.csv'
        orgchart_parser = OrgChartParser(file_path=file_path_csv)
        check = orgchart_parser.validate()
        return True
    
    def run(self):
        """Run the workflow of tasks.  Ensure `prepare_workspace()` results are
        in-place: directory structure, .mdat files, .mdat file links
        
        """
        self.config['LOGGER'].info('begin process')
        self.config['START_TIME'] = time.time()
        for task in self.tasks:
            task.run()
        self.config['LOGGER'].info(f"end process, execution took: {round(time.time() - self.config['START_TIME'], 3)}sec")
        return True

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
        


workflow_ecomms = WorkflowEcomms()