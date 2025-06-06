#!/usr/bin/env python3
"""
Test Task templates and TaskComponent children.

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.TaskExport import ExportToLocalTableTask, ExportToVdiWorkspaceTask
from src.TaskImport import ImportFromLocalFileTask,ImportBatchDocsFromLocalFileTask 
from src.TaskTransform import CreateSingleFileRecordTask
from src.TaskModel import ApplyTextModelsTask
from src.Files import Files
from src.io import load

import pandas as pd

from pathlib import Path
import tempfile
import json
import time

from config._constants import (
    logging_dir,
    logger
)

def prepare_workspace(wdir, schema_name='workspace_schema_v0.2.1.json'):
  """Prepare workspace with output schema and file paths"""
  #prepare schema
  filepath = Path('./tests/data/VDI_ApplicationStateData_v0.2.1.gz')
  if filepath.is_file():
    workspace_schema = load.get_schema_from_workspace(filepath)
  schema = wdir / schema_name
  with open(schema, 'w') as f:
    json.dump(workspace_schema, f)
  return schema




def test_multiple_files_ExportToLocalTableTask():
  #setup
  config = {
    'LOGGER': logger,
    'TRAINING_DATA_DIR': Path('./models_data/template/'),
    'START_TIME': time.time()
    }
  input_dir = Path(__file__).parent / 'data'
  input_files = Files(
    name='input',
    directory_or_list=input_dir,
    extension_patterns=['.yml']
    )
  with tempfile.TemporaryDirectory() as t_dir:
    t_dir = Path(t_dir)
    intermediate_dir = t_dir / 'intermediate'
    intermediate_files = Files(
       name='intermediate',
       directory_or_list=intermediate_dir,
       extension_patterns=['.pickle']
       )
    xform_dir = t_dir / 'xform'
    xform_files = Files(
      name='intermediate',
      directory_or_list=xform_dir,
      extension_patterns=['.pickle']
      )
    classified_dir = t_dir / 'classified'
    classified_files = Files(
       name='classified',
       directory_or_list=classified_dir,
       extension_patterns=['.pickle']
       )
    export_dir = t_dir / 'export'
    export_files = Files(
       name='export',
       directory_or_list=export_dir,
       extension_patterns=['.csv']
       )
    name_diff = ''
    #implement
    import_task = ImportBatchDocsFromLocalFileTask(
      config, 
      input_files, 
      intermediate_files
      )
    xform_task = CreateSingleFileRecordTask(
     config, 
     intermediate_files, 
     xform_files
     )
    model_task = ApplyTextModelsTask(
      config, 
      xform_files, 
      classified_files
      )
    export_task = ExportToLocalTableTask(
      config, 
      classified_files, 
      export_files
      )
    check = import_task.run()
    check = xform_task.run()
    check = model_task.run()
    check = export_task.run()
    
    export_file = [item for item in export_dir.glob('**/*') 
                   if item.is_file() if '.csv' in item.name
                   ]
    assert len(export_file) == 1
    assert export_file[0].stem == 'export-2'     #4records in 1 export file
    df = pd.read_csv(export_file[0])
    assert df.shape == (4,6)


def test_single_file_ExportToVdiWorkspaceTask():
  #setup
  config = {
    'LOGGER': logger,
    'TRAINING_DATA_DIR': Path('./models_data/template/'),
    'START_TIME': time.time()
    }
  input_dir = Path(__file__).parent / 'data'
  input_files = Files(
    name='input',
    directory_or_list=input_dir,
    extension_patterns=['.txt']
    )
  with tempfile.TemporaryDirectory() as t_dir:
    t_dir = Path(t_dir)
    schema_name='workspace_schema_v0.2.1.json'
    vdi_schema = prepare_workspace(t_dir, schema_name)
    intermediate_dir = t_dir / 'intermediate'
    intermediate_files = Files(
       name='intermediate',
       directory_or_list=intermediate_dir,
       extension_patterns=['.pickle']
       )
    xform_dir = t_dir / 'xform'
    xform_files = Files(
      name='intermediate',
      directory_or_list=xform_dir,
      extension_patterns=['.pickle']
      )
    classified_dir = t_dir / 'classified'
    classified_files = Files(
       name='classified',
       directory_or_list=classified_dir,
       extension_patterns=['.pickle']
       )
    export_dir = t_dir / 'export'
    export_files = Files(
       name='export',
       directory_or_list=export_dir,
       extension_patterns=['.gz']
       )
    name_diff = ''
    #implement
    import_task = ImportFromLocalFileTask(
      config, 
      input_files, 
      intermediate_files
      )
    xform_task = CreateSingleFileRecordTask(
     config, 
     intermediate_files, 
     xform_files
     )
    model_task = ApplyTextModelsTask(
      config, 
      xform_files, 
      classified_files
      )
    export_task = ExportToVdiWorkspaceTask(
      config, 
      classified_files, 
      export_files,
      vdi_schema
      )
    check = import_task.run()
    check = xform_task.run()
    check = model_task.run()
    check = export_task.run()

    #export_file = [item for item in export_dir.glob('**/*') if item.is_file()]
    export_file = [item for item in Path('./tests/test_task/data').glob('**/*.gz') if item.is_file()]
    assert len(export_file) == 1
    assert export_file[0].name == 'VDI_ApplicationStateData_vTEST.gz'


def test_multiple_files_ExportToVdiWorkspaceTask():
  #setup
  config = {
    'LOGGER': logger,
    'TRAINING_DATA_DIR': Path('./models_data/template/'),
    'START_TIME': time.time()
    }
  input_dir = Path(__file__).parent / 'data'
  input_files = Files(
    name='input',
    directory_or_list=input_dir,
    extension_patterns=['.yml']
    )
  with tempfile.TemporaryDirectory() as t_dir:
    t_dir = Path(t_dir)
    schema_name='workspace_schema_v0.2.1.json'
    vdi_schema = prepare_workspace(t_dir, schema_name)
    intermediate_dir = t_dir / 'intermediate'
    intermediate_files = Files(
       name='intermediate',
       directory_or_list=intermediate_dir,
       extension_patterns=['.pickle']
       )
    xform_dir = t_dir / 'xform'
    xform_files = Files(
      name='intermediate',
      directory_or_list=xform_dir,
      extension_patterns=['.pickle']
      )
    classified_dir = t_dir / 'classified'
    classified_files = Files(
       name='classified',
       directory_or_list=classified_dir,
       extension_patterns=['.pickle']
       )
    export_dir = t_dir / 'export'
    export_files = Files(
       name='export',
       directory_or_list=export_dir,
       extension_patterns=['.gz']
       )
    name_diff = ''
    #implement
    import_task = ImportBatchDocsFromLocalFileTask(
      config, 
      input_files, 
      intermediate_files
      )
    xform_task = CreateSingleFileRecordTask(
     config, 
     intermediate_files, 
     xform_files
     )
    model_task = ApplyTextModelsTask(
      config, 
      xform_files, 
      classified_files
      )
    export_task = ExportToVdiWorkspaceTask(
      config, 
      classified_files, 
      export_files,
      vdi_schema = vdi_schema
      )
    check = import_task.run()
    check = xform_task.run()
    check = model_task.run()
    check = export_task.run()

    #export_file = [item for item in export_dir.glob('**/*') if item.is_file()]
    export_file = [item for item in Path('./tests/test_task/data').glob('**/*.gz') if item.is_file()]
    assert len(export_file) == 1
    assert export_file[0].name == 'VDI_ApplicationStateData_vTEST.gz'
    """
    TODO:
    note: prepare with the following:
    ~~~$ cp /tmp/tmp7o6zyvd2/export/VDI_ApplicationStateData_vTEST.gz tests/test_task/data


    * ~~classification results
      - ~~add some hits
    * doc id
    * title
    * combine doc bodies into multiple pdf pages
    """