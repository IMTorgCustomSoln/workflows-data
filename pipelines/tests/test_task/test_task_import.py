#!/usr/bin/env python3
"""
Test Task templates and TaskComponent children.

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.TaskImport import ImportFromLocalFileTask, ImportBatchDocsFromLocalFileTask
from src.Files import Files
from src.Task import PipelineRecord

from pathlib import Path
import tempfile
import pickle

from config._constants import (
    logging_dir,
    logger
)


def test_single_file_ImportFromLocalFileTask():
  #setup
  config = {
    'LOGGER': logger
    }
  input_dir = Path(__file__).parent / 'data'
  input_files = Files(
    name='input',
    directory_or_list=input_dir,
    extension_patterns=['.txt']
    )
  with tempfile.TemporaryDirectory() as t_dir:
   output_files = Files(
      name='output',
      directory_or_list=t_dir,
      extension_patterns=['.pickle']
      )
   name_diff = ''
   #implement
   tmp_task = ImportFromLocalFileTask(
     config, 
     input_files, 
     output_files
     )
   check = tmp_task.run()
   files1 = list(input_files.get_files())
   files2 = [item for item in Path(t_dir).glob('**/*') if item.is_file()]
   assert len(files1) == len(files2) == 4
   with open(files2[0], "rb") as pipeline_record_file:
    pipeline_record = pickle.load(pipeline_record_file)
  assert type(pipeline_record) == PipelineRecord


def test_multiple_files_ImportBatchDocsFromLocalFileTask():
  #setup
  config = {
    'LOGGER': logger
    }
  input_dir = Path(__file__).parent / 'data'
  input_files = Files(
    name='input',
    directory_or_list=input_dir,
    extension_patterns=['.yml']
    )
  with tempfile.TemporaryDirectory() as t_dir:
   output_files = Files(
      name='output',
      directory_or_list=t_dir,
      extension_patterns=['.pickle']
      )
   name_diff = ''
   #implement
   tmp_task = ImportBatchDocsFromLocalFileTask(
     config, 
     input_files, 
     output_files
     )
   check = tmp_task.run()
   files1 = list(input_files.get_files())
   files2 = [item for item in Path(t_dir).glob('**/*') if item.is_file()]
   assert len(files1) == len(files2) == 2
   with open(files2[0], "rb") as pipeline_record_file:
    pipeline_record = pickle.load(pipeline_record_file)
  assert type(pipeline_record) == PipelineRecord